import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import grpc
import pandas as pd
import numpy as np
import requests
from flask_login import login_required, current_user
from fate_flow.db.runtime_config import RuntimeConfig
from fate_arch.common import file_utils
from fate_arch.common.file_utils import get_project_base_directory
from fate_flow.entity import RetCode
from fate_flow.entity.run_status import FederatedSchedulingStatusCode
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db.db_models import StudioPartyInfo, StudioModelInfoExtend, \
    StudioProjectUsedModel
from fate_flow.web_server.db_service.model_service import ModelInfoExtendService
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.fl_config import config, PARTY_ID
from fate_flow.web_server.fl_scheduling_apps.fl_command import FL_Scheduler
from fate_flow.web_server.utils.common_util import datetime_format, \
    model_can_remove, pull_approval_result, model_id_get_hosts, model_id_get_guests, model_id_get_arbiters, \
    get_role_type
from fate_flow.web_server.utils.df_apply import concat_col
from fate_flow.web_server.utils.enums import RoleTypeEnum, PublishStatusChineseEnum, StatusEnum, APPROVEChineseEnum, \
    UserAuthEnum
from fate_flow.web_server.utils.license_util import check_license
from flask import request, send_file
from fate_flow.settings import TEMP_DIRECTORY, stat_logger, IS_STANDALONE, GRPC_OPTIONS
from fate_flow.utils import job_utils
from fate_flow.utils.api_utils import federated_api
from fate_flow.web_server.utils.reponse_util import get_json_result, validate_permission_code, have_permission_code, \
    request_chain
from fate_arch.protobuf.python import inference_service_pb2, inference_service_pb2_grpc
from fate_flow.pipelined_model import publish_model


@manager.route("/list", methods=['POST'])
@login_required
@validate_request("is_join")
@validate_permission_code(UserAuthEnum.MODEL.value)
def model_list():
    """模型列表展示"""
    is_join = int(request.json["is_join"])
    proj_id = request.json.get("project_id")
    # 我发起的
    role_type = get_role_type(is_join)
    if (role_type == RoleTypeEnum.GUEST.value and not have_permission_code(UserAuthEnum.MODEL_GUEST.value)) or (
            role_type == RoleTypeEnum.HOST.value and not have_permission_code(UserAuthEnum.MODEL_HOST.value)):
        return get_json_result(retcode=100, retmsg="no permission_code")
    model_df = pd.DataFrame(ModelInfoExtendService.get_by_role(role_type).dicts())
    # 查询导入的模型，并拼接
    model_df_import = pd.DataFrame(ModelInfoExtendService.get_import_model(role_type).dicts())
    model_df = model_df.append(model_df_import)
    model_df.reset_index(drop=True)
    # 根据job_id 找到party_ids
    if model_df.empty:
        return get_json_result(data=[])
    if proj_id: model_df = model_df[model_df.project_id == proj_id].reset_index(drop=True)

    project_use_model = StudioProjectUsedModel.select(StudioProjectUsedModel.model_version)
    if project_use_model:
        used_models = set([used_model.model_version for used_model in project_use_model])
        model_df["is_used"] = np.where(model_df.version.isin(used_models), True, False)
        model_df["can_remove"] = model_can_remove(model_df)
    else:
        model_df["can_remove"] = [True] * len(model_df)
    append_list = []
    for index, row in model_df.iterrows():
        party_dicts = row.get('f_roles')
        # if party_dicts is np.nan: 导入的模型，取不到f_roles，直接跳过
        if party_dicts is np.nan:
            row["party_id"] = np.nan
            append_list.append(row)
            continue
        if party_dicts and party_dicts.get('host'):
            party_ids = party_dicts['host']
            for party_id in party_ids:
                temp_row = row.copy()
                temp_row["party_id"] = str(party_id)
                append_list.append(temp_row)
        else:
            row["party_id"] = np.nan
            append_list.append(row)
    if append_list:
        df = pd.DataFrame(append_list)
        try:
            df.drop('f_roles', axis=1, inplace=True)
        except:
            pass
    else:
        model_df["party_id"] = np.nan
        df = model_df
    party_ids = df.party_id.dropna().unique().tolist()
    party_df = pd.DataFrame(
        PartyInfoService.get_by_ids(party_ids, cols=[PartyInfoService.model.id.alias('party_id'),
                                                     PartyInfoService.model.party_name]).dicts())
    if party_df.empty:
        model_df["party_name"] = ''
        df["party_name"] = ''
    else:
        df = df.merge(party_df, left_on='party_id', right_on='party_id', how='left')

    df = df.groupby(["id", "version"]).apply(concat_col).reset_index(drop=True)
    df.rename(columns={"id": "model_id", "name": "model_name", "version": "model_version", "job_name": "task_name",
                       "job_id": "task_id"}, inplace=True)
    if df.empty:
        return get_json_result(data=[])
    df.sort_values(by='create_time', ascending=False, inplace=True)
    return get_json_result(data=df.to_dict(orient="records"))


@manager.route("/delete", methods=['POST'])
@login_required
@validate_request('model_id', 'model_version')
@validate_permission_code(UserAuthEnum.MODEL.value, UserAuthEnum.MODEL_GUEST.value,
                          UserAuthEnum.MODEL_GUEST_DELETE.value)
def delete_model():
    """模型管理_我发起的_模型删除"""
    model_id = request.json["model_id"]
    model_version = request.json["model_version"]
    model_obj = StudioModelInfoExtend.query(id=model_id, version=model_version).first()
    if not model_obj:
        return get_json_result(data=False, retmsg="模型不存在")
    command_body = {"model_id": model_id, "model_version": model_version}
    status_code, response = FL_Scheduler.model_manage_command(model_obj, "delete_model", command_body)
    if status_code != FederatedSchedulingStatusCode.SUCCESS:
        return get_json_result(data=False, retcode=100, retmsg=str(response))
    else:
        return get_json_result(data=True, retmsg="success")


@manager.route("/approval", methods=['POST'])
@login_required
@validate_request("model_id", "model_version", "operate", "operate_advise")
@validate_permission_code(UserAuthEnum.MODEL.value, UserAuthEnum.MODEL_HOST.value,
                          UserAuthEnum.MODEL_HOST_APPROVE.value)
def approve():
    # 模型审批 同意:1，拒绝:2
    request_data = request.json
    approve_result = str(request_data["operate"])
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    operate_advise = request_data["operate_advise"]
    current = datetime_format(datetime.now())
    obj = StudioModelInfoExtend.select().where(StudioModelInfoExtend.id == model_id,
                                               StudioModelInfoExtend.version == model_version).first()
    if not obj:
        return get_json_result(retcode=100,
                               retmsg="model_id,or model_version 不存在", data=False)
    # 通知guest方，更新进度条。
    json_body = {
        "model_id": model_id,
        "model_version": model_version,
    }
    status_code, response = FL_Scheduler.model_manage_command(obj, "approval_do", json_body,
                                                              dest_partis=[
                                                                  (RoleTypeEnum.HOST.value, [obj.initiator_party_id])])
    if status_code != FederatedSchedulingStatusCode.SUCCESS:
        stat_logger.exception(str(response))
        return get_json_result(data=False, retcode=100, retmsg="向guest授权失败")
    kwargs = {
        "approve_result": approve_result,
        "updator": current_user.username,
        "service_end_time": current,
        "update_time": current,
        "approve_status": APPROVEChineseEnum.APPROVE_TRUE.value if approve_result == "1" else APPROVEChineseEnum.APPROVE_FALSE.value,
        "operate_advise": operate_advise,
    }
    ModelInfoExtendService.update_by_key(model_id, model_version, "host", config.local_party_id,
                                         current_user.username, **kwargs)
    return get_json_result(data=True)


@manager.route("/approval_result", methods=["POST"])
@validate_request("model_id", "model_version", "is_join")
def approval_result():
    """展示模型各方审批详情"""
    request_data = request.json
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    is_join = request_data["is_join"]
    role_type = get_role_type(is_join)
    if role_type == RoleTypeEnum.GUEST.value:
        hosts = model_id_get_hosts(model_id)
        retcode, retmsg, host_approval_response = pull_approval_result(model_id, model_version, hosts)
        if retcode:
            return get_json_result(data=False, retcode=100, retmsg=retmsg)
        for host_id, host_response in host_approval_response.items():
            party_obj = StudioPartyInfo.select(StudioPartyInfo.party_name).where(StudioPartyInfo.id == host_id).first()
            if party_obj:
                host_approval_response[host_id]["party_name"] = party_obj.party_name
        return get_json_result(data=host_approval_response)
    else:
        obj = StudioModelInfoExtend.select(
            StudioModelInfoExtend.approve_result, StudioModelInfoExtend.sample_name,
            StudioModelInfoExtend.operate_advise, StudioModelInfoExtend.service_reason,
        ).where(StudioModelInfoExtend.id == model_id, StudioModelInfoExtend.version == model_version,
                StudioModelInfoExtend.role_type == role_type).first()
        if obj:
            data = {
                "approve_result": obj.approve_result,
                "sample_name": obj.sample_name,
                "operate_advise": obj.operate_advise,
                "service_reason": obj.service_reason,
            }
            return get_json_result(data={"my": data})
        return get_json_result(data=False, retcode=100, retmsg="没有对应model_id,model_version")


@manager.route("/release", methods=["POST"])
@login_required
@validate_request("service_name", "model_id", "model_version", "service_reason")
@validate_permission_code(UserAuthEnum.MODEL.value, UserAuthEnum.MODEL_GUEST.value,
                          UserAuthEnum.MODEL_GUEST_PUBLISH.value)
def model_release():
    """模型发布"""
    request_data = request.json
    model_id = request_data.get("model_id")
    model_version = request_data.get("model_version")
    service_reason = request_data.get("service_reason")
    service_name = request_data.get("service_name")
    service_start_time = datetime_format(datetime.now())
    objs = StudioModelInfoExtend.select().where(StudioModelInfoExtend.service_name == service_name)
    if objs:
        return get_json_result(retcode=100,
                               retmsg="Sorry！服务名称已经存在，请再取一个名字！", data=False)

    objs = StudioModelInfoExtend.select().where(StudioModelInfoExtend.id == model_id,
                                                StudioModelInfoExtend.version == model_version)
    if not objs:
        return get_json_result(retcode=100,
                               retmsg="model_id,or model_version 不存在", data=False)
    else:
        base_data = {'model_id': model_id, 'model_version': model_version,
                     "service_reason": service_reason,
                     "status": PublishStatusChineseEnum.UNPUBLISHED.value,
                     "service_name": service_name, "service_start_time": service_start_time,
                     "approve_progress": 0, "approve_result": None, "publish_result": "",
                     "service_end_time": None,
                     "operate_advise": None,
                     }
        for obj in objs:
            hosts = model_id_get_hosts(model_id)
            for host_id in hosts:
                if not PartyInfoService.query(id=host_id, status=StatusEnum.VALID.value, ping_status="正常").first():
                    return get_json_result(retmsg="合作方节点无效 或者 已删除,无法发布", data=False, retcode=100)
            dest_partis = [(RoleTypeEnum.HOST.value, [host_id for host_id in hosts])]
            status_code, response = FL_Scheduler.model_manage_command(obj, "query_model", base_data,
                                                                      dest_partis=dest_partis)
            if status_code != FederatedSchedulingStatusCode.SUCCESS:
                return get_json_result(data=False, retcode=100, retmsg="合作方模型不存在，请导入模型")
            # guest发布
            request_data = base_data.copy()
            # guest 发布
            request_data["user"] = current_user.username
            request_data["role_type"] = obj.role_type
            request_data["party_id"] = obj.party_id
            request_data["approve_status"] = APPROVEChineseEnum.APPROVE_running.value
            status_code, response = FL_Scheduler.model_manage_command(obj, "release_do", request_data,
                                                                      dest_partis=[(RoleTypeEnum.GUEST.value,
                                                                                    [PARTY_ID])])
            if status_code != FederatedSchedulingStatusCode.SUCCESS:
                stat_logger.exception(str(response))
                return get_json_result(data=False, retcode=100, retmsg="guest 模型发布失败")
            # host发布
            request_data["user"] = "{}-{}".format("out_party_id", obj.initiator_party_id)
            request_data["role_type"] = "host"
            request_data["party_id"] = host_id
            request_data["approve_status"] = APPROVEChineseEnum.APPROVE_WAITING.value
            status_code, response = FL_Scheduler.model_manage_command(obj, "release_do", request_data,
                                                                      dest_partis=dest_partis)
            if status_code != FederatedSchedulingStatusCode.SUCCESS:
                stat_logger.exception(str(response))
                return get_json_result(data=False, retcode=100, retmsg="host 模型发布失败")
        return get_json_result()


@manager.route("/export", methods=["POST"])
@login_required
@validate_permission_code(UserAuthEnum.MODEL.value)
@validate_request("model_id", "model_version", "migrate_guest_id", "migrate_host_ids", "is_join")
def export_model():
    """模型管理_我发起的、我参与的_模型导出"""
    request_config = request.json
    is_join = int(request_config["is_join"])
    role_type = get_role_type(is_join)
    if role_type == RoleTypeEnum.GUEST.value and not have_permission_code(UserAuthEnum.MODEL_GUEST.value,
                                                                          UserAuthEnum.MODEL_GUEST_EXPORT.value):
        return get_json_result(retcode=100, retmsg="no permission_code")
    elif role_type == RoleTypeEnum.HOST.value and not have_permission_code(UserAuthEnum.MODEL_HOST.value,
                                                                           UserAuthEnum.MODEL_HOST_EXPORT.value):
        return get_json_result(retcode=100, retmsg="no permission_code")
    execute_party = {}
    migrate_guest_id = int(request_config["migrate_guest_id"])
    migrate_host_ids = request_config["migrate_host_ids"]
    migrate_role = {
        "guest": [
            migrate_guest_id
        ],
        "host": migrate_host_ids
    }
    model_id = request_config["model_id"]
    model_version = request_config["model_version"]
    guests = [int(i) for i in model_id_get_guests(model_id)]
    hosts = [int(i) for i in model_id_get_hosts(model_id)]
    arbiters = [int(i) for i in model_id_get_arbiters(model_id)]
    role = {"guest": guests, "host": hosts}
    if arbiters:
        migrate_role["arbiter"] = [hosts[0]]
        role["arbiter"] = arbiters
    # PARTY_ID=request.json["guest_id"]
    if guests and int(PARTY_ID) in guests:
        execute_party["guest"] = [int(PARTY_ID)]
    if hosts and int(PARTY_ID) in hosts:
        execute_party["host"] = [int(PARTY_ID)]
    if arbiters and int(PARTY_ID) in arbiters:
        execute_party["arbiter"] = [int(PARTY_ID)]

    migrate_initiator = {
        "role": "guest",
        "party_id": migrate_guest_id
    }
    request_config = {
        "job_parameters": {
            "federated_mode": "MULTIPLE" if not IS_STANDALONE else "SINGLE"
        },
        "role": role,
        "execute_party": execute_party,
        "migrate_initiator": migrate_initiator,
        "migrate_role": migrate_role,
        "model_id": request_config["model_id"],
        "model_version": request_config["model_version"]
    }
    _job_id = job_utils.generate_job_id()
    initiator_party_id = request_config['migrate_initiator']['party_id']
    initiator_role = request_config['migrate_initiator']['role']
    request_config["unify_model_version"] = request_config["model_version"]
    migrate_status = True
    migrate_status_info = {}
    migrate_status_msg = 'success'
    migrate_status_info['detail'] = {}

    res_dict = {}
    for role_name, role_partys in request_config.get("migrate_role").items():
        for offset, party_id in enumerate(role_partys):
            local_res = {
                "role": role_name,
                "party_id": request_config.get("role").get(role_name)[offset],
                "migrate_party_id": party_id
            }
            if not res_dict.get(role_name):
                res_dict[role_name] = {}
            res_dict[role_name][local_res["party_id"]] = local_res

    for role_name, role_partys in request_config.get("execute_party").items():
        migrate_status_info[role_name] = migrate_status_info.get(role_name, {})
        migrate_status_info['detail'][role_name] = {}
        for party_id in role_partys:
            request_config["local"] = res_dict.get(role_name).get(party_id)
            try:
                response = federated_api(job_id=_job_id,
                                         method='POST',
                                         endpoint='/model_manage_schedule/export/do',
                                         src_party_id=initiator_party_id,
                                         dest_party_id=party_id,
                                         src_role=initiator_role,
                                         json_body=request_config,
                                         federated_mode=request_config['job_parameters']['federated_mode'])
                if response['retcode'] != 0:
                    return get_json_result(retcode=100,
                                           retmsg=response['retmsg'], data=response['data'])
                migrate_status_info[role_name][party_id] = response['retcode']
                execute_party_detail = {party_id: {}}
                execute_party_detail[party_id]['retcode'] = response['retcode']
                execute_party_detail[party_id]['retmsg'] = response['retmsg']
                execute_party_detail[party_id]['data'] = response['data']
                migrate_status_info['detail'][role_name].update(execute_party_detail)
            except Exception as e:
                stat_logger.exception(e)
                migrate_status = False
                migrate_status_msg = 'failed'
                migrate_status_info[role_name][party_id] = 100
                break
    if migrate_status:
        zip_archive = ""
        for role, role_dict in migrate_status_info["detail"].items():
            for party_id, party_id_dict in role_dict.items():
                zip_file = party_id_dict["data"]["path"]
                zip_parent_dir = Path(zip_file).parent
                zip_archive = zip_parent_dir.joinpath(PARTY_ID + "_" + request_config["model_version"])
                zip_archive.mkdir(parents=True, exist_ok=True)
                shutil.move(zip_file, zip_archive)
        columns = [StudioModelInfoExtend.name, StudioModelInfoExtend.project_name, StudioModelInfoExtend.job_name,
                   StudioModelInfoExtend.party_id, StudioModelInfoExtend.initiator_party_id,
                   StudioModelInfoExtend.mix_type]
        obj = StudioModelInfoExtend.query(id=model_id, version=model_version,
                                          cols=columns).dicts().first()
        obj["initiator_party_id"] = migrate_guest_id
        with open(os.path.join(zip_archive, "project_info.json"), "w") as f:
            f.write(json.dumps(obj))
        archive_file_path = str(zip_archive) + ".zip"
        shutil.make_archive(zip_archive, 'zip', zip_archive)
        shutil.rmtree(zip_archive)
        request_chain({"retcode": RetCode.SUCCESS, "retmsg": "success", "data": True}, RetCode.SUCCESS)
        return send_file(archive_file_path, attachment_filename=os.path.basename(archive_file_path), as_attachment=True)
    return get_json_result(retcode=(0 if migrate_status else 100),
                           retmsg=migrate_status_msg, data=migrate_status_info)


@manager.route("/import", methods=["POST"])
@login_required
@validate_permission_code(UserAuthEnum.MODEL.value)
def import_model():
    """模型管理_我发起的_模型导入"""
    file = request.files['file']
    file_path = os.path.join(TEMP_DIRECTORY, file.filename)
    file.save(file_path)
    file_path_dir = file_path.replace(".zip", "")
    os.makedirs(file_path_dir, exist_ok=True)
    shutil.unpack_archive(file_path, file_path_dir)
    p = Path(file_path_dir)
    model_id = ""
    model_version = ""
    for x in p.glob('*'):
        if x.suffix == ".zip":
            sub_dir = Path(str(x).replace(".zip", ""))
            shutil.unpack_archive(x, sub_dir)
            project_config = file_utils.load_json_conf(sub_dir.joinpath("import_model.json"))
            model_id = project_config["model_id"]
            model_version = project_config["model_version"]
            project_config["force_update"] = 1
            files = {'file': open(str(x), 'rb')}
            obj = ModelInfoExtendService.query(id=model_id, version=model_version,
                                               role_type=project_config["role"]).first()
            if obj:
                shutil.rmtree(file_path_dir)
                return get_json_result(data=False, retmsg="模型导入，数据已存在", retcode=100)
            response = requests.post(request.host_url + "v1/model/import", data=project_config, files=files).json()
            if response["retcode"] != 0:
                return get_json_result(data=response["data"], retmsg=response["retmsg"], retcode=100)
            if project_config["role"] == "guest":
                if not have_permission_code(UserAuthEnum.MODEL_GUEST_IMPORT.value):
                    return get_json_result(retcode=100, retmsg="no permission_code")
            elif project_config["role"] == "host":
                if not have_permission_code(UserAuthEnum.MODEL_HOST_IMPORT.value):
                    return get_json_result(retcode=100, retmsg="no permission_code")

            model_extend_info_dict = {
                "id": model_id,
                "version": model_version,
                "role_type": project_config["role"],
                "status": PublishStatusChineseEnum.UNPUBLISHED.value,
                "creator": current_user.username if hasattr(current_user, "id") else "",
                "create_time": datetime_format(datetime.now()),
                "party_id": config.local_party_id,
                "sample_id": "",
                "initiator_party_name": ""
            }
            model_extend_info_dict.update(file_utils.load_json_conf(sub_dir.parent.joinpath("project_info.json")))
            ModelInfoExtendService.save(**model_extend_info_dict)
    shutil.rmtree(file_path_dir)
    return get_json_result(data={"model_id": model_id, "model_version": model_version})


@manager.route("/detail", methods=["POST"])
@validate_request("model_id", "model_version")
@validate_permission_code(UserAuthEnum.MODEL.value, UserAuthEnum.MODEL_GUEST.value,
                          UserAuthEnum.MODEL_GUEST_DETAIL.value)
def detail():
    """查询模型详情"""
    request_data = request.json
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    obj = ModelInfoExtendService.query(id=model_id, version=model_version).first()
    if obj:
        data = {"job_id": obj.job_id, "job_content": obj.job_content}
        return get_json_result(data=data)
    else:
        return get_json_result(data=False, retcode=100, retmsg="没有对应的模型,参数有误")


@manager.route("/publish/upload", methods=["POST"])
@validate_request("model_id", "model_version", "service_name")
def publish_upload():
    """模型审批同意时，上传的预测文件"""
    request_data = request.form
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    service_name = request_data["service_name"]
    obj = ModelInfoExtendService.query(id=model_id, version=model_version, service_name=service_name).first()
    if obj:
        filename = obj.service_name + ".csv"
        filename = os.path.join(get_project_base_directory(), 'host_data', filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        file = request.files['file']
        obj.file_name = file.filename
        df = pd.read_csv(file.stream)
        df.rename({c: c.lower() for c in df.columns}, inplace=True)
        df.to_csv(filename, index=False)
        obj.save()
        return get_json_result(data=True)
    else:
        return get_json_result(data=False, retcode=100, retmsg="没有对应的模型,服务名，参数有误")


@manager.route("/download_predict_csv", methods=['POST'])
@validate_request("model_id", "model_version", "service_name")
@login_required
def get_csv():
    """下载模型预测文件，demo"""
    request_data = request.json
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    service_name = request_data["service_name"]
    obj = ModelInfoExtendService.query(id=model_id, version=model_version, service_name=service_name).first()
    if obj:
        file_path = os.path.join(get_project_base_directory(),
                                 "fateflow/python/fate_flow/web_server/data/breast_hetero_guest.csv")
        return send_file(file_path, mimetype="text/csv", attachment_filename=obj.file_name, as_attachment=True)
    else:
        return get_json_result(data=False, retcode=100, retmsg="数据不存在")


@manager.route("/inference", methods=["POST"])
@login_required
@validate_permission_code(UserAuthEnum.MODEL.value)
def inference():
    """在线推理服务"""
    svr = RuntimeConfig.SERVICE_DB.get_urls("servings")
    if not svr: return get_json_result(data=False, retcode=100, retmsg="在线推理服务不存在!")
    svr = svr[0]
    with grpc.insecure_channel(svr, GRPC_OPTIONS) as channel:
        stub = inference_service_pb2_grpc.InferenceServiceStub(channel)
        req = inference_service_pb2.InferenceMessage()
        req.body = json.dumps(request.json).encode("utf-8")
        res = json.loads(stub.inference(req).body.decode("utf-8"))
        res["data"] = {k: v for k, v in res["data"].items() if not re.search(r"(model|time)", k)}
        if res["retmsg"].find("host") >= 0: res["retmsg"] = "合作方未找到样本！"
        return res


@manager.route("/get_feature", methods=["POST"])
@validate_request("id", "service_id")
def get_feature():
    try:
        filename = os.path.join(get_project_base_directory(), 'host_data', request.json["service_id"] + ".csv")
        df = pd.read_csv(filename).set_index(["id"])
        columns = df.columns.values
        df = df.loc[request.json["id"], :]
        if isinstance(df, pd.DataFrame): df = df.iloc[0, :]
        assert len(df) == len(columns), f"Features names and features values don't match {len(df)} vs {len(columns)}"
        df = {c: float(df[i]) if type(df[i]) != type("str") else df[i] for i, c in enumerate(columns)}

        return get_json_result(data=df)
    except Exception as e:
        return get_json_result(data={}, retcode=100, retmsg=e)


@manager.route("/host_compose_dag", methods=['POST'])
@check_license
@validate_request("fake_model_info", "component_list", "job_content")
def host_compose_dag():
    fake_model_info = request.json["fake_model_info"]
    cpn_nm_lst = request.json["component_list"]
    publish_model.composeDAG(request.json["job_content"], "host", fake_model_info, config.local_party_id, cpn_nm_lst)
    return get_json_result(data=True)
