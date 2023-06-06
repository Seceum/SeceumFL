from flask import request
from flask_login import login_required

from fate_flow.web_server.db.db_models import StudioProjectInfo
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.log.log_utils import Log_seceum_audit
from fate_flow.web_server.utils.reponse_util import get_json_result


@manager.route("/audit", methods=['POST'])
@login_required
@validate_request("job_id")
def audit():
    """审计日志"""
    if request.json["job_id"] in StudioProjectInfo.get_auth_jobs():
        log_audit = Log_seceum_audit(request.json["job_id"])
        audit_path = log_audit.get_log_file_path()
        if audit_path:
            data = log_audit.cat_log()
            return get_json_result(data=data)
    return get_json_result(retcode=100, data=False, retmsg="任务id不存在")
