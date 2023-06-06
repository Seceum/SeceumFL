
from flask import request

from fate_flow.utils.api_utils import get_json_result
from fate_flow.web_server.db.db_models import StudioProjectActivationCode, StudioProjectInfo


@manager.route('/<role>/<src_party_id>/verify_project_activation_code_do/<username>', methods=['POST'])
def verify_project_activation_code_do(role,src_party_id,username):
    request_data = request.json
    project_id = request_data["project_id"]
    project_activation_code = request_data["project_activation_code"]
    party_id=src_party_id
    obj = StudioProjectInfo.query(id=project_id,project_activation_code=project_activation_code).first()
    if obj and obj.project_activation_code == project_activation_code:
        return get_json_result(data=True)
    else:
        return get_json_result(retmsg="验证失败", data=[], retcode=100)

@manager.route('/<role>/<src_party_id>/project_activation_code_is_verify/<username>', methods=['POST'])
def project_activation_code_is_verify(role,src_party_id,username):
    request_data = request.json
    project_id = request_data["project_id"]
    party_id=src_party_id
    if StudioProjectActivationCode.query(project_id=project_id,party_id=party_id).first():
        return get_json_result(data=True)
    else:
        return get_json_result(retmsg="项目未验证，或刷新验证码，重新验证", data=[], retcode=100)

@manager.route('/<role>/<src_party_id>/delete_project/<username>', methods=['POST'])
def delete_project(role,src_party_id,username):
    request_data = request.json
    project_id = request_data["project_id"]
    StudioProjectInfo.delete().where(StudioProjectInfo.id == project_id).execute()
    return get_json_result(data=True)

