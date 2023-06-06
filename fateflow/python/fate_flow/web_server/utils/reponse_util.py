import json
import re
from functools import wraps
from flask import session
import flask
from flask_login import current_user
from chain.common.util import store_send, chain_logger
from fate_flow.entity import RetCode
from flask import make_response, jsonify, request
from fate_flow.web_server.db.db_models import StudioEventHistory, StudioProjectInfo, \
    StudioProjectUser
from fate_flow.web_server.db_service.event_service import EventService
from fate_flow.web_server.fl_config import url_code_dict, config
from cache3 import SafeCache
from fate_flow.web_server.utils.common_util import url_code, get_uuid

cache = SafeCache()


def get_json_result(retcode=RetCode.SUCCESS, retmsg='success', data=None):
    # fate_reg = re.compile(re.escape('fate'), re.IGNORECASE)
    # if isinstance(retmsg, str):
    #     retmsg = fate_reg.sub('seceum', retmsg)
    response = {"retcode": retcode, "retmsg": retmsg, "data": data}
    request_chain(response, retcode)
    return jsonify(response)


def request_chain(response, retcode,input_arguments=None,is_chain=config.is_chain):
    user_id = None
    user_name = None
    if hasattr(current_user, "id"):
        user_id = current_user.id
        user_name = current_user.username
    code, url_name = url_code(flask.request.url_rule.rule)

    if code:
        if not input_arguments:
            input_arguments = get_input_arguments(url_name)
        if code == url_code_dict["/v1/approve/status"]:
            # 1授权同意，2授权拒绝，3取消授权 3060表示削权
            if input_arguments["操作"] == 3:
                code = "3060"
        # 审记日志上链
        chain_ret = None
        if is_chain:
            event_chain_obj = EventService.query(chain=True, code=code).first()
            if event_chain_obj:
                data = {
                    "event_class": event_chain_obj.p_name,
                    "event_sub_class": event_chain_obj.name,
                    "user_id": user_id,
                    "user_name": user_name,
                    "session_id": session.get("_id", ""),
                    # "client_ip": flask.request.remote_addr,
                    "event_detail": str(input_arguments),
                }
                if retcode != RetCode.SUCCESS:
                    data["event_is_success"] = "failed"
                    data["event_ret"] = str(response)
                try:
                    data["event_is_success"] = "success"
                    response_api = store_send({"data": str(data)})
                    if response_api["state"] == 200:
                        chain_ret = response_api["data"]
                    else:
                        chain_logger.error(str(response_api) + str(data))
                except Exception as e:
                    chain_logger.error(str(e) + str(data))

        # 审记日志到数据库
        event_log_obj = EventService.query(log=True, code=code).first()
        if event_log_obj:
            data = {
                "id": get_uuid(),
                "event_class": event_log_obj.p_name,
                "event_sub_class": event_log_obj.name,
                "user_id": user_id,
                "user_name": user_name,
                "session_id": session.get("_id", ""),
                "client_ip": flask.request.remote_addr,
                "event_detail": json.dumps(input_arguments),
                "is_chain": event_log_obj.chain,
                "chain_ret": chain_ret
            }
            if retcode != RetCode.SUCCESS:
                data["event_ret"] = json.dumps(response)
                data["event_is_success"] = "failed"
            else:
                data["event_ret"] = {}
                data["event_is_success"] = "success"
            StudioEventHistory(**data).save(force_insert=True)


def get_input_arguments(url_name):
    input_arguments = flask.request.json or flask.request.form.to_dict() or flask.request.args
    if url_name == '/v1/user/login':
        input_arguments = {"登录名": input_arguments.get("username")}
    elif url_name == '/v1/canvas/save':
        input_arguments = {
            "任务命令": input_arguments.get("command"),
            "任务名称": input_arguments.get("job_name"),
            "任务类型": input_arguments.get("job_type"),
            "项目名称": input_arguments.get("project_name")
        }
    elif url_name == "/v1/user/setting":
        input_arguments = {"昵称": input_arguments.get("nickname")}
    elif url_name == "/v1/user/add":
        input_arguments = {"昵称": input_arguments.get("nickname")}
    elif url_name == "/v1/user/delete":
        input_arguments = {"用户ids": input_arguments.get("user_ids")}
    elif url_name == "/v1/user/edit/*":
        input_arguments = {
            "昵称": input_arguments.get("nickname"),
            "用户名": input_arguments.get("username"),
            "项目ID": input_arguments.get("team_id"),
            "角色ID": input_arguments.get("role_id"),
            "权限码": input_arguments.get("permission_codes"),
            "请求路径": str(flask.request.path)
        }
    elif url_name == "/v1/node/add":
        input_arguments = {
            "节点编号": input_arguments.get("id"),
            "节点名称": input_arguments.get("party_name"),
            "合作节点公钥": input_arguments.get("public_key"),
            "本方IP地址": input_arguments.get("train_party_ip"),
            "本方端口": input_arguments.get("train_port"),
            "合作方IP地址": input_arguments.get("predict_party_ip"),
            "合作方端口": input_arguments.get("predict_port"),
            "联系人": input_arguments.get("contact_person"),
            "联系电话": input_arguments.get("contact_phone"),
            "邮箱": input_arguments.get("contact_email"),
            "描述": input_arguments.get("comments")
        }
    elif url_name == "/v1/node/edit/*":
        input_arguments = {
            "节点编号": input_arguments.get("id"),
            "节点名称": input_arguments.get("party_name"),
            "合作节点公钥": input_arguments.get("public_key"),
            "本方IP地址": input_arguments.get("train_party_ip"),
            "本方端口": input_arguments.get("train_port"),
            "合作方IP地址": input_arguments.get("predict_party_ip"),
            "合作方端口": input_arguments.get("predict_port"),
            "联系人": input_arguments.get("contact_person"),
            "联系电话": input_arguments.get("contact_phone"),
            "邮箱": input_arguments.get("contact_email"),
            "描述": input_arguments.get("comments"),
            "请求路径": str(flask.request.path)
        }
    elif url_name == "/v1/node/delete/*":
        input_arguments = {"请求路径": str(flask.request.path)}
    elif url_name == "/v1/role/add":
        input_arguments = {
            "角色名称": input_arguments.get("name"),
            "描述": input_arguments.get("comments"),
            "功能权限": input_arguments.get("permission_codes")
        }
    elif url_name == "/v1/role/edit":
        input_arguments = {
            "角色名称": input_arguments.get("name"),
            "描述": input_arguments.get("comments"),
            "功能权限": input_arguments.get("permission_codes"),
            "角色ID": input_arguments.get("role_id")
        }
    elif url_name == "/v1/role/delete":
        input_arguments = {
            "角色ID": input_arguments.get("role_id"),
        }
    elif url_name == "/v1/own/add":
        if input_arguments.get("type") == "本地文件":
            input_arguments = {
                "样本名称": input_arguments.get("name"),
                "样本集类别": input_arguments.get("sample_type"),
                "数据源类型": input_arguments.get("type"),
                "文件路径": input_arguments.get("file_path"),
                "文件上传路径": input_arguments.get("file_upload")
            }
        elif input_arguments.get("type") == "MYSQL" or input_arguments.get("type") == "POSTGRESQL":
            input_arguments = {
                "样本名称": input_arguments.get("name"),
                "样本集类别": input_arguments.get("sample_type"),
                "数据源类型": input_arguments.get("type"),
                "IP地址": input_arguments.get("db_host"),
                "端口": input_arguments.get("db_port"),
                "数据库名称": input_arguments.get("db_database"),
                "用户名": input_arguments.get("db_username"),
                "表名": input_arguments.get("db_tablename"),
                "SQL": input_arguments.get("sql"),
                "描述": input_arguments.get("comments")
            }
        elif input_arguments.get("type") == "ORACLE":
            input_arguments = {
                "样本名称": input_arguments.get("name"),
                "样本集类别": input_arguments.get("sample_type"),
                "数据源类型": input_arguments.get("type"),
                "IP地址": input_arguments.get("db_host"),
                "端口": input_arguments.get("db_port"),
                "数据库名称": input_arguments.get("db_dsh"),
                "用户名": input_arguments.get("db_username"),
                "表名": input_arguments.get("db_tablename"),
                "描述": input_arguments.get("comments")
            }
        elif input_arguments.get("type") == "FLHIVE":
            input_arguments = {
                "样本名称": input_arguments.get("name"),
                "样本集类别": input_arguments.get("sample_type"),
                "数据源类型": input_arguments.get("type"),
                "IP地址": input_arguments.get("db_host"),
                "端口": input_arguments.get("db_port"),
                "数据库名称": input_arguments.get("db_database"),
                "用户名": input_arguments.get("db_username"),
                "表名": input_arguments.get("db_tablename"),
                "描述": input_arguments.get("comments")
            }
        elif input_arguments.get("type") == "HDFS":
            input_arguments = {
                "样本名称": input_arguments.get("name"),
                "样本集类别": input_arguments.get("sample_type"),
                "数据源类型": input_arguments.get("type"),
                "节点名称": input_arguments.get("node_name"),
                "文件路径": input_arguments.get("file_path"),
                "描述": input_arguments.get("comments")
            }
        elif input_arguments.get("type") == "HBASE":
            input_arguments = {
                "样本名称": input_arguments.get("name"),
                "样本集类别": input_arguments.get("sample_type"),
                "数据源类型": input_arguments.get("type"),
                "IP地址": input_arguments.get("db_host"),
                "端口": input_arguments.get("db_port"),
                "表名": input_arguments.get("db_tablename"),
                "描述": input_arguments.get("comments")
            }
    elif url_name == "/v1/own/on_off_line":
        input_arguments = {
            "样本ID": input_arguments.get("sample_id"),
            "操作": input_arguments.get("operate")
        }
    elif url_name == "/v1/own/edit_fields/*":
        input_arguments = {"请求路径": str(flask.request.path)}
    elif url_name == "/v1/approve/status":
        input_arguments = {
            "样本ID": input_arguments.get("sample_id"),
            "操作": input_arguments.get("operate")
        }
    elif url_name == "/v1/project/add":
        input_arguments = {
            "项目名称": input_arguments.get("project_name"),
            "参与成员": input_arguments.get("modelers"),
            "合作方": input_arguments.get("party_ids"),
            "描述": input_arguments.get("comments")
        }
    elif url_name == "/v1/project/edit/*":
        input_arguments = {
            "项目名称": input_arguments.get("project_name"),
            "参与成员": input_arguments.get("modelers"),
            "合作方": input_arguments.get("party_ids"),
            "描述": input_arguments.get("comments"),
            "请求路径": str(flask.request.path)
        }
    elif url_name == "/v1/project/delete/*":
        input_arguments = {"请求路径": str(flask.request.path)}
    elif url_name == "/v1/project/canvas_add":
        input_arguments = {
            "任务名称": input_arguments.get("job_name"),
            "任务类型": input_arguments.get("job_type"),
            "项目ID": input_arguments.get("project_id"),
        }
    elif url_name == "/v1/project/detail/delete":
        input_arguments = {
            "画布ID": input_arguments.get("canvas_id"),
            "任务名称": input_arguments.get("job_name"),
            "任务类型": input_arguments.get("job_type"),
            "项目名称": input_arguments.get("project_name")
        }
    elif url_name == "/v1/canvas/model_store":
        input_arguments = {
            "画布ID": input_arguments.get("canvas_id"),
            "模型名称": input_arguments.get("model_name"),
            "模型": input_arguments.get("module")
        }
    elif url_name == "/v1/model_manage/delete":
        input_arguments = {
            "模型ID": input_arguments.get("model_id"),
            "模型版本": input_arguments.get("model_version")
        }
    elif url_name == "/v1/model_manage/export/*":
        input_arguments = {
            "模型ID": input_arguments.get("model_id"),
            "模型版本": input_arguments.get("model_version"),
            "是否是参与方": input_arguments.get("is_join"),
        }
    elif url_name == "/v1/model_manage/release":
        input_arguments = {
            "模型ID": input_arguments.get("model_id"),
            "模型版本": input_arguments.get("model_version"),
            "模型名称": input_arguments.get("module_name"),
            "服务名称": input_arguments.get("service_name"),
            "申请理由": input_arguments.get("service_reason")
        }
    elif url_name == "/v1/model_manage/approval":
        input_arguments = {
            "模型ID": input_arguments.get("model_id"),
            "模型版本": input_arguments.get("model_version"),
            "审批": input_arguments.get("operate"),
            "审批意见:": input_arguments.get("operate_advise")
        }
    return input_arguments


def cors_reponse(retcode=RetCode.SUCCESS, retmsg='success', data=None, auth=None):
    result_dict = {"retcode": retcode, "retmsg": retmsg, "data": data}
    response_dict = {}
    for key, value in result_dict.items():
        if value is None and key != "retcode":
            continue
        else:
            response_dict[key] = value
    response = make_response(jsonify(response_dict))
    if auth:
        response.headers["Authorization"] = auth
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Method"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "Authorization"
    request_chain(response_dict, retcode)
    return response


def have_permission_code(*args):
    input_user_id = current_user.alternative_id
    permission_codes = cache.get(input_user_id)
    if not permission_codes:
        permission_codes = current_user.get_permission_code()
        cache.set(current_user.alternative_id, permission_codes, timeout=60 * 60 * 24 * 2)
    for arg in args:
        if arg not in permission_codes:
            return False
    return True


def validate_permission_code(*args):
    def wrapper(func):
        @wraps(func)
        def decorated_function(*_args, **_kwargs):
            try:
                input_user_id = current_user.alternative_id
            except:
                return get_json_result(retcode=401, retmsg="please login")
            permission_codes = cache.get(input_user_id)
            if not permission_codes:
                permission_codes = current_user.get_permission_code()
                cache.set(current_user.alternative_id, permission_codes, timeout=60 * 60 * 24 * 2)
            for arg in args:
                if arg not in permission_codes:
                    # 获取最新权限码
                    permission_codes = current_user.get_permission_code()
                    cache.set(current_user.alternative_id, permission_codes, timeout=60 * 60 * 24 * 2)
                    if arg not in permission_codes:
                        return get_json_result(data=False, retcode=401, retmsg="no permission_code")
            return func(*_args, **_kwargs)

        return decorated_function

    return wrapper


# def validate_project_id(project_id):
#     def wrapper(func):
#         @wraps(func)
#         def decorated_function(*_args, **_kwargs):
#             if project_id in current_user.get_auth_projects():
#                 return func(*_args, **_kwargs)
#             return get_json_result(data=False, retcode=100, retmsg="项目不存在")
#         return decorated_function
#     return wrapper
def validate_project_id(func):
    @wraps(func)
    def decorated_function(*_args, **_kwargs):
        if "project_id" in request.view_args:
            project_id = request.view_args["project_id"]
        else:
            input_arguments = flask.request.json or flask.request.form.to_dict()
            project_id = input_arguments["project_id"]
        if flask.request.url_rule.rule=="/v1/project/detail":
            if flask.request.json["is_join"]==1:
                obj =StudioProjectInfo.query(id=project_id).first()
                if obj:
                    if current_user.is_superuser or  StudioProjectUser.query(project_id=project_id,user_id=current_user.id,role_type="host").first(): #是admin or 用户在host_project_auth里:
                        return func(*_args, **_kwargs)
                    elif StudioProjectUser.query(project_id=project_id, role_type="host").first():
                        return get_json_result(data={"flag": False, "msg": "项目拥有者已存在，请向拥有者申请权限"})
                    else:  # 去认证，做为管理者
                        return get_json_result(data={"flag": True, "msg": "项目拥有者不存在，请输入激活码做为拥有者"})
                else:
                    return get_json_result(data=False, retcode=100, retmsg="guest 项目不存在")

        if project_id in current_user.get_auth_projects():
            return func(*_args, **_kwargs)
        return get_json_result(data=False, retcode=100, retmsg="项目不存在")
    return decorated_function


def validate_canvas_id(func):
    @wraps(func)
    def decorated_function(*_args, **_kwargs):
        if "canvas_id" in request.view_args:
            canvas_id = request.view_args["canvas_id"]
        else:
            input_arguments = flask.request.json or flask.request.form.to_dict()
            canvas_id = input_arguments["canvas_id"]
        if canvas_id in current_user.get_auth_canvas():
            return func(*_args, **_kwargs)

        return get_json_result(data=False, retcode=100, retmsg="画布不存在")

    return decorated_function
