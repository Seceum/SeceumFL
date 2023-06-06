import pandas as pd
from flask import request
from flask_login import login_required
from fate_flow.settings import stat_logger
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db_service.event_service import EventService, StudioEventHistoryService
from fate_flow.web_server.utils.permission_util import get_event_list
from fate_flow.web_server.utils.reponse_util import get_json_result


@manager.route("/query_event", methods=['POST'])
@login_required
def query_event():
    """查询事件"""
    data = {
        "data": [],
        "log_codes": [],
        "clain_codes": []
    }
    try:
        event_df = pd.DataFrame(
            EventService.get_all().dicts())
        if not event_df.empty:
            data["data"] = get_event_list(event_df)
            data["log_codes"] = event_df[event_df["log"] == True].code.tolist()
            data["chain_codes"] = event_df[event_df["chain"] == True].code.tolist()
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e), retcode=100)


@manager.route("/edit_event", methods=['POST'])
@login_required
@validate_request("type", "codes")
def edit_event():
    """修改事件"""
    EventService.update_event(request.json["type"], request.json["codes"])
    return get_json_result(data=True)


@manager.route("/query_history", methods=['POST'])
@login_required
def query_history():
    """查询历史"""
    try:
        data = {
            "event_class": [],
            "event_sub_class": [],
            "event_is_success": [],
            "user_name": [],
            "data": [],
        }
        event_history_df = pd.DataFrame(
            StudioEventHistoryService.get_all(reverse=True).limit(10000).dicts())
        if not event_history_df.empty:
            data["event_class"] = event_history_df.event_class.unique().tolist()
            data["event_sub_class"] = event_history_df.event_sub_class.unique().tolist()
            data["event_is_success"] = event_history_df.event_is_success.unique().tolist()
            data["user_name"] = event_history_df.user_name.unique().tolist()
            data["data"] = event_history_df.to_dict("records")
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e), retcode=100)
