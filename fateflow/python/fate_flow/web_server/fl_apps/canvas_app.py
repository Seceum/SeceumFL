import os, re, json, shutil
from copy import deepcopy
import pandas as pd
from flask import request, send_file
from flask_login import login_required, current_user
from fate_flow.web_server.fl_config import config
from fate_flow.utils.api_utils import server_error_response, get_data_error_result, federated_api
from fate_flow.web_server.db_service.job_service import JobContentService
from fate_flow.web_server.utils.common_util import get_uuid, get_format_time, get_df_types, get_field_type
from fate_flow.web_server.utils.enums import OwnerEnum, StatusEnum, RoleTypeEnum, JobStatusEnum, \
    PublishStatusChineseEnum, SamplePublishStatusEnum, ApproveStatusEnum, SampleStatusEnum
from fate_flow.web_server.db_service.sample_service import SampleService, VSampleInfoService, SampleAuthorizeService
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db.db_models import StudioProjectCanvas
from fate_flow.web_server.db_service.model_service import ModelInfoExtendService
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.db_service.project_service import ProjectCanvasService, ProjectInfoService, \
    ProjectSampleService
from fate_flow.settings import stat_logger, ENGINES
from fate_flow.utils import job_utils
from fate_flow.web_server.utils.reponse_util import get_json_result, validate_canvas_id, validate_project_id
from fate_flow.web_server.utils.upload_utils import Diy_upload
from fate_flow.web_server.data import df2json
from fate_flow.web_server.db_service.algorithm_service import SampleAlgorithmService
from fate_flow.web_server.utils.job_utils import job_run_operate
from fate_flow.utils.log_sharing_utils import ErrorLogCollector, LogCollector
from fate_flow.web_server.pipeline_wrapper import exception_interpret, WrapperFactory
from fate_flow.web_server.utils.license_util import check_license
from fate_flow.web_server.data import component_output_data, statistics, column_view
from fate_flow.web_server.pipeline_wrapper.canvas_jobs import update_project_canvas4hosts, create_job_conf, \
    update_canvas4hosts
from fate_flow.web_server.pipeline_wrapper.filter_log import *


@manager.route('/component/run', methods=['post'])
@login_required
@validate_request("last_job_id", "last_component_name", "module", "parameters")
def component_run():
    from fate_flow.web_server.pipeline_wrapper import component_run
    try:
        return get_json_result(data=component_run(request.json, current_user.username))
    except Exception as e:
        return server_error_response(e)


@manager.route('/component/stop', methods=['post'])
@login_required
@validate_request("job_id")
def component_stop():
    from fate_flow.web_server.pipeline_wrapper import component_stop

    try:
        if not component_stop(request.json["job_id"]): return get_data_error_result(100, f"Sorry，停止运行失败！")
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)


@manager.route('/component/data', methods=['post'])
@login_required
@validate_request("job_id")
def component_data():
    jid, cpn, limit, role, party_id = request.json["job_id"], request.json.get("component_name"), request.json.get(
        "limit"), request.json.get('role', "guest"), request.json.get('party_id', config.local_party_id)
    if not cpn: cpn = "outs"
    if not limit: limit = 3000

    df = None
    try:
        df = component_output_data(jid, cpn, pid=party_id, role=role, limit=max(int(limit), 1000))
    except Exception as e:
        stat_logger.exception(e)
    if not df:
        return get_data_error_result(100, "Sorry, 查找不到组件输出！")
    df, cnt = df

    sts = statistics(df)
    return get_json_result(data={
        "total": cnt,
        "loaded": len(df),
        "column_num": len([c for c in df.columns if not re.match(r".*id$", c, flags=re.IGNORECASE)]) - 1,
        "rows": df.iloc[0: limit, 0:256].fillna('-').to_dict("records"),  # df2json(df.iloc[0: limit, 0:256]),
        "columns": column_view(df),
        "statistic": sts,
        "is_all_columns_included": 256 > len(df.columns)
    })


@manager.route('/component/data/download', methods=['post'])
@login_required
@validate_request("job_id")
def component_data_download():
    jid, cpn, limit = request.json["job_id"], request.json.get("component_name"), request.json.get("limit")
    role = request.json.get("role", "guest")
    if not cpn: cpn = "outs"
    if not limit: limit = 30000
    limit = int(limit)

    df = None
    try:
        df = component_output_data(jid, cpn, pid=config.local_party_id, role=role, limit=limit)
    except Exception as e:
        stat_logger.exception(e)
    if not df:
        return get_data_error_result(100, "Sorry, 查找不到组件输出！")
    df, cnt = df
    df.to_csv(f"/tmp/{jid}.csv", sep=",", index=False)
    return send_file(f"/tmp/{jid}.csv", mimetype="text/csv", as_attachment=True)


@manager.route('/component/data/features', methods=['post'])
@check_license
@validate_request("job_id", "role", "party_id")
def component_data_features():
    from fate_flow.web_server.pipeline_wrapper import component_data_features
    stats = request.json.get("stats", False)
    feas = component_data_features(request.json["job_id"],
                                   request.json.get("component_name", "outs"),
                                   request.json["role"],
                                   request.json["party_id"],
                                   stats=stats)

    if stats: feas, stats = feas

    if not feas: return get_data_error_result(100, "Sorry, 查找不到组件输出！")

    return get_json_result(data={
        "features": feas,
        "stats": stats
    })


@manager.route('/component/data/save', methods=['post'])
@login_required
@validate_request("job_id", "sample_name")
def component_data_save():
    jid, proid, nm = request.json["job_id"], request.json.get("project_id"), request.json["sample_name"]
    cpn = request.json.get("component_name")
    if not cpn: cpn = "outs"

    if not request.json["sample_name"]: return get_data_error_result(100, "请为您的新样本取个靓名！")

    obj = SampleService.query(name=request.json["sample_name"])
    if obj:
        return get_data_error_result(100, "Sorry, 样本名称已存在，请重新取个靓名！")

    df = component_output_data(jid, cpn, pid=config.local_party_id, role='guest')
    if not df:
        return get_data_error_result(100, "Sorry, 查找不到组件输出！")
    df, cnt = df
    # remove comma in values
    clms = df.select_dtypes([object]).columns
    df[clms] = df[clms].astype(str).replace(",", "", regex=True)

    # save file to local
    job_id = job_utils.generate_job_id()
    filename = os.path.join(job_utils.get_job_directory(job_id), 'fate_upload_tmp', nm)
    temp_party_filename = os.path.join(job_utils.get_job_directory(job_id), 'temp_party', nm)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    os.makedirs(os.path.dirname(temp_party_filename), exist_ok=True)
    try:
        df.to_csv(filename, index=False)
        if os.stat(filename).st_size <= 0:
            return get_data_error_result(100, 'Sorry, 上传的文件并无半点字迹！')
    except Exception as e:
        shutil.rmtree(os.path.join(job_utils.get_job_directory(job_id), 'fate_upload_tmp'))
        shutil.rmtree(os.path.join(job_utils.get_job_directory(job_id), 'temp_party'))
        stat_logger.exception(e)
        raise e

    # upload file to fate
    job_config = {'table_name': nm, 'namespace': config.namespace,
                  'head': True, 'partitions': config.partition, 'drop': 1,
                  'file': filename,
                  'name': nm, 'destroy': True}

    try:
        myupload = Diy_upload()
        myupload.diy_run(job_id, job_config)
    except Exception as e:
        stat_logger.exception(e)
        return get_data_error_result(100, "Sorry, 上传样本未成功！")

    # save sample info & field info
    sample_id = get_uuid()
    create_time = get_format_time()
    info = {
        "name": nm,
        "publish_status": SampleStatusEnum.IMMUTABLE.value,
        "owner": OwnerEnum.OWN.value,
        "creator": current_user.username,
        "create_time": create_time,
        "party_id": config.local_party_id,
        "id": sample_id,
        "party_name": config.local_party_name,
        "file_path": filename,
        "comments": request.json.get("comments", "")
    }

    field_data = []
    for sample_dict in get_field_type(df, get_df_types(df.dtypes.values)):
        sample_dict["creator"] = current_user.username
        sample_dict["id"] = get_uuid()
        sample_dict["sample_id"] = sample_id
        sample_dict["create_time"] = create_time
        field_data.append(sample_dict)

    SampleService.create_sample(info, field_data)

    return get_json_result(data={"sample_id": sample_id, "sample_name": nm})


@manager.route("/host_fusion_store", methods=['POST'])
@check_license
def host_fusion_store():
    req_data = request.json
    project_id = req_data["project_id"]
    role = RoleTypeEnum.HOST.value
    party_id = config.local_party_id
    v_sample_list = req_data["v_sample_list"]
    job_type = req_data["job_type"]
    user = "{}-{}".format("out_party_id", req_data["src_party_id"])
    job_run_operate(project_id, role, party_id, v_sample_list, user, job_type)
    return get_json_result(data=True)


@manager.route("/component/data_count", methods=['POST'])
@check_license
@validate_request("job_id")
def data_count():
    cmp_nm = request.json.get("component_name", "outs")
    _, cnt = component_output_data(request.json["job_id"], cmp_nm, pid=config.local_party_id, role='host')
    return get_json_result(data={"sample_count": cnt})


@manager.route('/component/data/register', methods=['post'])
@login_required
@validate_request("canvas_id", "job_id", "component_name", "fusion_name")
@validate_canvas_id
def component_data_register():
    """任务的输出数据进行登记，用作其他任务的输入"""
    # mix_type 建模模型：纵向0 横向1
    req_data = request.json
    canvas_id = req_data["canvas_id"]
    job_id = req_data["job_id"]
    component_name = req_data["component_name"]
    fusion_name = req_data["fusion_name"]

    cnvs = ProjectCanvasService.get_or_none(id=canvas_id)
    if not cnvs: return get_data_error_result(100, f"Sorry, 当前画布不存在!")
    mix_type = cnvs.job_type
    project_id = cnvs.project_id

    # 判断融合样本名称是否已经存在
    if ProjectSampleService.join_by_Vsample(project_id, filters=[VSampleInfoService.model.v_name == fusion_name]):
        return get_data_error_result(100, f"Sorry, 融合样本名称：‘{fusion_name}’ 已存在！")
    # 1. 加载作业信息
    jb = JobContentService.get_or_none(job_id=job_id)
    if not jb: return get_data_error_result(100, f"Sorry, 上游任务 {job_id} 不存在!")

    host_party_ids = [host["party_id"] for host in jb.party_info.get("host", [])]
    role = "guest" if config.local_party_id not in host_party_ids else "host"

    _, cnt = component_output_data(job_id, "outs", pid=config.local_party_id, role=role)
    if mix_type == "横向建模":
        if role == "guest":
            for dest_party_id in host_party_ids:
                try:
                    ret = federated_api(job_id=job_id,
                                        method='POST',
                                        endpoint="/canvas/component/data_count",
                                        src_role="guest",
                                        src_party_id=config.local_party_id,
                                        dest_party_id=dest_party_id,
                                        json_body={"job_id": job_id},
                                        federated_mode=ENGINES["federated_mode"])
                    if ret["retcode"]:
                        stat_logger.error(f"{dest_party_id}: {ret['retmsg']}")
                    else:
                        cnt += ret["data"]["sample_count"]
                except Exception as e:
                    stat_logger.exception(e)
        else:
            try:
                dest_party_id = jb.party_info["guest"]["party_id"]
                ret = federated_api(job_id=job_id,
                                    method='POST',
                                    endpoint="/canvas/component/data_count",
                                    src_role="guest",
                                    src_party_id=config.local_party_id,
                                    dest_party_id=dest_party_id,
                                    json_body={"job_id": job_id},
                                    federated_mode=ENGINES["federated_mode"])
                if ret["retcode"]:
                    stat_logger.error(f"{dest_party_id}: {ret['retmsg']}")
                else:
                    cnt += ret["data"]["sample_count"]
            except Exception as e:
                stat_logger.exception(e)

    # 3. 保存融合数据

    usr = current_user.username
    v_sample = {
        "v_name": fusion_name,
        "mix_type": mix_type,
        "job_id": job_id,
        "component_name": component_name,
        "party_info": jb.party_info,
        "sample_count": cnt
    }
    job_type = mix_type
    v_sample_list = [v_sample, ]
    v_sample_copy = deepcopy(v_sample_list)
    v_ids = job_run_operate(project_id, RoleTypeEnum.GUEST.value,
                            config.local_party_id, v_sample_copy,
                            usr, job_type)

    if role == "host": return get_json_result(data={"sample_id": v_ids[0]})

    # 通知 host方
    endpoint = "/canvas/host_fusion_store"
    error_info = {}
    for dest_party_id in host_party_ids:
        try:
            ret = federated_api(job_id=job_id,
                                method='POST',
                                endpoint=endpoint,
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=dest_party_id,
                                json_body={"project_id": project_id, "v_sample_list": deepcopy(v_sample_list),
                                           "job_type": job_type},
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                error_info[dest_party_id] = ret["retmsg"]
                stat_logger.error(f"{dest_party_id}: {ret['retmsg']}")
        except Exception as e:
            stat_logger.exception(e)
            error_info[dest_party_id] = str(e)
            VSampleInfoService.delete_by_id(v_ids[0])

    if error_info:
        error_info = ";".join([f"合作方：{k} 保存数据出错：{v}" for k, v in error_info.items()])
        return get_data_error_result(100, f"Sorry, {error_info}")

    return get_json_result(data={"sample_id": v_ids[0]})


@manager.route('/save', methods=['post'])
@login_required
@validate_request("canvas_id", "canvas_content")
@validate_canvas_id
def save():
    """保存画布及各个组件的运行数据信息"""
    canvas_id = request.json["canvas_id"]
    cnvs_cntt = request.json["canvas_content"]
    cmd = request.json.get("command", "save")
    if ProjectCanvasService.update_by_id(canvas_id, {
        "canvas_content": cnvs_cntt,
        "status": cmd,
        "updator": current_user.username
    }) != 1: return get_data_error_result(100, "Sorry, 画布保存失败！")

    update_project_canvas4hosts(canvas_id, cnvs_cntt, current_user.username)
    return get_json_result(data=[])


@manager.route('/host_save', methods=['post'])
@check_license
def host_save():
    """保存画布及各个组件的运行数据信息"""
    canvas_id = request.json["canvas_id"]
    cnvs_cntt = request.json["canvas_content"]
    usr = request.json.get("user_name")

    dt = {
        "canvas_content": cnvs_cntt,
        "status": "save"
    }
    if usr: dt["updator"] = usr
    if ProjectCanvasService.update_by_id(canvas_id, dt) != 1: return get_data_error_result(100, "Sorry, 画布保存失败！")
    return get_json_result(data=[])


@manager.route('/load', methods=['post'])
@login_required
@validate_request("canvas_id")
@validate_canvas_id
def load():
    """查看画布及各个组件的运行数据信息"""
    canvas_id = request.json["canvas_id"]
    objs = ProjectCanvasService.query(id=canvas_id, cols=[ProjectCanvasService.model.canvas_content]).dicts()
    if not objs: return get_data_error_result(100, "Sorry, 画布查找失败！")

    return get_json_result(data=objs[0]["canvas_content"])


from fate_flow.db.db_models import Job


@manager.route('/component/history', methods=['post'])
@login_required
@validate_request("canvas_id", "module")
@validate_canvas_id
def component_history():
    """查看画布中某个模块的执行历史"""
    cid = request.json["canvas_id"]
    mdl = request.json["module"]
    objs = JobContentService.query(canvas_id=cid, module_name=mdl, cols=[JobContentService.model.job_id,
                                                                         JobContentService.model.job_name,
                                                                         JobContentService.model.creator]).dicts()
    basics = {o["job_id"]: {"name": o["job_name"], "creator": o["creator"]} for o in objs}
    if not objs: return get_data_error_result(100, "Sorry, 找不到任务信息！")

    arr = []
    cols = ["job_id", "start_date", "end_date", "elapsed", "status"]
    for j in Job.select().where(Job.f_job_id.in_([o["job_id"] for o in objs]), Job.f_role == "guest").order_by(
            Job.f_create_time.desc()).dicts():
        job = {c: j.get(f"f_{c}") for c in cols}
        for k, v in basics[job["job_id"]].items(): job[k] = v
        arr.append(job)
    return get_json_result(data=arr)

    # transpose rows and columns for jobs
    # keys = set([])
    # for a in arr: keys |= set(a.keys())
    # res = {k: [] for k in list(keys)}
    # for a in arr:
    #    for k, v in a.items():
    #        res[k].append(v)

    # return get_json_result(data=res)


@manager.route('/component/parameters', methods=['post'])
@login_required
@validate_request("job_id")
def component_parameters():
    jid = request.json['job_id']
    jb = JobContentService.get_or_none(job_id=jid)
    if not jb: return get_data_error_result(100, f"Sorry, 找不该任务执行记录！")

    jobs = Job.query(job_id=jid)
    if not jobs: return get_data_error_result(100, f"Sorry, 找不该任务执行的记录！")
    prcs = 0
    for j in jobs: prcs += j.f_progress
    prcs = prcs * 1. / len(jobs)

    return get_json_result(data={
        "parameter": jb.run_param,
        "job_id": request.json["job_id"],
        "model_info": {"model_version": jid},
        "nodeState": jobs[0].f_status,
        "progress": prcs,
        "start_date": jobs[0].f_start_date,
        "end_date": jobs[0].f_end_date,
        "elapsed": jobs[0].f_elapsed,
        "job_name": jb.job_name
    })


@manager.route('/label_info', methods=['post'])
@login_required
@validate_request("canvas_id")
@validate_canvas_id
def label_info():
    """获得任务的label信息，binary，multi,regression"""
    canvas_id = request.json["canvas_id"]
    objs = ProjectCanvasService.query(id=canvas_id, cols=[ProjectCanvasService.model.target_content]).dicts()
    if not objs: return get_json_result(data=[])

    return get_json_result(data=objs[0]["target_content"])


def project_operate(canvas_id, canvas_name, project_id, new_cid=None):
    objs = ProjectCanvasService.query(job_name=canvas_name, project_id=project_id)
    if objs: raise ValueError("画布名已被占用，请重新取个靓名！")
    cnvs = ProjectCanvasService.get_or_none(id=canvas_id)
    cnvs.id = get_uuid() if not new_cid else new_cid
    cnvs.job_name = request.json["canvas_name"]
    cnvs.creator = current_user.username
    cnvs.status = "save"
    cnvs.target_content = None
    if cnvs.canvas_content:
        for i in range(len(cnvs.canvas_content)):
            if cnvs.canvas_content[i]["shape"] != "myNode": continue
            if not cnvs.canvas_content[i].get("data"): continue
            for k in ["error", "job_id", "model_info", "nodeState", "progress"]:
                if k in cnvs.canvas_content[i]["data"]:
                    del cnvs.canvas_content[i]["data"][k]
            if not re.search(r"(LR|Lin|means|NN|Poisson|XGB|Light|DataTra|Interse)",
                             cnvs.canvas_content[i]["data"].get("nodeName", "")) \
                    and "parameter" in cnvs.canvas_content[i]["data"]: del cnvs.canvas_content[i]["data"]["parameter"]
    cnvs.create_time = get_format_time()
    ProjectCanvasService.save(**(cnvs.to_dict()))
    return cnvs.id


@manager.route('/host_duplicate', methods=['post'])
@check_license
@validate_request("canvas_id", "canvas_name", "project_id", "new_canvas_id")
def host_duplicate():
    try:
        project_operate(request.json['canvas_id'],
                        request.json['canvas_name'],
                        request.json['project_id'],
                        request.json['new_canvas_id'])
    except Exception as ex:
        stat_logger.exception(str(ex))
        return get_data_error_result(100, f"Sorry, 任务复制失败！")
    return get_json_result(data=[])


@manager.route('/duplicate', methods=['post'])
@login_required
@validate_request("project_id", "canvas_id", "canvas_name")
@validate_canvas_id
def duplicate():
    canvas_id = request.json['canvas_id']
    canvas_name = request.json['canvas_name']
    project_id = request.json['project_id']
    # 将相关数据通知到host方进行保存
    try:
        new_canvas_id = project_operate(canvas_id, canvas_name, project_id)
        update_canvas4hosts(canvas_id, "/canvas/host_duplicate", {"canvas_id": canvas_id,
                                                                  "new_canvas_id": new_canvas_id,
                                                                  "canvas_name": canvas_name,
                                                                  "project_id": project_id})
    except Exception as ex:
        stat_logger.exception(str(ex))
        return get_data_error_result(100, f"Sorry, 任务复制失败！{ex}")

    return get_json_result(data=[])


@manager.route('/partner', methods=['post'])
@login_required
@validate_request("canvas_id")
@validate_canvas_id
def partner():
    """复制画布"""
    canvas_id = request.json["canvas_id"]
    jb = JobContentService.get_or_none(canvas_id=canvas_id)
    if not jb.party_info: return get_data_error_result(100, "Sorry, 没有找到合作方信息！")

    pids = [h["party_id"] for h in jb.party_info.get("host", [])]
    party_df = pd.DataFrame(PartyInfoService.get_by_ids(pids, cols=[PartyInfoService.model.id.alias("party_id"),
                                                                    PartyInfoService.model.party_name]).dicts())

    return get_json_result(data=party_df.to_dict(orient="records"))


@manager.route("/host_model_save", methods=['POST'])
@check_license
def host_model_save():
    """合作方模型保存信息更新"""
    req_data = request.json
    role = RoleTypeEnum.HOST.value
    user = "{}-{}".format("out_party_id", req_data["src_party_id"])
    sample_id = req_data["sample_id"]
    initiator_party_id = req_data["initiator_party_id"]
    sample_flag, sample_obj = SampleService.get_by_id(sample_id)
    if not sample_flag: get_data_error_result(100, "Sorry, 样本id {} 不存在".format(sample_id))
    party_flag, party_obj = PartyInfoService.get_by_id(initiator_party_id)
    if not party_flag: return get_data_error_result(100, "Sorry, 合作方id {} 不存在".format(initiator_party_id))
    model_info_dict = {
        "id": req_data["model_id"],
        "project_id": req_data["project_id"],
        "project_name": req_data["project_name"],
        "job_id": req_data["job_id"],
        "job_name": req_data["job_name"],
        "name": req_data["model_name"],
        "version": req_data["model_version"],
        "role_type": role,
        "sample_id": req_data["sample_id"],
        "sample_name": sample_obj.name,
        "party_id": config.local_party_id,
        "initiator_party_id": initiator_party_id,
        "initiator_party_name": party_obj.party_name,
        "mix_type": req_data["mix_type"],
        "status": PublishStatusChineseEnum.UNPUBLISHED.value,
        "creator": user,
    }
    ModelInfoExtendService.save(**model_info_dict)
    return get_json_result(data=True)


@manager.route('/model_store', methods=['post'])
@validate_request("canvas_id", "model_name", "module")
@validate_canvas_id
def model_store():
    """模型保存"""
    canvas_id = request.json["canvas_id"]
    model_name = request.json["model_name"]
    mdlnm = request.json["module"]

    if ModelInfoExtendService.query(name=model_name): return get_data_error_result(100, f"Sorry, 模型名称 {model_name} 已存在")

    # Extract component sequences which will be used by prediction from canvas json
    canvas_obj = StudioProjectCanvas.get_or_none(id=canvas_id)
    if not canvas_obj: return get_data_error_result(100, "Sorry, 找不到该画布信息！")

    from fate_flow.web_server.crons.pipeline_wraper_detector import be_graph
    gh = be_graph(canvas_obj.canvas_content)
    cpns, mdids = [], []

    def dfs(n):
        nonlocal gh, cpns, mdids
        nn, st = gh[n]['data']['nodeName'], gh[n]["data"]["nodeState"]
        # if re.match(r"(intersection|datatransform)", nn, flags=re.IGNORECASE) and \
        #        not re.match(r"datatransform1", nn, flags=re.IGNORECASE): return
        if st != JobStatusEnum.SUCCESS.value: raise ValueError("Some jobs are not success yet!")
        dt = gh[n]["data"]
        cpns.append((dt["model_info"]["model_version"], [f"{nn}:{dt.get('component_name', 'outs')}"]))
        mdids.append(dt["model_info"].get("model_id"))
        if gh[n].get("from"): return dfs(gh[n]["from"][0])

    # transverse graph upwardly till intersection or datatransform part.
    try:
        for k in gh.keys():
            if gh[k]["data"]["nodeName"] == mdlnm:
                dfs(k)
                break
    except Exception as e:
        stat_logger.exception(e)
        return get_data_error_result(100, "Sorry, 请先成功训练模型！")
    if not cpns: return get_data_error_result(100, "Sorry, 没有可导出的模型！")
    model_id = mdids[0]
    model_version = cpns[0][0]

    jb = JobContentService.get_or_none(job_id=model_version)
    if not jb: return get_data_error_result(100, f"Sorry！没有任务信息！")
    if jb.module_name.find("Prediction") < 0:
        try:
            params = json.loads(jb.run_param)
            if "ModelCheckpoint" not in params.get("callback_param", {}).get("callbacks", []):
                return get_data_error_result(100, "Sorry! 没有设置回调函数（callbacks）为‘ModelCheckpoint’，暂不支持模型保存！")
        except Exception as e:
            stat_logger.exception("Abnormal run_param: " + str(e))

    # get all other info about this canvas
    project_id = canvas_obj.project_id
    job_name = canvas_obj.job_name
    role = RoleTypeEnum.GUEST.value
    party_id = config.local_party_id
    mix_type = canvas_obj.job_type

    if ModelInfoExtendService.query(id=model_version, version=model_version,
                                    role_type=role, party_id=party_id):
        return get_data_error_result(100, "Sorry, 模型已存在,无需再保存")

    flag, project_obj = ProjectInfoService.get_by_id(project_id)
    if not flag: return get_data_error_result(100, "Sorry, 项目编号 {} 不存在".format(project_id))

    # get sample info used by this model
    own_sample_id, own_sample_name, hosts = jb.party_info["guest"]["sample_id"], \
                                            jb.party_info["guest"]["sample_name"], \
                                            [{"party_id": h["party_id"], "sample_id": h["sample_id"]} for h in
                                             jb.party_info["host"]]
    project_name = project_obj.name
    model_info_dict = {
        "id": model_id,
        "project_id": project_id,
        "project_name": project_name,
        "job_id": jb.job_name,  # model_version,
        "job_name": job_name,
        "name": model_name,
        "version": model_version,
        "role_type": role,
        "sample_id": own_sample_id,
        "sample_name": own_sample_name,
        "party_id": party_id,
        "initiator_party_id": party_id,
        "initiator_party_name": party_id,
        "job_content": json.dumps({
            "model_id": model_id,
            "model_versions": cpns[::-1]
        }),
        "mix_type": mix_type,
        "status": PublishStatusChineseEnum.UNPUBLISHED.value,
        "creator": current_user.username,
    }
    obj = ModelInfoExtendService.query(id=model_id, version=model_version, role_type=role, party_id=party_id,
                                       sample_id=own_sample_id).first()
    if obj:
        return get_json_result(data=False, retcode=100, retmsg="Sorry！该模型已保过，模型名是“%s”,需重新运行才能再次保存！" % obj.name)
    ModelInfoExtendService.save(**model_info_dict)

    # notify hosts to audit the
    error_info = {}
    endpoint = "/canvas/host_model_save"
    for host_info in hosts:
        dest_party_id = host_info["party_id"]
        dest_sample_id = host_info["sample_id"]
        json_body = {
            "project_id": project_id, "project_name": project_name, "job_id": model_version, "job_name": job_name,
            "model_id": model_id,
            "model_version": model_version, "model_name": model_name, "sample_id": dest_sample_id,
            "initiator_party_id": party_id,
            "role_type": RoleTypeEnum.HOST.value,
            "status": PublishStatusChineseEnum.UNPUBLISHED.value,
            "mix_type": mix_type,
        }
        try:
            ret = federated_api(job_id=model_version,
                                method='POST',
                                endpoint=endpoint,
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=dest_party_id,
                                json_body=json_body,
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                stat_logger.error(f"{dest_party_id}: {ret['retmsg']}")
                error_info[dest_party_id] = ret["retmsg"]
        except Exception as e:
            stat_logger.exception(e)
            error_info[dest_party_id] = str(e)

    if error_info:
        error_info = ";".join([f"合作方：{k} 保存数据出错：{v}" for k, v in error_info.items()])
        return get_data_error_result(100, f"Sorry, {error_info}")

    return get_json_result(data=True)


@manager.route('/model_detail', methods=['post'])
@login_required
@validate_request("model_name")
def model_detail():
    """模型保存后，查看详情"""
    mdlnm = request.json["model_name"]
    minfo = ModelInfoExtendService.get_or_none(name=mdlnm)
    if not minfo: return get_data_error_result(100, f"Sorry, 未找到模型信息！")
    res = minfo.to_json()
    jbs = JobContentService.get_or_none(job_id=minfo.version)
    if not jbs: return get_data_error_result(100, f"Sorry, 未找到模型信息！")
    res["canvas_id"] = jbs.canvas_id

    minfo = json.loads(minfo.job_content)
    parties = {}
    try:
        for n in minfo["model_id"].split("#"):
            if n.find('-') < 0: continue
            n = n.split('-')
            if len(n) != 2: continue
            n, v = n
            if n not in parties: parties[n] = []
            parties[n].append(v)
    except Exception as e:
        stat_logger.error(f"Can't parse modelID %s for '{mdlnm}'; Exception: {e}" % minfo["model_id"])
    cpns, lines = [], []
    for ii, (v, cpnm) in enumerate(minfo["model_versions"]):
        cpnm = cpnm[0].split(":")
        if len(cpnm) == 1: cpnm.append("outs")
        jc = JobContentService.query(job_id=v).get()
        if not jc:
            stat_logger.error(f"Can't find job: {v}")
            continue
        if cpns:
            lines.append({
                "shape": "dag-edge", "attrs": {"line": {"strokeDasharray": "", "style": {"animation": ""}}},
                "zIndex": 0,
                "id": f"c49f54e0-4af7-4019-9e86-d545eca6e9e5-{ii}",
                "source": {
                    "cell": cpns[-1]["id"],
                    "port": "port1_2"
                },
                "target": {
                    "cell": f"8899f4f1-4515-41a1-90f1-{ii}",
                    "port": "port2_1"
                }
            })
        cpns.append(
            {"position": {"x": 50, "y": 130 + ii * 100}, "size": {"width": 124, "height": 46}, "view": "vue-shape-view",
             "shape": "myNode", "component": {}, "ports": {"groups": {"in": {"position": "top", "attrs": {
                "circle": {"r": 5, "magnet": True, "stroke": "#3C79F2", "strokeWidth": 1.5, "fill": "#fff",
                           "style": {"visibility": "hidden"}}}}, "out": {
                "position": {"name": "absolute", "args": {"x": 60, "y": 39}}, "attrs": {
                    "circle": {"r": 5, "magnet": True, "stroke": "#3C79F2", "strokeWidth": 1.5, "fill": "#fff",
                               "style": {"visibility": "hidden"}}}}}, "items": [{"group": "in", "id": "port2_1"},
                                                                                {"group": "out", "id": "port1_2"}]},
             "direction": [0, 1, 2, 3], "zIndex": 1,
             "id": f"8899f4f1-4515-41a1-90f1-{ii}",
             "data": {
                 "attrs": "{\"contextmenu\":\"\"}",
                 "component_name": cpnm[1],
                 "error": "",
                 "guest": str(parties.get("guest", [config.local_party_id])[0]),
                 "hosts": parties.get("host", []),
                 "job_id": v,
                 "model_info": {
                     "model_id": minfo["model_id"],
                     "model_version": v
                 },
                 "nodeClick": True,
                 "nodeIcon": "element_datasample_datasource",
                 "nodeName": cpnm[0],
                 "nodeState": "success",
                 "nodeTitle": WrapperFactory(cpnm[0], 1),
                 "parameter": jc.run_param,
                 "progress": 100
             }
             })

    cpns.extend(lines)
    res["canvas"] = cpns
    return get_json_result(data=res)


@manager.route("/model_list", methods=["POST"])
@login_required
@validate_request("project_id")
@validate_project_id
def model_list():
    project_id = request.json["project_id"]
    cols = [ModelInfoExtendService.model.id.alias("model_id"), ModelInfoExtendService.model.name.alias("model_name"),
            ModelInfoExtendService.model.mix_type,
            ModelInfoExtendService.model.version.alias("model_version")]
    data = list(ModelInfoExtendService.query(project_id=project_id, cols=cols).dicts())
    return get_json_result(data=df2json(pd.DataFrame(data)))


@manager.route("/host_job_sample_auth", methods=['POST'])
@check_license
def host_job_sample_auth():
    req_data = request.json
    sample_id = req_data["sample_id"]
    sample_name = req_data["sample_name"]
    apply_party_id = req_data["apply_party_id"]
    mdl_nm = req_data["module_name"]

    sample_auth = SampleAuthorizeService.query(apply_party_id=apply_party_id,
                                               approve_party_id=config.local_party_id,
                                               sample_id=sample_id)
    sample_objs = SampleService.query(id=sample_id, status=StatusEnum.VALID.value,
                                      publish_status=SamplePublishStatusEnum.PUBLISHED.value)
    can_use_algorithm = [sample_algorithm.module_name for sample_algorithm in
                         SampleAlgorithmService.query(sample_id=sample_id)]
    if sample_auth and sample_objs:
        auth_info = sample_auth[0]
        fusion_times_limits = auth_info.fusion_times_limits if auth_info.fusion_times_limits else 0
        if auth_info.approve_result in [ApproveStatusEnum.AGREE.value, ApproveStatusEnum.APPLY.value, ]:
            if auth_info.approve_result == ApproveStatusEnum.APPLY.value and not auth_info.fusion_deadline:
                return get_json_result(data=False, retmsg="{}已下线或未申请授权".format(sample_name))
            if auth_info.fusion_deadline < get_format_time().date():
                return get_json_result(data=False, retmsg="{}样本使用截止日期已过期".format(sample_name))
            if auth_info.fusion_limit and (auth_info.current_fusion_count >= fusion_times_limits):
                return get_json_result(data=False, retmsg="{}样本使用次数已达上限".format(sample_name))
            if mdl_nm not in can_use_algorithm and not re.match(r"(Sir|Predict)", mdl_nm, flags=re.IGNORECASE):
                return get_json_result(data=False,
                                       retmsg="{}样本没有使用{}算法的权限".format(sample_name, mdl_nm))
            return get_json_result(data=True)
        else:
            return get_json_result(data=False, retmsg="{}样本未授权".format(sample_name))
    else:
        return get_json_result(data=False, retmsg="{}已下线或未申请授权".format(sample_name))


@manager.route("/host_training_run", methods=['POST'])
@check_license
def host_training_run():
    req_data = request.json
    project_id = req_data["project_id"]
    project_name = req_data["project_name"]
    comments = req_data["project_comments"]
    guest_party_id = req_data["guest_party_id"]
    job_id = req_data["job_id"]
    job_name = req_data["job_name"]
    sample_id = req_data["sample_id"]
    canvas_id = req_data["canvas_id"]
    apply_party_id = req_data["apply_party_id"]
    current_time = get_format_time()
    job_detail = req_data['job_detail']

    if not ProjectInfoService.query(id=project_id):
        project_save_dict = {
            "id": project_id,
            "name": project_name,
            "comments": comments,
            "role_type": RoleTypeEnum.HOST.value,
            "guest_party_id": guest_party_id,
            "creator": job_detail['user_name'],
            "create_time": current_time
        }
        ProjectInfoService.save(**project_save_dict)

    # 插入job content记录到表中
    create_job_conf(cid=canvas_id,
                    job_content=job_detail['job_content'],
                    user_name=job_detail['user_name'],
                    job_id=job_id,
                    run_param=job_detail['run_param'],
                    job_name=job_name,
                    module_name=job_detail['module_name'],
                    last_job_id=job_detail.get('last_job_id'),
                    party_info=job_detail['party_info'],
                    proj_id=project_id
                    )
    # ProjectCanvasService.update_by_id(id=canvas_id, data = {"canvas_content": req_data["canvas_content"]})

    auth_obj = SampleAuthorizeService.get_or_none(sample_id=sample_id, apply_party_id=apply_party_id,
                                                  approve_party_id=config.local_party_id)
    if auth_obj and auth_obj.approve_result in [ApproveStatusEnum.APPLY.value, ApproveStatusEnum.AGREE.value]:
        auth_obj.current_fusion_count = auth_obj.current_fusion_count + 1
        auth_obj.total_fusion_count = auth_obj.total_fusion_count + 1
        auth_obj.save()

    # if used_model_version and not ProjectUsedModelService.query(job_id=job_id, canvas_id=canvas_id,
    #                                                            model_version=used_model_version):
    #    ProjectUsedModelService.create_by_info(project_id, job_id, job_type, used_model_id, used_model_version,
    #                                           canvas_id, user_name)
    # ProjectUsedSampleService.insert_by_ids(project_id, canvas_id, job_id, [sample_id], SampleTypeEnum.ORIGIN.value,
    #                                       user_name, party_id=config.local_party_id)
    return get_json_result(data=True)


@manager.route("/job_names", methods=['POST'])
@login_required
@validate_request("job_ids")
def job_names():
    jids = request.json["job_ids"]
    objs = JobContentService.query(filters=[JobContentService.model.job_id.in_(jids)],
                                   cols=[JobContentService.model.job_id, JobContentService.model.module_name,
                                         JobContentService.model.job_name]).dicts()

    res = []
    nms = set([])
    for o in objs:
        nm = re.sub(r"(hetero|homo|_[0-9]+)", "", o["module_name"], flags=re.IGNORECASE)
        i = 0
        nm_ = nm
        while nm_ in nms:
            nm_ = "%s-%d" % (nm, i)
            i += 1
        nms.add(nm_)
        res.append({"job_id": o["job_id"], "module_name": nm_, "job_name": o["job_name"]})

    return get_json_result(data=res)


@manager.route("/all_error_info", methods=['POST'])
@login_required
@validate_request("job_id")
def get_all_error_info():
    req_data = request.json
    party_id = request.json.get('party_id', config.local_party_id)
    role = request.json.get('role', 'guest')
    jbs = JobContentService.get_or_none(job_id=req_data['job_id'])
    if not jbs: return get_data_error_result(100, f"Sorry！没有任务信息！")
    jbs = jbs.party_info
    if not jbs['host']: return get_json_result(data={"本方": "Sorry！请确认合作方是否有数据！"})

    error_info = {}
    log_collect = ErrorLogCollector("partyError", req_data['job_id'], party_id=party_id, role=role)
    audit_path = log_collect.get_log_file_path()
    if audit_path:
        line_lst = log_collect.cat_log(None, None)
        error_info["本方"] = exception_interpret(" ".join([o["content"] for o in line_lst[:100]]))

    if role == 'host':
        return get_json_result(data=error_info)

    party_df = pd.DataFrame(PartyInfoService.get_by_ids([h['party_id'] for h in jbs['host']],
                                                        cols=[PartyInfoService.model.id.alias("party_id"),
                                                              PartyInfoService.model.party_name]).dicts()) \
        .set_index(["party_id"])

    # get error from hosts #
    endpoint = "/canvas/error_info"
    json_body = {
        "job_id": req_data['job_id'],
        "role": "host"
    }
    for host_info in jbs['host']:
        json_body["party_id"] = host_info['party_id']
        ret = federated_api(job_id=req_data['job_id'],
                            method='POST',
                            endpoint=endpoint,
                            src_role="guest",
                            src_party_id=config.local_party_id,
                            dest_party_id=host_info['party_id'],
                            json_body=json_body,
                            federated_mode=ENGINES["federated_mode"])
        nm = party_df.loc[str(host_info['party_id'])]["party_name"]
        error_info[nm] = ret.get("data", "")

        if not error_info[nm]:
            json_body["role"] = "arbiter"
            ret = federated_api(job_id=req_data['job_id'],
                                method='POST',
                                endpoint=endpoint,
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=host_info['party_id'],
                                json_body=json_body,
                                federated_mode=ENGINES["federated_mode"])
            error_info[nm] = ret.get("data", "")
    return get_json_result(data=error_info)


@manager.route("/error_info", methods=['POST'])
@check_license
@validate_request("job_id", "role", "party_id")
def get_job_error_info():
    req_data = request.json
    log_collect = ErrorLogCollector("partyError", req_data['job_id'], \
                                    party_id=req_data['party_id'], role=req_data['role'])
    audit_path = log_collect.get_log_file_path()
    if audit_path:
        line_lst = log_collect.cat_log(None, None)
        return get_json_result(data=exception_interpret(" ".join([o["content"] for o in line_lst[:100]])))
        # if len(line_lst) != 0:
        #    data = log_collect.parse_error_info(line_lst)
    return get_json_result(data="")


@manager.route('/component/arbitor', methods=['post'])
@check_license
@validate_request("job_id", "component_name")
def arbitor_report():
    req_data = request.json
    jbs = JobContentService.get_or_none(job_id=req_data['job_id'])
    if not jbs: return get_data_error_result(100, f"Sorry！没有任务信息！")
    jbs = jbs.party_info
    if not jbs['host']: return get_json_result(data={"本方": "Sorry！请确认合作方是否存在！"})

    req_data["role"] = "arbiter"
    req_data["party_id"] = jbs['host'][0]['party_id']
    return federated_api(job_id=req_data['job_id'],
                         method='POST',
                         endpoint="/tracking/component/metric/all",
                         src_role="guest",
                         src_party_id=config.local_party_id,
                         dest_party_id=jbs['host'][0]['party_id'],
                         json_body=req_data,
                         federated_mode=ENGINES["federated_mode"])


@manager.route("/log", methods=['POST'])
@login_required
@validate_request("job_id", "role", "party_id")
def log():
    req_data = request.json
    logs = LogCollector("componentInfo", req_data["job_id"], req_data["party_id"], req_data["role"],
                        req_data.get("component_name", "outs"))
    lines = [re.sub(r" \[[0-9]{20,}.*?: ", "", l["content"]) for l in logs.cat_log(begin=req_data.get("begin", 0)) if
             re.match(r"^\[(INFO|WARNING|ERROR)\]", l["content"]) and not log_filter(l["content"])]
    return get_json_result(data=lines)
