from flask import request
from flask_login import login_required

from fate_flow.utils.api_utils import validate_request
from fate_flow.web_server.utils.monitor_util import request_grafana, cf
from fate_flow.web_server.utils.reponse_util import get_json_result

cookies = ""


@manager.route("/query_range", methods=["POST"])
@validate_request("query", "start", "end", "step")
@login_required
def grafana_query_range():
    """查询事件"""
    global cookies
    request_data = request.json
    flag, data, cookies = request_grafana(request_data, cookies)
    if flag:
        return get_json_result(data=data)
    else:
        return get_json_result(data=[], retmsg=str(data), retcode=100)


@manager.route("/prometheus_instance", methods=["GET"])
@login_required
def prometheus_instance():
    """加载监控历史数据"""
    prometheus_instance = cf.get("prometheus_instance")
    if cf.get("prometheus_instance"):
        return get_json_result(data=prometheus_instance)
    return get_json_result(data=[], retmsg="服务未配置prometheus_instance", retcode=100)
