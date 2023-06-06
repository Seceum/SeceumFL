from flask import request

from fate_flow.settings import stat_logger
from fate_flow.utils.api_utils import get_json_result
from fate_flow.web_server.db.db_models import StudioModelInfoExtend
from fate_flow.web_server.db_service.model_service import ModelInfoExtendService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.common_util import model_id_get_hosts, pull_approval_result
from fate_flow.web_server.utils.enums import APPROVEChineseEnum
from fate_flow.web_server.utils.migrate_util import migration


@manager.route('/<role>/<src_party_id>/delete_model/<username>', methods=['POST'])
def delete_model(role,src_party_id,username):
    request_data = request.json
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    filters = [ModelInfoExtendService.model.id == model_id, ModelInfoExtendService.model.version == model_version,
               ModelInfoExtendService.model.role_type == role]
    ModelInfoExtendService.filter_delete(filters)
    return get_json_result(data=True)

@manager.route('/<role>/<src_party_id>/query_model/<username>', methods=['POST'])
def query_model(role,src_party_id,username):
    request_data = request.json
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    if ModelInfoExtendService.get_or_none(**{"id": model_id, "version": model_version}):
        return get_json_result(data=True)
    else:
        return get_json_result(retcode=100,retmsg="合作方没有对应模型")

@manager.route('/<role>/<src_party_id>/approval_do/<username>', methods=['POST'])
def approval_do(role,src_party_id,username):
    model_id = request.json["model_id"]
    model_version = request.json["model_version"]
    hosts = model_id_get_hosts(model_id)
    retcode, retmsg, host_approval_response = pull_approval_result(model_id, model_version, hosts)
    if retcode:
        return get_json_result(data=False, retcode=100, retmsg=retmsg)
    try:
        approval_num = 1
        for host_id, data in host_approval_response.items():
            if data["approve_result"] is not None:
                approval_num += 1
        StudioModelInfoExtend.update(approve_progress=int((approval_num / len(host_approval_response)) * 100)).where(
            StudioModelInfoExtend.id == model_id,
            StudioModelInfoExtend.version == model_version,
            StudioModelInfoExtend.role_type == "guest").execute()
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retcode=100, retmsg=str(e))

@manager.route('/<role>/<src_party_id>/release_do/<username>', methods=['POST'])
def release_do(role,src_party_id,username):
    request_data = request.json
    if "src_role" in request_data:
        del request_data["src_role"]
    if "src_party_id" in request_data:
        del request_data["src_party_id"]
    if "dest_party_id" in request_data:
        del request_data["dest_party_id"]
    if request_data.get("src_fate_ver"):
        del request_data["src_fate_ver"]
    try:
        ModelInfoExtendService.update_by_key(**request_data)
        return get_json_result(data=True)
    except Exception as e:
        return get_json_result(data=False, retcode=100, retmsg=str(e))

@manager.route("/host_approval_result", methods=["POST"])
def host_approval_result():
    request_data = request.json
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    role_type = request_data["role_type"]
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
        return get_json_result(data=data)
    return get_json_result(data=False, retcode=100, retmsg="没有对应model_id,model_version")

@manager.route('/export/do', methods=['POST'])
def export_do():
    """模型导出export_do"""
    request_data = request.json
    retcode, retmsg, data = migration(request_data)
    return get_json_result(retcode=retcode, retmsg=retmsg, data=data)

@manager.route("/model_update_status", methods=["POST"])
def model_update_status():
    """定时任务，模型发布，修改是否发布成功"""
    request_data = request.json
    model_id = request_data["model_id"]
    model_version = request_data["model_version"]
    role_type = request_data["role_type"]
    party_id = request_data["party_id"]
    update = {"status": request_data["status"]}
    user = "{}-{}".format("out_party_id", request_data["src_party_id"])
    try:
        ModelInfoExtendService.update_by_key(model_id, model_version, role_type, party_id, user, **update)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retcode=100, retmsg=str(e))