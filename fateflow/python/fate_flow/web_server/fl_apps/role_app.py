import pandas as pd
import numpy as np
from flask import request
from flask_login import login_required, current_user
from fate_flow.settings import stat_logger
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db_service.auth_service import RoleService, RolePermissionService, PermissionService, \
    UserRoleService, UserPermissionService
from fate_flow.web_server.utils.common_util import get_uuid, get_format_time
from fate_flow.web_server.utils.permission_util import get_permission_list
from fate_flow.web_server.utils.reponse_util import get_json_result


@manager.route("/list", methods=['POST'])
@login_required
def role_list():
    """角色权限列表"""
    try:
        role_permission_list = []
        roles_df = pd.DataFrame(RolePermissionService.permission_list().dicts())
        if roles_df.empty:
            return get_json_result(data=[])
        permission_cols = [PermissionService.model.id, PermissionService.model.p_id, PermissionService.model.code,
                           PermissionService.model.name, PermissionService.model.menu_level]
        permission_df = pd.DataFrame(PermissionService.query(is_superuser_auth=False, cols=permission_cols).dicts())
        for role_name, role_df in roles_df.groupby("name"):
            code_list = roles_df.permission_code.dropna().unique().tolist()
            permission_df_copy = permission_df[:]
            permission_df_copy.loc[:, "auth"] = np.where(permission_df_copy.code.isin(code_list), True, False)
            role_dict = dict(role_df.to_dict("records")[0])
            del role_dict["permission_code"]
            role_dict["permission_list"] = get_permission_list(permission_df_copy)
            role_permission_list.append(role_dict)
        data = sorted(role_permission_list, key=lambda x: x["create_time"], reverse=True)
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e))


@manager.route("/down_list", methods=['POST'])
@login_required
def role_down_list():
    """角色下拉框列表"""
    try:
        cols = [RoleService.model.id.alias("role_id"), RoleService.model.name, RoleService.model.comments,
                RoleService.model.create_time]
        data = list(RoleService.get_all(cols=cols, reverse=False, order_by="create_time").dicts())
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e))


@manager.route("/permission", methods=['POST'])
@login_required
def role_permission():
    """初始化权限列表"""
    try:
        permission_cols = [PermissionService.model.id, PermissionService.model.p_id, PermissionService.model.code,
                           PermissionService.model.name, PermissionService.model.menu_level]
        permission_df = pd.DataFrame(PermissionService.query(is_superuser_auth=False, cols=permission_cols).dicts())
        data = get_permission_list(permission_df)
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e))


@manager.route("/add", methods=['POST'])
@login_required
@validate_request("name", "permission_codes")
def role_add():
    """新建角色"""
    request_data = request.json
    name = request_data["name"]
    permission_codes = set(request_data["permission_codes"])
    try:
        if RoleService.query(name=name):
            return get_json_result(data=False, retmsg='角色名称已存在', retcode=100)
        role_dict = {
            "id": get_uuid(),
            "name": name,
            "comments": request_data.get("comments"),
            "creator": current_user.username
        }
        RoleService.create_by_permission(role_dict, permission_codes, current_user.username)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='新建失败', retcode=100)


@manager.route("/delete", methods=['POST'])
@login_required
@validate_request("role_id")
def role_delete():
    """删除角色"""
    role_id = request.json["role_id"]
    try:
        if UserRoleService.query(role_id=role_id):
            return get_json_result(data=False, retmsg='该角色正在使用', retcode=100)
        RoleService.delete_by_id(role_id)
        RolePermissionService.filter_delete([RolePermissionService.model.role_id == role_id])
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='删除失败', retcode=100)


@manager.route("/edit", methods=['POST'])
@login_required
@validate_request("role_id", "permission_codes")
def role_edit():
    """编辑角色"""
    request_data = request.json
    role_id = request_data["role_id"]
    name = request_data.get("name")
    comments = request_data.get("comments")
    permission_codes = set(request_data["permission_codes"])
    try:
        role_update = {}
        if name:
            role_update["name"] = name
        if comments:
            role_update["comments"] = comments
        if role_update:
            role_update["updator"] = current_user.username
            role_update["update_time"] = get_format_time()
            RoleService.update_by_id(role_id, role_update)
        RolePermissionService.update_by_permission(role_id, permission_codes, current_user.username)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='编辑失败', retcode=100)


@manager.route("/query_permission", methods=['POST'])
@login_required
@validate_request("role_id")
def query_permission_list():
    """获取角色&用户权限列表"""
    role_id = request.json["role_id"]
    user_id = request.json.get("user_id")
    have_disable = int(request.json.get("have_disable", 0))
    data = {
        "permission_list": [],
        "user_permissions": [],
        "role_permissions": []
    }
    try:
        permission_cols = [PermissionService.model.id, PermissionService.model.p_id, PermissionService.model.code,
                           PermissionService.model.name, PermissionService.model.menu_level]
        permission_df = pd.DataFrame(
            PermissionService.query(is_superuser_auth=False, cols=permission_cols, reverse=True,
                                    order_by="create_time").dicts())
        role_permission_codes = set(
            [i.permission_code for i in RolePermissionService.permission_list(role_id=role_id)])
        if have_disable:
            permission_df.loc[:, "disabled"] = np.where(permission_df.code.isin(role_permission_codes), True,
                                                        False)
        data["role_permissions"] = role_permission_codes
        if user_id:
            user_role_objs = UserRoleService.query(user_id=user_id, role_id=role_id)
            if user_role_objs:
                data["user_permissions"] = list(
                    set([k.permission_code for k in UserPermissionService.query(user_id=user_id)]))
                data["user_permissions"].extend(data["role_permissions"])
                data["user_permissions"] = list(set(data["user_permissions"]))
        data["permission_list"] = get_permission_list(permission_df)
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e), retcode=100)
