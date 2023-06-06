import copy
import json
import re
import traceback

from fate_flow.controller.job_controller import JobController
from fate_flow.db.db_models import Job
from fate_flow.utils import cron
from fate_flow.utils.log_utils import detect_logger
from fate_flow.web_server.utils.enums import JobStatusEnum
from fate_flow.web_server.db_service.project_service import ProjectCanvasService
from fate_flow.web_server.pipeline_wrapper.canvas_jobs import data_transform, component_run, exception_interpret, \
    update_project_canvas4hosts
from fate_flow.scheduler.federated_scheduler import FederatedScheduler
from fate_flow.web_server.db_service.job_service import JobContentService
from fate_flow.web_server.fl_config import config


def be_graph(cells):
    graph = {}
    edge = {}
    for c in cells:
        if c["shape"] == "dag-edge":
            f, t = c["source"]["cell"], c["target"]["cell"]
            if f not in edge: edge[f] = []
            edge[f].append(t)
            continue
        if isinstance(c.get("data", {}).get("parameter", {}), str):
            try:
                c["data"]["parameter"] = json.loads(c["data"]["parameter"])
            except Exception as e:
                c["data"]["parameter"] = {}
                detect_logger().error("Can't load parameter Json: ", c["data"]["parameter"])
        graph[c["id"]] = c

    for f, ts in edge.items():
        graph[f]["to"] = ts
        for t in ts:
            if not graph[t].get("from"): graph[t]["from"] = []
            graph[t]["from"].append(f)

    tgs = set([t for f, ts in edge.items() for t in ts])
    graph["root"] = list(set([k for k in graph.keys()]) - tgs)
    return graph


def be_flat(cnvs, graph):
    res = []
    for c in cnvs:
        if isinstance(c.get("data", {}).get("parameter", ""), dict):
            c["data"]["parameter"] = json.dumps(c["data"]["parameter"], ensure_ascii=False)
        res.append(c)
        if c["id"] not in graph: continue
        if "to" in graph[c["id"]]: del graph[c["id"]]["to"]
        if "from" in graph[c["id"]]: del graph[c["id"]]["from"]
        res[-1] = graph[c["id"]]
    return res


def stop_job(jid):
    jobs = Job.query(job_id=jid)
    if not jobs: return False

    kill_status, kill_details = JobController.stop_jobs(job_id=jid, stop_status=JobStatusEnum.CANCELED.value)
    detect_logger().info(f"stop job {jid} on this party status {kill_status}")
    detect_logger().info(f"request stop job {jid} to canceled")
    j = jobs[0]
    FederatedScheduler.request_stop_job(job=j, stop_status=JobStatusEnum.CANCELED.value, command_body=j.to_dict())
    return True


def submit_jobs():
    objs = ProjectCanvasService.query(cols=[ProjectCanvasService.model.id.alias("canvas_id"),
                                            ProjectCanvasService.model.project_id,
                                            ProjectCanvasService.model.canvas_content,
                                            ProjectCanvasService.model.status,
                                            ProjectCanvasService.model.updator],
                                      filters=[ProjectCanvasService.model.status.in_(["run", "stop", "step"])]).dicts()
    if not objs: return

    detect_logger().info(f"find {len(objs)} jobs to do.")

    def state(cnvs, nid):
        return cnvs[nid]["data"].get("nodeState", "")

    def set_state(cnvs, nid, st):
        cnvs[nid]["data"]["nodeState"] = st

    def set_error(cnvs, nid, er):
        cnvs[nid]["data"]["error"] = exception_interpret(er)

    c = 0
    for ii, cnvs in enumerate(objs):
        proj_id = cnvs["project_id"]
        cid = cnvs["canvas_id"]
        usr = cnvs["updator"]
        ocnvs = cnvs["canvas_content"]
        cmd = cnvs["status"]
        cnvs = be_graph(cnvs["canvas_content"])
        ids = []

        def dfs(nid, last_nid=''):
            nonlocal ids, cnvs
            if not nid: return
            if cnvs[nid]["data"].get("nodeState", "") not in ["run", JobStatusEnum.RUNNING.value,
                                                              JobStatusEnum.WAITING.value]:
                for n in cnvs[nid].get("to", []): dfs(n, nid)
                return
            ids.append((nid, last_nid))

        for n in cnvs["root"]: dfs(n)

        if not ids:
            # nothing is running
            if cmd == "stop":
                c += ProjectCanvasService.update_by_id(cid, {"status": "canceled"})
            else:
                detect_logger().error(f"Nothing to run for canvas {cid}")
            continue

        ids_dic = {}
        for (nid, last_nid) in ids:
            if nid not in ids_dic: ids_dic[nid] = []
            ids_dic[nid].append(last_nid)
        ids = [(k, ",".join(arr)) for k, arr in ids_dic.items()]

        if cmd == "stop":
            for nid, lnid in ids:
                if state(cnvs, nid) in [JobStatusEnum.RUNNING.value, JobStatusEnum.WAITING.value]:
                    # stop jobs
                    jid = cnvs[nid]["data"].get("job_id")
                    assert jid
                    detect_logger().info(f"[{cid}] stopping job: {jid}")
                    if stop_job(jid):
                        set_state(cnvs, nid, JobStatusEnum.CANCELED.value)
                if state(cnvs, nid) == "run":
                    jid = cnvs[nid]["data"].get("job_id")
                    if jid:
                        detect_logger().info(f"[{cid}] stopping job: {jid}")
                        if stop_job(jid):
                            set_state(cnvs, nid, JobStatusEnum.CANCELED.value)

                    set_state(cnvs, nid, JobStatusEnum.CANCELED.value)

                c += ProjectCanvasService.update_by_id(cid,
                                                       {"canvas_content": be_flat(ocnvs, cnvs),
                                                        "status": JobStatusEnum.CANCELED.value})
                update_project_canvas4hosts(cid, be_flat(ocnvs, cnvs))

            continue

        sts = []
        for nid, lnid in ids:
            if state(cnvs, nid) == JobStatusEnum.RUNNING.value:
                # update the running job progresses, status
                jid = cnvs[nid]["data"].get("job_id")
                assert jid
                jobs = Job.query(job_id=jid)
                if not jobs:
                    detect_logger().error(f"[{cid}] Can't find job {jid} {cnvs[nid]}")
                    continue

                prcs = 0
                for j in jobs: prcs += j.f_progress
                cnvs[nid]["data"]["progress"] = prcs * 1. / len(jobs)
                if any([j.f_status in [JobStatusEnum.FAILED.value, JobStatusEnum.TIMEOUT.value,
                                       JobStatusEnum.CANCELED.value] for j in jobs]):
                    set_state(cnvs, nid, JobStatusEnum.FAILED.value)
                    sts.append(JobStatusEnum.FAILED.value)
                    # c += ProjectCanvasService.update_by_id(cid,
                    #                                       {"canvas_content": be_flat(ocnvs, cnvs),
                    #                                        "status": JobStatusEnum.FAILED.value})
                    detect_logger().warn(f"[{cid}] Job: {jid} fail -----------------")
                    # return c
                    continue

                if all([j.f_status == JobStatusEnum.SUCCESS.value for j in jobs]):
                    set_state(cnvs, nid, JobStatusEnum.SUCCESS.value)
                    # start to run son-nodes in next iteration
                    if cmd == "run":
                        for t in cnvs[nid].get("to", []):
                            set_state(cnvs, t, "run")
                            sts.append(JobStatusEnum.RUNNING.value)
                    if not cnvs[nid].get("to") or cmd == "step":
                        sts.append(JobStatusEnum.SUCCESS.value)
                        # cmd = JobStatusEnum.SUCCESS.value
                else:
                    assert prcs / len(jobs) < 100, f"[{cid}] {jid} abnormal status!"
                    sts.append(JobStatusEnum.RUNNING.value)

            elif any([state(cnvs, n) != JobStatusEnum.SUCCESS.value for n in cnvs[nid].get("from", [])]):
                if not state(cnvs, n) or any([state(cnvs, n) in [JobStatusEnum.CANCELED.value, JobStatusEnum.FAILED.value,
                                           JobStatusEnum.TIMEOUT.value] for n in cnvs[nid].get("from", [])]):
                    detect_logger().error(f"[{cid}] Any of upstream task didn't go well")
                    set_state(cnvs, nid, JobStatusEnum.FAILED.value)
                    set_error(cnvs, nid, "Sorry, 请先成功运行上游组件！")
                    cnvs[nid]["data"]["progress"] = 0
                    sts.append(JobStatusEnum.FAILED.value)
                    cnvs[nid]["data"]['job_id'] = ""
                    if "model_info" in cnvs[nid]["data"]: del cnvs[nid]["data"]['model_info']
                # if the upstream task is not done yet
            elif re.sub(r"_.*", "", cnvs[nid]["data"]["nodeName"]) == "DataTransform":
                assert not lnid, f"{cnvs}"
                if not cnvs[nid]["data"]["parameter"]: raise Exception("Sorry！请配置参数！")
                cnvs[nid]["data"]["parameter"]["canvas_id"] = cid
                cnvs[nid]["data"]["parameter"]["project_id"] = proj_id
                try:
                    r = data_transform(cnvs[nid]["data"]["parameter"], usr)
                    set_state(cnvs, nid, JobStatusEnum.RUNNING.value)
                    cnvs[nid]["data"]["progress"] = 0
                    set_error(cnvs, nid, "")
                    sts.append(JobStatusEnum.RUNNING.value)
                    for k, v in r.items(): cnvs[nid]["data"][k] = v
                    detect_logger().info(f"[{cid}] submit a job {r['job_id']}")
                except Exception as e:
                    detect_logger().error(f"[{cid}] DataTransform: " + traceback.format_exc())
                    set_state(cnvs, nid, JobStatusEnum.FAILED.value)
                    set_error(cnvs, nid, str(e))
                    cnvs[nid]["data"]["progress"] = 0
                    cnvs[nid]["data"]['job_id'] = ""
                    if "model_info" in cnvs[nid]["data"]: del cnvs[nid]["data"]['model_info']
                    sts.append(JobStatusEnum.FAILED.value)
                    # cmd = JobStatusEnum.FAILED.value
                    # break
            elif re.sub(r"_.*", "", cnvs[nid]["data"]["nodeName"]) == "Reader":
                set_state(cnvs, nid, JobStatusEnum.SUCCESS.value)
                cnvs[nid]["data"]["progress"] = 100
                jid = cnvs[nid]["data"]["parameter"].get("job_id", [0])[0]
                lst_jb = JobContentService.get_or_none(job_id=jid)
                if not jid or not lst_jb:
                    detect_logger().error(f"[{cid}] Reader: No jobid??")
                    set_state(cnvs, nid, JobStatusEnum.FAILED.value)
                    set_error(cnvs, nid, "Sorry！提交任务失败，未指定保存的样本，或找不到其关联任务！")
                    cnvs[nid]["data"]["progress"] = 0
                    cnvs[nid]["data"]['job_id'] = ""
                    sts.append(JobStatusEnum.FAILED.value)
                    continue
                cnvs[nid]["data"]["job_id"] = jid
                cnvs[nid]["data"]["model_info"] = {"model_version": jid}
                cnvs[nid]["data"]["hosts"] = [h["party_id"] for h in lst_jb.party_info.get("host", [])]
                cnvs[nid]["data"]["guest"] = config.local_party_id
                sts.append(JobStatusEnum.SUCCESS.value)
                detect_logger().info(f"[{cid}] reader a job {jid}")
            else:
                try:
                    if not cnvs[nid]["data"]["parameter"]: raise Exception("Sorry！请配置参数！")
                    assert lnid, f"Sorry！任务提交失败！该组件运行依赖上游组件的输出，请正确连接并成功运行上游组件。"
                    lnid = list(set(lnid.split(",")))
                    linfo = cnvs[lnid[0]]["data"]
                    assert linfo.get("job_id"), f"Sorry！任务提交失败！该组件运行依赖上游组件的输出，请正确连接并成功运行上游组件。"
                    r = component_run({
                        "canvas_id": cid,
                        "project_id": proj_id,
                        "last_job_id": linfo["job_id"] if len(lnid) < 2 else ",".join(
                            [cnvs[i]["data"]["job_id"] for i in lnid]),
                        "last_component_name": linfo.get("component_name", "outs"),
                        "last_module_name": linfo["nodeName"] if len(lnid) < 2 else ",".join(
                            [cnvs[i]["data"]["nodeName"] for i in lnid]),
                        "hosts": linfo.get("hosts"),
                        "parameters": copy.deepcopy(cnvs[nid]["data"]["parameter"]),
                        "exclude": cnvs[nid]["data"]["parameter"].get("exclude", []),
                        "module": cnvs[nid]["data"]["nodeName"]},
                        usr
                    )
                    set_state(cnvs, nid, JobStatusEnum.RUNNING.value)
                    set_error(cnvs, nid, "")
                    sts.append(JobStatusEnum.RUNNING.value)
                    cnvs[nid]["data"]["progress"] = 0
                    for k, v in r.items(): cnvs[nid]["data"][k] = v
                    detect_logger().info(f"[{cid}] submit a job {r['job_id']}")
                except Exception as e:
                    detect_logger().error(f"[{cid}] component_run: " + traceback.format_exc())
                    set_state(cnvs, nid, JobStatusEnum.FAILED.value)
                    set_error(cnvs, nid, str(e))
                    cnvs[nid]["data"]["progress"] = 0
                    sts.append(JobStatusEnum.FAILED.value)
                    cnvs[nid]["data"]['job_id'] = ""
                    if "model_info" in cnvs[nid]["data"]: del cnvs[nid]["data"]['model_info']
                    # cmd = JobStatusEnum.FAILED.value
                    # break

        if all([c == JobStatusEnum.SUCCESS.value for c in sts]):
            cmd = JobStatusEnum.SUCCESS.value
        elif all([c == JobStatusEnum.FAILED.value for c in sts]):
            cmd = JobStatusEnum.FAILED.value

        c += ProjectCanvasService.update_by_id(cid, {"canvas_content": be_flat(ocnvs, cnvs), "status": cmd})
        update_project_canvas4hosts(cid, be_flat(ocnvs, cnvs))

    return c


class PipelineWraperDetector(cron.Cron):
    def run_do(self):
        submit_jobs()


if __name__ == "__main__":
    import time

    while True:
        submit_jobs()
        time.sleep(1)