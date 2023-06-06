import pandas as pd
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64
from flask import request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fate_flow.entity import RetCode
from fate_flow.settings import stat_logger
from fate_flow.utils.base_utils import get_fate_flow_directory
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db.db_models import StudioAuthGroup
from fate_flow.web_server.db_service.auth_service import UserService, RoleService, PermissionService, UserRoleService, \
    RolePermissionService, UserPermissionService, GroupService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.common_util import get_uuid, get_format_time
from fate_flow.web_server.utils.enums import StatusEnum
from fate_flow.web_server.utils.license_util import parse_license
from fate_flow.web_server.utils.reponse_util import cors_reponse, get_json_result, cache, request_chain
import os


@manager.route('/login', methods=['POST'])
@validate_request("username", "password")
def login():
    """用户登录"""
    username = request.json['username']
    password = request.json['password']
    if config.login_rsa:
        project_dir = get_fate_flow_directory()
        data_dir = os.path.join(project_dir, "python", "fate_flow", "web_server", "data")
        file_path = os.path.join(data_dir, "private.pem")
        rsa_key = RSA.importKey(open(file_path).read())
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)  # 创建用于执行pkcs1_v1_5加密或解密的密码
        try:
            password = cipher.decrypt(base64.b64decode(password), "解密失败")
            password = password.decode('utf-8')
        except:
            return get_json_result(data=False, retcode=100, retmsg='rsa解密失败')
    flag, license_msg = parse_license()
    if not flag:
        return cors_reponse(retcode=100, retmsg=license_msg, data=False)
    user = UserService.query_user(username, password)
    if user:
        if user.username != username:
            return get_json_result(data=False, retcode=100, retmsg='用户名或密码错误')
        response_data = {"nickname": user.nickname, "username": user.username,
                         "license_msg": license_msg, "is_red": False, "is_superuser": user.is_superuser}
        login_user(user)
        user.alternative_id = get_uuid()
        user.save()
        cache.set(user.alternative_id, user.get_permission_code(), timeout=60 * 60 * 24 * 2)
        remain_days = (datetime.strptime(license_msg, "%Y-%m-%d").date() - datetime.now().date()).days
        if remain_days == 0:
            response_data["is_red"] = True
            msg = "系统使用当天过期"
        elif remain_days < 3 * 30:
            response_data["is_red"] = True
            msg = "系统使用时间还剩{}天".format(remain_days)
        else:
            msg = "登录成功"
        return cors_reponse(data=response_data, auth=user.get_id(), retmsg=msg)
    else:
        return get_json_result(data=False, retcode=100, retmsg='用户名或密码错误')


@manager.route("/logout", methods=['POST', 'GET'])
@login_required
def log_out():
    """用户登出"""
    del cache[current_user.alternative_id]
    current_user.alternative_id = get_uuid()
    current_user.save()
    request_chain({"ret_code": RetCode.SUCCESS, "ret_msg": "success", "data": True}, RetCode.SUCCESS,
                  input_arguments={"登录名": current_user.username})
    logout_user()
    from fate_flow.utils.api_utils import get_json_result
    return get_json_result(data=True)


@manager.route("/setting", methods=["POST"])
@login_required
def setting_user():
    """账户设置"""
    # todo
    request_data = request.json
    if not request_data:
        return get_json_result(data=True, retmsg="无编辑内容")
    old_password = str(request_data["old_password"])
    new_password = str(request_data["new_password"])
    real_password = current_user.password
    if not check_password_hash(real_password, old_password):
        return get_json_result(data=False, retcode=100, retmsg='登录旧密码错误')
    update_dict = {
        "password": generate_password_hash(new_password),
        "updator": current_user.username,
        "alternative_id": get_uuid()
    }
    if request_data.get("nickname"):
        update_dict["nickname"] = request_data["nickname"]
    try:
        UserService.update_by_id(current_user.id, update_dict)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='设置失败', retcode=100)


@manager.route("/add", methods=["POST"])
@login_required
@validate_request("nickname", "username", "password", "team_id", "role_id")
def user_add():
    """用户管理_新增用户"""
    request_data = request.json
    request_data["creator"] = current_user.username
    user_id = get_uuid()
    creator = current_user.username
    create_time = get_format_time()
    user_dict = {
        "id": user_id,
        "username": request_data["username"],
        "nickname": request_data["nickname"],
        "password": generate_password_hash(request_data["password"]),
        "is_superuser": False,
        "creator": creator,
        "create_time": create_time
    }
    team_user_list = []
    for group_id in request_data["team_id"]:
        team_user_list.append({
            "id": get_uuid(),
            "user_id": user_id,
            "group_id": group_id,
            "creator": creator,
            "create_time": create_time
        })
    role_user_list = [{
        "id": get_uuid(),
        "user_id": user_id,
        "role_id": role_id,
        "creator": creator,
        "create_time": create_time
    } for role_id in request_data["role_id"]]
    user_obj = UserService.query(username=request_data["username"])
    if user_obj:
        if user_obj[0].status == StatusEnum.VALID.value:
            return get_json_result(data=False, retmsg=f'登录名{request_data["username"]}已存在', retcode=100)
        else:
            return get_json_result(data=False, retmsg=f'登录名{request_data["username"]}已被系统占用', retcode=100)
    try:
        user_permission_list = []
        role_permission_codes = set(
            [i.permission_code for i in RolePermissionService.permission_list(role_id=request_data["role_id"])])
        for permission_code in list(set(request_data.get("permission_codes")) - role_permission_codes):
            user_permission_list.append({
                "id": get_uuid(),
                "user_id": user_id,
                "permission_code": permission_code,
                "creator": creator,
                "create_time": create_time
            })
        UserService.create_user(user_dict, team_user_list, role_user_list, user_permission_list)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg=str(e), retcode=100)


@manager.route("/delete", methods=["POST"])
@login_required
@validate_request("user_ids")
def delete_user():
    """用户管理_删除用户"""
    update_dict = {"status": StatusEnum.IN_VALID.value, "updator": current_user.username,
                   "update_time": get_format_time()}
    user_ids = request.json["user_ids"]
    if UserService.query(id=user_ids[0]).first().is_superuser:
        return get_json_result(data=False, retmsg='超級管理员不可删除', retcode=100)
    try:
        UserService.delete_user(user_ids, update_dict)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='删除失败', retcode=100)


@manager.route("/edit/<string:user_id>", methods=["POST"])
@login_required
def edit_user(user_id):
    """用户管理_编辑用户"""
    user_dict = {}
    team_list = []
    target_role_id_list = []
    if request.json.get("nickname"):
        user_dict["nickname"] = request.json["nickname"]
    if request.json.get("password"):
        user_dict["password"] = generate_password_hash(request.json["password"])
        user_dict["alternative_id"] = get_uuid()
    if request.json.get("team_id"):
        team_list = request.json["team_id"]
    if request.json.get("role_id"):
        target_role_id_list = request.json["role_id"]
    try:

        role_permission_codes = set(
            [i.permission_code for i in RolePermissionService.permission_list(role_id=target_role_id_list)])
        user_permission_list = list(set(request.json.get("permission_codes", [])) - role_permission_codes)
        UserService.update_user(user_id, user_dict, team_list, target_role_id_list, user_permission_list,
                                current_user.username)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='编辑失败', retcode=100)


@manager.route("/detail", methods=["POST"])
@login_required
@validate_request("user_id")
def user_detail():
    """用户管理_编辑用户展示详情"""
    user_id = request.json["user_id"]
    try:
        user_obj = UserService.get_or_none(id=user_id)
        if not user_obj:
            return get_json_result(data=[], retmsg="用户不存在", retcode=100)
        role_info_list = RoleService.query_by_user_list([user_id])
        role_id = [role_obj["role_id"] for role_obj in role_info_list] if role_info_list else []
        team_id_list = GroupService.get_by_user_id(user_id,
                                                   cols=[StudioAuthGroup.id]).execute()
        team_id = [group_obj.id for group_obj in team_id_list] if team_id_list else []
        data = {
            "user_id": user_id,
            "nickname": user_obj.nickname,
            "username": user_obj.username,
            "team_id": team_id,
            "role_id": role_id,
        }
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg="获取用户详情失败", retcode=100)


@manager.route("/auth", methods=["POST"])
@login_required
def auth():
    # 用户权限列表
    try:
        user_id = current_user.id
    except:
        return get_json_result(retcode=401, retmsg="please login")
    is_superuser = current_user.is_superuser
    cols = [PermissionService.model.id, PermissionService.model.p_id, PermissionService.model.code,
            PermissionService.model.name, PermissionService.model.menu_level, PermissionService.model.menu_level,
            PermissionService.model.url, PermissionService.model.img, PermissionService.model.is_superuser_auth]
    permission_df = pd.DataFrame(PermissionService.get_all(cols=cols).dicts())
    if not is_superuser:
        role_ids = list(set([user_role.role_id for user_role in UserRoleService.query(user_id=user_id)]))
        role_permission_codes = [role_permission.permission_code for role_permission in
                                 RolePermissionService.filter_scope_list("role_id", role_ids)]
        user_permission_codes = [user_permission.permission_code for user_permission in UserPermissionService.query(
            user_id=user_id)]
        all_permission_codes = set(role_permission_codes).union(set(user_permission_codes))
        permission_df = permission_df[(permission_df.code.isin(all_permission_codes)) & (
                permission_df.is_superuser_auth == False)]
    data = permission_df.to_dict("records")
    return get_json_result(data=data)


@manager.route("/verify_password", methods=["POST"])
@login_required
@validate_request("password")
def verify_password():
    # 验证用户密码
    if check_password_hash(str(current_user.password), request.json["password"]):
        return get_json_result(data=True)
    else:
        return get_json_result(data=False, retmsg="verify password error")
