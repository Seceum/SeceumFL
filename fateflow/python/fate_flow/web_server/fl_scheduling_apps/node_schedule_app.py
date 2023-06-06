from threading import Thread

from flask import request, after_this_request

from fate_flow.utils.api_utils import get_json_result
from fate_flow.web_server.db.ras_manage import RsaKeyManager
from fate_flow.web_server.db_service.model_service import ModelInfoExtendService
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.fl_config import PARTY_ID
from fate_flow.web_server.utils.enums import SiteKeyName
from fate_flow.web_server.utils.node_util import add_rollsite_node


@manager.route('/<role>/<src_party_id>/verify_node_public_key/<username>', methods=['POST'])
def verify_node_public_key(role,src_party_id,username):
    request_data = request.json
    public_key = request_data["host_public_key"]
    host_eggroll_ip=request_data["predict_party_ip"]
    host_eggroll_port=request_data["predict_port"]
    party_id = request_data["id"]
    data = RsaKeyManager.get_key(PARTY_ID,
                                 key_name= SiteKeyName.PUBLIC.value)
    if data==public_key:
        if request_data["command"]=="add":
            PartyInfoService.delete_by_id(party_id)
            PartyInfoService.save(**request_data)
        elif request_data["command"]=="update":
            PartyInfoService.update_by_id(party_id,request_data)
        t = Thread(target=add_rollsite_node,kwargs={"party_id":party_id,"rollsite_ip":host_eggroll_ip,"rollsite_port":host_eggroll_port,"command":"restart"})
        t.start()
        # add_rollsite_node(party_id, host_eggroll_ip, host_eggroll_port)
        return get_json_result(data=True)
    else:
        return get_json_result(data=False)
