import copy

from fate_flow.controller.job_controller import JobController
from fate_flow.db.db_models import Job
from fate_flow.scheduler.federated_scheduler import FederatedScheduler
from fate_flow.utils.log_utils import schedule_logger
from fate_flow.web_server.db_service.project_service import ProjectCanvasService, ProjectInfoService, \
    ProjectUsedSampleService, ProjectPartyService
from fate_flow.web_server.utils.reponse_util import get_json_result
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.db_service.sample_service import SampleService, SampleAuthorizeService, SampleFieldsService
from fate_flow.web_server.db_service.job_service import JobContentService
from fate_flow.web_server.fl_config import config
from fate_flow.settings import stat_logger, ENGINES
from fate_flow.web_server.pipeline_wrapper import pickname
import json, re

from fate_flow.web_server.pipeline_wrapper import WrapperFactory
from fate_flow.utils.api_utils import get_data_error_result, federated_api
from fate_flow.web_server.db_service.model_service import ModelInfoExtendService, ProjectUsedModelService
from fate_flow.web_server.utils.enums import JobStatusEnum, MixTypeChineseEnum, SampleTypeEnum
from fate_flow.web_server.data import statistics
from fate_flow.utils.job_utils import generate_job_id

def rm_excluded_params(request):
    if request.get("exclude"):
        for e in request["exclude"]:
            if len(e.split(".")) == 2:
                e = e.split(".")
                if request["parameters"].get(e[0], {}).get(e[1]):
                    del request["parameters"][e[0]][e[1]]
                continue

            if len(e.split(".")) == 3:
                e = e.split(".")
                if request["parameters"].get(e[0], {}).get(e[1], {}).get(e[2]):
                    del request["parameters"][e[0]][e[1]][e[2]]
                continue

            if e not in request["parameters"]: continue
            request["parameters"][e] = {}
    if "exclude" in request["parameters"]: del request["parameters"]["exclude"]
    return request

def data_transform(request, usr):
    request = copy.deepcopy(request)
    def get_str_feats(smpid):
        feature_cols = [SampleFieldsService.model.field_name, SampleFieldsService.model.distribution_type,
                        SampleFieldsService.model.field_type]
        clmns = list(SampleFieldsService.query(sample_id=smpid, cols=feature_cols).dicts())
        return [c["field_name"] for c in clmns if c["distribution_type"] == "离散型" and c["field_type"].find("int") < 0]

    cid = request.get("canvas_id")
    jt = ""
    if cid:
        cvs = ProjectCanvasService.get_or_none(id=cid)
        jt = cvs.job_type

    if request.get("exclude"):
        request = rm_excluded_params({"exclude": request["exclude"], "parameters": request})

    gst = copy.deepcopy(request["guest_only_param"])
    if gst.get("sample_ids") is None: raise ValueError("Sorry, 请选择本方样本数据！")
    gst_dt_param = {k: v for k, v in gst.items() if k != "sample_ids" and v}
    if jt != "隐匿查询" and gst_dt_param.get("with_label") and not gst_dt_param.get("label_name"):
        raise ValueError(f"Sorry！参数配置有误！请指定Label Name！")
    if not gst_dt_param.get("label_name"): gst_dt_param["with_label"] = False  # this is for SIR
    # for string type feature
    str_feats = get_str_feats(gst["sample_ids"][0]) if gst["sample_ids"] else []
    if str_feats: gst_dt_param["exclusive_data_type"] = {k: "str" for k in str_feats}

    party_info = {"guest": {"party_id": config.local_party_id,
                            "sample_id": gst["sample_ids"][0] if gst["sample_ids"] else "",
                            "label_name": gst_dt_param.get("label_name")}}
    # for guest party information
    gst["sample"] = SampleService.sample_names(gst["sample_ids"])
    if gst["sample_ids"] and (not gst["sample"] or len(gst["sample"]) != len(gst["sample_ids"])): raise ValueError(
        "Sorry, 无法查到本方样本！")
    gst["sample"] = [{"name": smp["name"], "namespace": config.namespace} for smp in gst["sample"]] if gst[
        "sample"] else []
    party_info["guest"]["sample_name"] = gst["sample"][0]["name"]

    # for hosts party info
    hosts = copy.deepcopy(request.get("host_only_param", {}))
    if hosts: party_info["host"] = []
    host_dt_param = {}
    for h, cnf in hosts.items():
        if not cnf["sample_ids"]: raise ValueError("Sorry！请选择合作方样本！")
        dt_param = {k: v for k, v in cnf.items() if k != "sample_ids" and v is not None}
        cnf["sample_id"] = cnf["sample_ids"][0]
        if re.match(r"[^0-9]", str(h)): h = re.sub(r"[^0-9]", "", str(h))
        host_dt_param[h] = dt_param

        cnf["sample"] = SampleService.sample_names(cnf["sample_id"])
        if not cnf["sample"]: raise ValueError(f"Sorry, 无法查到合作方本方样本！{h}: {cnf['sample_id']}")
        cnf["sample"] = {"name": cnf["sample"][0]["name"], "namespace": config.namespace}
        party_info["host"].append({"sample_id": cnf["sample_id"],
                                   "sample_name": cnf["sample"]["name"],
                                   "label_name": dt_param.get("label_name"),
                                   "party_id": h})
        # for string type feature
        str_feats = get_str_feats(cnf["sample_id"])
        if str_feats: cnf["exclusive_data_type"] = {k: "str" for k in str_feats}
        if cnf.get("with_label") and not cnf.get("label_name"):
            raise ValueError(f"Sorry！参数配置有误！请指定Label Name！")

        del cnf["sample_id"]

    from fate_flow.web_server.pipeline_wrapper import DataTransformWrapper
    pip = DataTransformWrapper(role="guest", pid=config.local_party_id, guest=config.local_party_id,
                               hosts=[re.sub(r"[^0-9]", "", str(h)) for h in hosts.keys()])
    pip.setReader(gst["sample"],
                  {re.sub(r"[^0-9]", "", str(h)): cnf["sample"] for h, cnf in hosts.items() if cnf.get("sample")})

    jid, mdl_info = pip.exe(guest_only_param=gst_dt_param,
                            host_only_param=host_dt_param)

    # store job info
    try:
        jbnm = pickname()
        create_job_conf(cid=cid, job_content={"module": "DataTransform"},
                        user_name=usr, job_id=jid,
                        run_param=json.dumps(request),
                        job_name=jbnm,
                        module_name="DataTransform_0",
                        party_info=party_info,
                        proj_id=request["project_id"])

        # 通知host 方存储datasource信息
        notify_host_job_end(jid, party_info, cid,
                            job_detail={"job_content": {"module": "DataTransform"},
                                        "user_name": usr,
                                        "run_param": json.dumps(request),
                                        "job_name": jbnm,
                                        "party_info": party_info,
                                        "module_name": "DataTransform_0"
                                        }
                            )

    except Exception as e:
        if jid: component_stop(jid)
        raise e

    # store the target and label info for a canvas task
    from fate_flow.web_server.data import get_data_by_name
    df = get_data_by_name(gst["sample"][0]["name"], limit=1000)
    if df is not None:
        df, cnt = df
        c = gst_dt_param.get("label_name", "")
        for i in df.columns:
            if i.lower() == c.lower():
                c = i
                break
        if c in df.columns:
            tgt_info = {"label_name": c}
            vc = df[c].value_counts(normalize=True).to_dict()
            rt = len(vc.keys()) * 1. / len(df)
            if len(vc.keys()) == 2:
                tgt_info["target"] = "binary"
            elif rt < 0.1:
                tgt_info["target"] = "multi"
            else:
                tgt_info["target"] = "regression"

            if tgt_info["target"] in set(["binary", "multi"]): tgt_info["labels"] = vc
            try:
                ProjectCanvasService.update_by_id(request["canvas_id"], {"target_content": tgt_info})
            except Exception as e:
                stat_logger.error(f"Update canvas's target_content: '{e}'")
    else:
        stat_logger.warn(f"Can't get sample data by name: '{gst['sample'][0]['name']}'")

    return {
        "job_id": jid,
        "component_name": "outs",
        "model_info": mdl_info,
        "guest": config.local_party_id,
        "hosts": [int(re.sub(r"[^0-9]", "", str(h))) for h in hosts.keys()]
    }


def component_run(request, usr):
    req_param = copy.deepcopy(request["parameters"])
    request = rm_excluded_params(request)

    cpn_init = {
        "jid4reader": request["last_job_id"],
        "cpn4reader": request["last_component_name"],
        "pid": config.local_party_id,
        "guest": config.local_party_id,
        "hosts": request.get("hosts"),
        "arbiter": request.get("hosts")[0] if request.get("hosts") and len(request.get("hosts")) > 0 else None,
    }
    lst_jb = JobContentService.get_or_none(job_id=request["last_job_id"].split(",")[0])
    if not lst_jb: raise ValueError("Sorry, 上游任务不存在！")

    mdl_name = request["module"]

    if re.search(r"(SIR|Predict|LinR|LR|HeteroNN|HomoNN|light|boost|means|poisson)", mdl_name, flags=re.IGNORECASE):
        agree, inf = check_sample_auth(lst_jb.party_info, mdl_name)
        if not agree: raise ValueError(f"Sorry！{inf} 请联系合作方加宽样本的模型使用范围或时间。")

    cid = request["canvas_id"]
    proj_id = request["project_id"]

    if mdl_name.find("Predict") == 0:
        mdlnm = request["parameters"].get("model_name")
        minfo = ModelInfoExtendService.query(name=mdlnm).get()
        if not minfo: raise ValueError(f"模型名称 {mdlnm} 找不到")
        request["parameters"] = json.loads(minfo.job_content)
        del cpn_init["arbiter"]

    if mdl_name.find("Evaluation") == 0 or mdl_name.find("PositiveUnlabeled") == 0:
        del cpn_init["jid4reader"]
        del cpn_init["cpn4reader"]

    if re.match(r".*(LR|LinR)", mdl_name) and request["parameters"].get("reveal_strategy"):
        mdl_name = re.sub(r"(Hetero|Homo)(LinR|LR)", r"\1SSHE\2", mdl_name)
        for k in ["floating_point_precision", "early_stopping_rounds", "metrics", "masked_rate", "shuffle", "sqn_param",
                  "stepwise_param"]:
            if k in request["parameters"]: del request["parameters"][k]
    if len(cpn_init["hosts"]) > 0 and re.search(r"(LinR|LR|poisson)", mdl_name, flags=re.IGNORECASE):
        if "early_stop" in request["parameters"]: request["parameters"]["early_stop"] = "weight_diff"

    if mdl_name.find("SIR") == 0:
        if len(request["parameters"]["target_cols"])==0 or request["parameters"]["target_ids"]=='' or request["parameters"]["target_ids"] is None:
            raise ValueError("Sorry! ID或特征都不能为空")
        request["parameters"]["target_ids"] = [a for a in re.split(r"[:;，,、\t\n\r]+", request["parameters"].get("target_ids", "")) if a]

    elif re.match(r".*(Hetero|Homo)(LR|LinR)", mdl_name):
        if "reveal_strategy" in request["parameters"]: del request["parameters"]["reveal_strategy"]
        if "reveal_every_iter" in request["parameters"]: del request["parameters"]["reveal_every_iter"]

    if mdl_name.find("HeteroFeatureBin") == 0:
        def split_points(spp):
            for k in list(spp.keys()):
                if not spp[k]: del spp[k]
            for k in spp.keys():
                spp[k] = [float(d) for d in re.split(r"[,，、；; ]", spp[k])]

        spp = request["parameters"].get("guest_only_param", {}).get("manually_param", {}).get(
            "split_points_by_col_name")
        if spp:
            split_points(spp)
            request["parameters"]["guest_only_param"]["split_points_by_col_name"] = spp
            if not request["parameters"]["guest_only_param"].get("bin_names"):
                request["parameters"]["guest_only_param"]["bin_names"] = []
            for k in spp.keys():
                if k not in request["parameters"]["guest_only_param"]["bin_names"]:
                    request["parameters"]["guest_only_param"]["bin_names"].append(k)
        if request["parameters"].get("guest_only_param", {}).get("manually_param", {}):
            request["parameters"]["guest_only_param"].pop("manually_param")
        for k, par in request["parameters"]["host_only_param"].items():
            spp = par.get("manually_param", {}).get("split_points_by_col_name")
            if spp:
                split_points(spp)
                request["parameters"]["host_only_param"][k]["split_points_by_col_name"] = spp
                if not request["parameters"]["host_only_param"][k].get("bin_names"):
                    request["parameters"]["host_only_param"][k]["bin_names"] = []
                for s in spp.keys():
                    if s not in request["parameters"]["host_only_param"][k]["bin_names"]:
                        request["parameters"]["host_only_param"][k]["bin_names"].append(s)
            del request["parameters"]["host_only_param"][k]["manually_param"]

    if mdl_name.find("HeteroNN") == 0:
        request["parameters"]["guest_bottom_nn"] = request["parameters"]["bottom_nn_define"]["bottom_nn_define"][
            "guest_bottom_nn"]
        request["parameters"]["host_bottom_nn"] = request["parameters"]["bottom_nn_define"]["bottom_nn_define"][
            "host_bottom_nn"]
        request["parameters"]["top_nn_param"] = request["parameters"]["top_nn_param"]["top_nn_param"]
        request["parameters"]["interactive_layer_lr"] = request["parameters"]["interactive_layer_param"].pop(
            "interactive_layer_lr")
        del request["parameters"]["bottom_nn_define"]

    if mdl_name.find("SampleWeight") == 0:
        lblw = request["parameters"].pop("label_weight")
        if request["parameters"]["class_weight"] == 'stratified':
            request["parameters"]["class_weight"] = lblw
            request["parameters"]["class_weight"] = {l: p for l, p in request["parameters"]["class_weight"]}
        else:
            request["parameters"]["host_only_param"] = {h: {"need_run": False} for h in cpn_init["hosts"]}

    if mdl_name.find("FeatureSele") > 0:
        hasFeat = False
        for h, v in request["parameters"]["host_only_param"].items():
            if v.get("select_names"):
                hasFeat = True
                break
        if "correlation_filter" in request["parameters"]["guest_only_param"]["filter_methods"]:
            if hasFeat and not request["parameters"]["guest_only_param"]["correlation_param"].get("select_federated"):
                raise ValueError("Sorry！任务提交失败！相关性过滤中存在合作方特征，应将“Federated”激活！")
            if not hasFeat and request["parameters"]["guest_only_param"]["correlation_param"].get("select_federated"):
                raise ValueError("Sorry！任务提交失败！相关性过滤中“Federated”已激活，但未选择任何合作方特征！")
        if not hasFeat and not request["parameters"]["guest_only_param"].get("select_names"):
            raise ValueError("Sorry！任务提交失败！请选择需要计算的特征！")

    if mdl_name.find("SIR") == 0:
        hst_param = copy.deepcopy(request["parameters"])
        hst_param["target_ids"]=['======']
        request["parameters"] = {"guest_only_param": request["parameters"],
                                 "host_only_param": {h.get("party_id",10000): hst_param for h in lst_jb.party_info.get("host", [])}
                                 }


    gst_p, hst_p = None, None
    if "guest_only_param" in request["parameters"]:
        gst_p = request["parameters"].pop("guest_only_param")
    if "host_only_param" in request["parameters"]:
        hst_p_ = request["parameters"].pop("host_only_param")
        hst_p = {}
        if not hst_p_: hst_p_ = {}
        for k, v in hst_p_.items(): hst_p[re.sub(r"[^0-9]+", "", str(k))] = v

    cpn_init["cmp_nm"] = mdl_name
    if hst_p and len(hst_p.keys()) > 0: cpn_init["hosts"] = [int(h) for h in hst_p.keys()]
    pip = WrapperFactory(mdl_name)(**cpn_init)

    if mdl_name.find("Evaluation") == 0 or mdl_name.find("PositiveUnlabeled") == 0:
        gpid = lst_jb.party_info.get("guest", {}).get("party_id", "")
        hst_smpl = []
        for h in lst_jb.party_info.get("host", []):
            if h.get("party_id") == gpid or not h.get("sample_name"): continue
            hst_smpl = [h["party_id"], h["sample_name"]]
            break
        if not hst_smpl or not hst_smpl[1]: raise ValueError("Sorry！未找到上游有关合作方的样本信息，请成功执行数据源并保证合作方持有对应样本。")

        pip.setReader(request["last_job_id"].split(","),
                      request["last_component_name"].split(","),
                      request["last_module_name"].split(","),
                      hst_smpl
                      )
    else:
        pip.setReader()

    stat_logger.info(f"{mdl_name}: param:" + json.dumps(request["parameters"]) + " guest: " + json.dumps(
        gst_p) + " host:" + json.dumps(hst_p))
    jid, mdl_info = pip.exe(request["parameters"],
                            guest_only_param=gst_p,
                            host_only_param=hst_p
                            )
    jbnm = pickname()
    try:
        create_job_conf(cid=cid, job_content=request, user_name=usr, job_id=jid, run_param=json.dumps(req_param),
                        job_name=jbnm, module_name=mdl_name,
                        last_job_id=request['last_job_id'].split(',')[0],
                        party_info=lst_jb.party_info,
                        proj_id=proj_id)
    except Exception as e:
        if jid: component_stop(jid)
        raise e

    error_info = notify_host_job_end(jid, lst_jb.party_info, cid,
                        job_detail={"job_content": request,
                                    "user_name": usr,
                                    "run_param": json.dumps(req_param),
                                    "job_name": jbnm,
                                    "party_info": lst_jb.party_info,
                                    "last_job_id": request['last_job_id'].split(',')[0],
                                    "module_name": mdl_name
                                    }
                        )

    return {
        "job_id": jid,
        "component_name": "outs",
        "hosts": request.get("hosts"),
        "model_info": mdl_info,
        "error_info": error_info,
        "guest": config.local_party_id,
    }


def create_job_conf(cid=None, job_content=None, user_name=None, job_id=None, run_param=None, job_name=None,
                    module_name=None, last_job_id=None, party_info=None, proj_id=None):
    JobContentService.create_conf(cid, None,
                                  job_content=job_content["module"],
                                  user_name=user_name, job_id=job_id,
                                  run_param=run_param,
                                  job_name=job_name,
                                  module_name=module_name,
                                  last_job_id=last_job_id,
                                  party_info=party_info
                                  )
    if re.match(r"(Reader|Predict|DataTransform)", module_name):
        ProjectUsedSampleService.insert_by_party_info(proj_id, cid, job_id, party_info,
                                                      SampleTypeEnum.ORIGIN.value if module_name.find("DataTransform")>=0 else SampleTypeEnum.FUSION.value,
                                                      user_name)
        if module_name.find("Predict") >= 0:
            ProjectUsedModelService.create_by_info(proj_id, job_id, MixTypeChineseEnum.predict.value,
                                                   job_content["parameters"]["model_id"],
                                                   job_content["parameters"]["model_versions"][-1][0],
                                                   cid, user_name)
        SampleAuthorizeService.auth_add_count(party_info)


def component_stop(jid):
    jobs = Job.query(job_id=jid)
    if not jobs: return False
    prcs = 0
    for j in jobs: prcs += j.f_progress
    prcs /= len(jobs) * 1.

    if prcs >= 100: return False

    kill_status, kill_details = JobController.stop_jobs(job_id=jid, stop_status=JobStatusEnum.CANCELED.value)
    stat_logger.info(f"stop job {jid} on this party status {kill_status}")
    stat_logger.info(f"request stop job {jid} to canceled")
    j = jobs[0]
    FederatedScheduler.request_stop_job(job=j, stop_status=JobStatusEnum.CANCELED.value, command_body=j.to_dict())
    return True


def component_data_features(jid, cpn_nm='outs', role='guest', party_id=config.local_party_id, stats=False):
    from fate_flow.web_server.data import component_output_data
    df = component_output_data(jid, cpn_nm, pid=party_id, role=role, limit=1 if not stats else 1000)
    if not df: return None, None
    df, cnt = df
    if not stats: return list(df.columns.values[1:])
    return list(df.columns.values[1:]), statistics(df)


def check_sample_auth(party_info, mdl_name):
    endpoint = "/canvas/host_job_sample_auth"
    for out_party in party_info["host"]:
        dest_party_id = out_party["party_id"]
        json_body = {
            "sample_id": out_party["sample_id"],
            "sample_name": out_party["sample_name"],
            "apply_party_id": config.local_party_id,
            "module_name": re.sub(r"_.*", "", mdl_name)
        }
        try:
            ret = federated_api(job_id="model_train_auth",
                                method='POST',
                                endpoint=endpoint,
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=dest_party_id,
                                json_body=json_body,
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                return False, "合作方样本{}权限验证失败".format(out_party["sample_name"])
            if not ret["data"]:
                return False, ret["retmsg"]
        except Exception as e:
            stat_logger.exception(e)
            return False, "合作方样本{}权限验证失败".format(out_party["sample_name"])
    return True, "success"


def update_project_canvas4hosts(canvas_id, cnvs_cntt, usr=None):
    return update_canvas4hosts(canvas_id,
                               "/canvas/host_save",
                               {"canvas_content": cnvs_cntt, "canvas_id": canvas_id,
                                       "user_name": usr})


def update_canvas4hosts(canvas_id, endpoint, body):
    pc = ProjectCanvasService.get_or_none(id=canvas_id)
    assert pc, f"Can't find canvas which was just updated:{canvas_id}"
    error_info = {}
    for p in ProjectPartyService.get_join_party([pc.project_id]).dicts():
        ret = federated_api(job_id=generate_job_id(),
                            method='POST',
                            endpoint=endpoint,
                            src_role="guest",
                            src_party_id=config.local_party_id,
                            dest_party_id=p["party_id"],
                            json_body=body,
                            federated_mode=ENGINES["federated_mode"])
        if ret["retcode"]:
            stat_logger.error(f"{p['party_id']}: {ret['retmsg']}")
            error_info[p['party_id']] = ret["retmsg"]

    return error_info


def notify_host_job_end(job_id, party_info, canvas_id,
                        used_model_id=None, used_model_version=None,
                        job_detail=None):
    error_info = {}
    cnvs = ProjectCanvasService.get_or_none(id=canvas_id)
    if not cnvs:
        stat_logger.exception(f"Can't find canvas: {canvas_id}")
        return {"guest": f"Can't find canvas: {canvas_id}"}
    proj = ProjectInfoService.get_or_none(id=cnvs.project_id)
    if not proj:
        stat_logger.exception(f"Can't find project: {cnvs.project_id}")
        return {"guest": f"Can't find project: {cnvs.project_id}"}
    endpoint = "/canvas/host_training_run"
    for out_party in party_info["host"]:
        dest_party_id = out_party["party_id"]
        json_body = {
            "project_id": proj.id,
            "project_name": proj.name,
            "guest_party_id": config.local_party_id,
            "project_comments": proj.comments,
            "job_id": job_id,
            "canvas_id": cnvs.id,
            "job_name": cnvs.job_name,
            "sample_id": out_party["sample_id"],
            "job_type": cnvs.job_type,
            "apply_party_id": config.local_party_id,
            "used_model_id": used_model_id,
            "used_model_version": used_model_version,
            "job_detail": job_detail
        }
        try:
            ret = federated_api(job_id=job_id,
                                method='POST',
                                endpoint=endpoint,
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=dest_party_id,
                                json_body=json_body,
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                error_info[dest_party_id] = ret["retmsg"]
        except Exception as e:
            stat_logger.exception(e)
            error_info[dest_party_id] = str(e)
    return error_info


def exception_interpret(error):
    if not error: return
    error = error[-3000:]
    patt = [
        (r".* _export_model", ""),
        (r"job submit failed,.* has redundant parameters: [^a-zA-Z]+([a-zA-Z_-]+)[^a-zA-Z]+.*",
         r"Sorry！任务提交失败！存在冗余参数：\1 ！"),
        (r".*ValueError: ([a-zA-Z0-9_-]+)[^a-zA-Z]* not supported, should be ([a-zA-Z0-9 ]+).*?",
         r"Sorry！任务提交失败！“\1” 参数不正确，应该为\2 ！"),
        (r".*got an unexpected keyword argument '([^']+)'.*?", r"Sorry！任务提交失败！存在冗余参数“\1”！"),
        (r".* has no attribute 'features'.*", r"Sorry！上游任务没有特征数据！"),
        (r".*validation freqs must be set.*", r"Sorry！当设置了早停轮次(early stopping rounds)时，必须设置验证频率（validation freqs）！"),
        (r".*early_stopping_rounds and callback.*", r"Sorry！早停轮次(early stopping rounds)和回调参数不能同时设置！"),
        (r".*validation_freqs and callback_param.*", r"Sorry！验证频率（validation freqs）和回调参数（callback_param）不能同时设置！"),
        (r".*socket closed.*", r"Sorry！网络连接出现问题，请重试！"),
        (r".*sum of top rate and other rate .*", r"Sorry！大样本采样比例（top rate）和小样本采样比例（other rate）的和应小于等于1！"),
        (r".*if \"name\" in parameters and \"namespace\" in parameters.*", "Sorry！未找到数据，您可能需要设置需要加载的数据！"),
        (r".*Pailliar encryption mode supports [^a-z]+sgd[^a-z]+.*", "Sorry！Pailliar加密算法仅仅支持SGD的优化算法(optimizer)！"),
        (r".* '([^']+)' is not in list.*", r"Sorry! \1不存在！"),
        (r".*selection param.*should be a float or int.*", r"Sorry! 未设置Threashold，任务提交失败！"),
        (r".*(call.cc|connection refused).*", r"Sorry! 网络错误，任务提交失败！"),
        (r".*(ValueError\(.*shapes .* not aligned|IndexError\('.*homo).*", r"Sorry! 任务失败，两方特征必须对齐！"),
        (r".*ValueError\(.*not found in data header.*", r"Sorry！任务失败，未找到特征列，请根据上游任务输出来配置！"),
        (r".*hash_method  not supported.*", r"Sorry！任务提交失败！哈希函数未设置！"),
        (r".*checkpoint was found.*", r"Sorry！任务提交失败！未找到需加载的组件！请确认是否设置了回调参数！"),
        (r".*not equals to num row of output.*", r"Sorry！任务失败！请确认是否加入求交组件！"),
        (r".*can not found table name: ([^ ]+) .*", r"Sorry！任务失败！无法找到文件：\1！"),
        (r".*k_fold.*serialize.*", r"Sorry！任务失败！交叉验证和模型存储（回调参数中ModelCheckPoint）不能同时设置，请选择其它回调函数！"),
        (r".*(batch_size is|batch size).*", r"Sorry！任务失败！可能是样本数据太少(<=10)导致！"),
        (r".*Only one class present in y_true.*", r"Sorry！模型评估失败，数据集中只存在一种类别，请调整数据划分！"),
        (r".*evaluation/.*", r"Sorry！模型评估失败，可能是结果并不适合做出评估！"),
        (r".*model weights are overflow.*", r"Sorry！任务失败！模型权重参数溢出，可能是特征中有异常数据导致，请更换优化器（Optimizer）或尝试先进行特征预处理，如归一化！"),
        (r".*Onehot input data support integer or string only ([^：]+：[^\t\r\n ]+).*",
         r"Sorry！任务失败！独热编码只支持处理整型或字符串类型的特征(\1)！"),
        (r".*expected .*([0-9]+)_.*shape.*", r"Sorry！第\1层网络输入输出的维度没有对齐，请修改Input Shape！"),
        (r".*shape \(([None0-9, ]+)\) .*shape \(([None0-9, ]+)\).*", r"Sorry！网络层的输入输出维度没有对齐，数据维度为【\1】, 但网络设定为【\2】"),
        (r".*target size [^\[\]]+\[([None0-9, ]+)\].*input size [^\[\]]+\[([None0-9, ]+)\].*", r"Sorry！目标数据维度（\1）和输入数据维度（\2）没有对齐!"),
        (r".*mat1 and mat2 shapes cannot be multiplied \(([0-9x]+) and ([0-9x]+)\).*",
         r"Sorry！网络层的输入输出维度没有对齐，数据维度为【\1】, 但网络设定为【\2】"),
        (r".*lable = int(label).*", r"Sorry！标签设定有误，分类标签应为字符串或整型！"),
        (r".*Host party .*woe transform.*", r"Sorry！合作方暂时不支持WOE的转换！"),
        (r".*cardinality-only .* rsa .*", r"Sorry！”Cardinality Only“只支持RSA方式！"),
        (r".*RSA split_calculation.*", r"Sorry！分片计算（Split Calculation）不支持Cache！"),
        (r".*Preprocessing does not support cache.*", r"Sorry！预处理不支持Cache！"),
        (r".*cache is not available for cardinality_only mode.*", r"Sorry！Cache不支持分片计算（Split Calculation）！"),
        (r".*cardinality-only .* unified .*", r"Sorry！”Cardinality Only“不支持分片计算（Split Calculation）！"),
        (r".*lable not .*sample rate.*", r"Sorry！请设置标签的采样比例后重试！"),
        (r".*provide at least one column.*", r"Sorry! 任务提交失败！请确保选择至少一个特征进行计算！"),
        (r".*need_run should be true.* when cross_parties is true.*",
         r"Sorry! 任务提交失败！当激活“Cross Parties”时，请确保选择至少一个特征进行计算！"),
        (r".*can not found input table.*", r"Sorry！无法读取上游任务数据输出！"),
        (r".*KeyError: *'([^']+)'.*", r"Sorry！任务失败！未找到特征‘\1’"),
        (r".*network.*", r"Sorry! 网络错误，任务提交失败！"),
        (r".*features.* out of bounds.*", r"Sorry! 任务失败！特征数没有对齐，请检查上下游的特征数是否一致。"),
        (r".*bin_names.*", r"Sorry! 任务提交失败！参数有误，在‘基本参数’中设定的特征和‘手动划分’中设置的特征不同。"),
        (r".*convert string to float: '([^:]+)'.*", r"Sorry! 任务提交失败！参数有误，不能将‘\1’转化为浮点数！"),
        (r".* no attribute 'split'", r""),
        (r".* intersect_method +not supported.*", r"Sorry! 任务提交失败！请选择合理的求交方式。"),
        (r".*count of data_instance is 0.*", r"Sorry! 任务失败！未找到指定数据。"),
        (r".*only data with match_id may apply left_join.*", r"Sorry! 任务失败！选择Left Join时，数据源设置需激活“Without ID”"),
        (r".* should be given in sorted order.*", r"Sorry! 任务提交失败！分割点请按从小到大的顺序设置。"),
        (r".*does not support multi-host.*", r"Sorry! 任务提交失败！不支持多个合作方！"),
        (r".*valueerror:([^\)]+).*", r"Sorry! 任务失败！\1。"),
        (r".*classes must be.*", r"Sorry! 任务失败！缺少分类目标！"),
        (r".*databaseerror.*", r"Sorry! 数据库连接错误！"),
        # (r".*'y'.*", r"Sorry! 数据缺少标签列！"),
        (r".*data_transform.py\",.*", r"Sorry! 任务提交失败！请正确配置“Label Name”!"),
        (r".*header should be the same.*", r"Sorry! 任务失败！特征名称不一致，无法兼容！"),
        (r".*convert float nan to .*", r"Sorry! 任务失败！无法计算float NaN！"),
        (r".*>>>>: ([^ ]+).*", r"Sorry! 任务失败！\1！"),
        (r".*reveal strategy: encrypted_reveal_in_host mode is not allow to reveal every iter.*",
         "Sorry! 任务提交失败！Reveal Strategy为“Encrypted Reveal In Host”时，Reveal Every Iteration不能激活！"),
        (r".*cannot call 'vectorize' on size 0 inputs.*", r"Sorry! 任务失败！发现存在缺省值而无法计算！建议先进行缺失值填充！"),
        (r".*Error:([^\}\{:]+).*", r"Sorry! 任务失败！\1。"),
        (r".*cross_entropy.*", r"Sorry！任务失败！该场景下不支持目标函数cross entropy！"),
        (r"[\\]+", r""),
        (r".*internal server error.*", r"Sorry! 任务提交失败！参数有误。"),
        (r".*Error\(['\"]+(.*)['\"],*\).*", r"Sorry！任务失败！\1"),
    ]

    for p, r in patt: error = re.sub(p, r, error, flags=re.IGNORECASE)
    return error
