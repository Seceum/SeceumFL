from datetime import datetime
from flask import request
import pandas as pd
from flask_login import login_required, current_user
from fate_flow.settings import stat_logger
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db.db_models import StudioPartyInfo
from fate_flow.web_server.db.ras_manage import RsaKeyManager
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.db_service.project_service import ProjectInfoService
from fate_flow.web_server.db_service.sample_service import SampleService
from fate_flow.web_server.fl_config import config, PARTY_ID
from fate_flow.web_server.utils.common_util import datetime_format
from fate_flow.web_server.utils.enums import StatusEnum, PartyPingStatusEnum, UserAuthEnum, NodeStatusEnum, \
    SampleStatusEnum, SiteKeyName, OwnerEnum
from fate_flow.web_server.utils.node_util import delete_rollsite_node, add_rollsite_node
from fate_flow.web_server.utils.socket_util import ping_status
from fate_flow.web_server.utils.reponse_util import get_json_result, validate_permission_code


@manager.route("/ping", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.SYSTEM.value, UserAuthEnum.SYSTEM_USER_NODE.value,
                          UserAuthEnum.SYSTEM_USER_NODE_PING.value)
def ping_node():
    """节点管理_ping节点"""
    request_data = request.json
    try:
        train_party_ip = request_data["train_party_ip"]
        train_port = request_data["train_port"]
        predict_party_ip = request_data["predict_party_ip"]
        predict_port = request_data["predict_port"]
        train_flag = ping_status(train_party_ip, train_port)
        predict_flag = ping_status(predict_party_ip, predict_port)
        if train_flag and predict_flag:
            msg = "success"
            data = True
        else:
            msg = "ping 网络不通"
            data = False
        return get_json_result(retmsg=msg, data=data)
    except:
        return get_json_result(retcode=100, retmsg="参数有误")

@manager.route("/list", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.SYSTEM.value,UserAuthEnum.SYSTEM_USER_NODE.value)
def node_list():
    """节点管理列表"""
    party_id = request.json.get("id")
    if party_id:
        party_df = pd.DataFrame(PartyInfoService.query(status=StatusEnum.VALID.value, id=party_id).dicts())
    else:
        party_df = pd.DataFrame(PartyInfoService.query(status=StatusEnum.VALID.value).dicts())
    if party_df.empty:
        return get_json_result(data=[])
    cooperate_project_count_dict = ProjectInfoService.sum_count_by_party()
    open_sample_count_dict = SampleService.sum_count_by_party(OwnerEnum.OTHER.value,StatusEnum.VALID.value)
    party_df["cooperate_project_count"] = party_df.id.apply(lambda x:cooperate_project_count_dict.get(x,0))
    party_df["open_sample_count"] = party_df.id.apply(lambda x:open_sample_count_dict.get(x,0))
    party_df["status"] = party_df["ping_status"]
    data = party_df.to_dict("records")
    return get_json_result(data=data)

@manager.route("/delete/<string:party_id>", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.SYSTEM.value, UserAuthEnum.SYSTEM_USER_NODE.value,
                          UserAuthEnum.SYSTEM_USER_NODE_DELETE.value)
def delete_node(party_id):
    """节点管理_删除"""
    try:
        num = PartyInfoService.update_by_id(party_id,
                                            {"status": NodeStatusEnum.IN_VALID.value, "updator": current_user.username})
        if not num:
            return get_json_result(data=False, retcode=100, retmsg=f'节点id{party_id}不存在')
        sample_filters = [SampleService.model.party_id == party_id]
        sample_update_dict = {"status": SampleStatusEnum.DELETE.value, "updator": current_user.username,
                              "publish_status": SampleStatusEnum.DELETE.value,
                              "update_time": datetime_format(datetime.now())}
        SampleService.filter_update(sample_filters, sample_update_dict)
        # delete_rollsite_node(party_id)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retcode=100, retmsg='删除失败')


@manager.route("/edit/<string:party_id>", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.SYSTEM.value, UserAuthEnum.SYSTEM_USER_NODE.value,
                          UserAuthEnum.SYSTEM_USER_NODE_UPDATE.value)
def edit_node(party_id):
    """节点管理_编辑节点"""
    request_data = request.json
    if not PartyInfoService.query(id=party_id):
        return get_json_result(retmsg=f'{party_id}节点不存在', data=False)
    can_edit_fields = [PartyInfoService.model.train_party_ip.name,
                       PartyInfoService.model.train_port.name,
                       PartyInfoService.model.predict_party_ip.name,
                       PartyInfoService.model.predict_port.name,
                       PartyInfoService.model.comments.name,
                       PartyInfoService.model.contact_email.name,
                       PartyInfoService.model.contact_person.name,
                       PartyInfoService.model.contact_phone.name,
                       PartyInfoService.model.public_key.name,
                       ]
    host_eggroll_ip = request_data["predict_party_ip"]
    host_eggroll_port = request_data["predict_port"]
    guest_eggroll_ip = request_data["train_party_ip"]
    guest_eggroll_port = request_data["train_port"]
    guest_eggroll_flag = ping_status(guest_eggroll_ip, guest_eggroll_port)
    host_eggroll_flag = ping_status(host_eggroll_ip, host_eggroll_port)
    if guest_eggroll_flag and host_eggroll_flag:
        request_data["ping_status"] = PartyPingStatusEnum.CONNECT.value
    else:
        return get_json_result(data=False, retmsg='网络不通', retcode=100)
    request_data = {}
    for k, v in request.json.items():
        if k in can_edit_fields:
            request_data[k] = v
    request_data["updator"] = current_user.username
    command_body = {"host_public_key": request_data["public_key"],
                    "public_key": RsaKeyManager.get_key(PARTY_ID,
                                                        key_name=SiteKeyName.PUBLIC.value),
                    "id": str(PARTY_ID), "creator": "out_%s" % PARTY_ID,
                    "party_name": "out_%s" % PARTY_ID,
                    "update_time": datetime_format(datetime.now()),
                    "updator": "out_%s" % PARTY_ID,
                    "predict_party_ip": guest_eggroll_ip,
                    "predict_port": guest_eggroll_port,
                    'ping_status': '正常',
                    "command": "update"
                    }
    PartyInfoService.update_by_id(party_id, request_data)
    return get_json_result(data=True)
    #flag, msg = add_rollsite_node(party_id, host_eggroll_ip, host_eggroll_port, command_body)
    # if flag:
    #     PartyInfoService.update_by_id(party_id, request_data)
    #     return get_json_result(data=True)
    # else:
    #     return get_json_result(data=False, retmsg=msg, retcode=100)


@manager.route("/add", methods=['POST'])
@login_required
@validate_request("id", "party_name", "public_key", "train_party_ip", "train_port", "predict_party_ip", "predict_port")
@validate_permission_code(UserAuthEnum.SYSTEM.value, UserAuthEnum.SYSTEM_USER_NODE.value,
                          UserAuthEnum.SYSTEM_USER_NODE_CREATE.value)
def add_node():
    """节点管理_新增节点"""
    request_data = request.json
    try:
        if request_data["id"].startswith("0"):
            return get_json_result(data=False, retmsg='节点编号输入应为数字', retcode=100)
        party_id = str(int(request_data["id"]))
        if party_id == int(config.local_party_id):
            return get_json_result(data=False, retmsg='本文节点编号%s,不能重复' % config.local_party_id, retcode=100)
    except:
        return get_json_result(data=False, retmsg='节点编号输入应为数字', retcode=100)
    if list(PartyInfoService.query(id=party_id, status=StatusEnum.VALID.value).dicts()):
        return get_json_result(data=False, retmsg='节点id已存在', retcode=100)
    party_name = request_data["party_name"]
    guest_eggroll_ip = request_data["train_party_ip"]
    guest_eggroll_port = request_data["train_port"]
    host_eggroll_ip = request_data["predict_party_ip"]
    host_eggroll_port = request_data["predict_port"]
    guest_eggroll_flag = ping_status(guest_eggroll_ip, guest_eggroll_port)
    host_eggroll_flag = ping_status(host_eggroll_ip, host_eggroll_port)
    if guest_eggroll_flag and host_eggroll_flag:
        request_data["ping_status"] = PartyPingStatusEnum.CONNECT.value
    else:
        return get_json_result(data=False, retmsg='网络不通', retcode=100)
    if list(PartyInfoService.query(party_name=party_name).dicts()):
        StudioPartyInfo.delete().where(StudioPartyInfo.party_name == party_name).execute()
    if list(PartyInfoService.query(id=party_id).dicts()):
        StudioPartyInfo.delete().where(StudioPartyInfo.id == party_id).execute()
    if list(PartyInfoService.query(predict_party_ip=host_eggroll_ip, predict_port=host_eggroll_port).dicts()):
        return get_json_result(retmsg="ip,端口已存在，不允许创建重复值", data=False, retcode=100)
    request_data["status"] = StatusEnum.VALID.value
    request_data["creator"] = current_user.username
    request_data["update_time"] = datetime_format(datetime.now())
    request_data["id"] = party_id
    command_body = {"host_public_key": request_data["public_key"],
                    "public_key": RsaKeyManager.get_key(PARTY_ID,
                                                        key_name=SiteKeyName.PUBLIC.value),
                    "id": str(PARTY_ID), "creator": "out_%s" % PARTY_ID,
                    "party_name": "out_%s" % PARTY_ID,
                    "create_time": datetime_format(datetime.now()),
                    "predict_party_ip": guest_eggroll_ip,
                    "predict_port": guest_eggroll_port,
                    "train_party_ip": host_eggroll_ip,
                    "train_port": host_eggroll_port,
                    'ping_status': '正常',
                    "command": "add"
                    }
    flag, msg = True, ""#add_rollsite_node(party_id, host_eggroll_ip, host_eggroll_port, command_body)
    if flag:
        if "rollsite_ip" in request_data:
            del request_data["rollsite_ip"]
        if "rollsite_port" in request_data:
            del request_data["rollsite_port"]
        PartyInfoService.save(**request_data)
        return get_json_result(data=True)
    else:
        return get_json_result(data=False, retmsg=msg, retcode=100)


@manager.route("/get_party_id", methods=['POST'])
@login_required
def get_party_id():
    """查本文方节点id"""
    return get_json_result(data={"party_id": config.local_party_id})
