from datetime import datetime
import pandas as pd
from flask import request
from flask_login import login_required, current_user
from fate_flow.settings import stat_logger
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db_service.auth_service import GroupService, UserService, RoleService, UserGroupService
from fate_flow.web_server.utils.common_util import datetime_format, get_uuid, get_format_time
from fate_flow.web_server.utils.df_apply import concat_col
from fate_flow.web_server.utils.enums import StatusEnum
from fate_flow.web_server.utils.reponse_util import get_json_result


@manager.route("/list", methods=['POST'])
@login_required
def team_list():
    """项目组列表"""
    cols = [GroupService.model.id.alias("team_id"), GroupService.model.name, GroupService.model.comments,
            GroupService.model.create_time]
    try:
        if current_user.is_superuser:
            df = pd.DataFrame(GroupService.get_all(cols=cols).dicts())
            df["can_operate"] = True
        else:
            df = pd.DataFrame(GroupService.get_by_user_id(current_user.id, cols).dicts())
            df["can_operate"] = True
        if df.empty:
            return get_json_result(data=[])
        df.sort_values(by='create_time', ascending=True, inplace=True)
        df.fillna("", inplace=True)
        data = df.to_dict("records")
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e))


@manager.route("/user", methods=['POST'])
@login_required
@validate_request("team_id")
def team_user():
    """项目组-用户"""
    team_id = request.json["team_id"]
    try:
        user_df = pd.DataFrame(UserService.query_by_team(team_id).dicts())
        if user_df.empty:
            return get_json_result(data=[])
        user_ids = user_df.user_id.unique().tolist()
        if not user_ids:
            return get_json_result(data=[])
        role_user_df = pd.DataFrame(RoleService.query_by_user_list(user_ids))
        if role_user_df.empty:
            user_df["roles"] = ""
            df = user_df
        else:
            role_user_df = role_user_df.groupby("user_id").apply(concat_col).reset_index(drop=True)
            df = user_df.merge(role_user_df, left_on="user_id", right_on="user_id", how="left")
        df.sort_values(by='create_time', ascending=False, inplace=True)
        df.fillna("", inplace=True)
        data = df.to_dict('records')
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e))


@manager.route("/add", methods=['POST'])
@login_required
@validate_request("name")
def team_add():
    """新建项目组"""
    name = request.json["name"]
    comments = request.json.get("comments", None)
    try:
        if GroupService.query(name=name):
            return get_json_result(data=False, retmsg='项目组名称已经存在', retcode=100)
        GroupService.save(**{"name": name, "comments": comments, "creator": current_user.username})
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='新建失败', retcode=100)


@manager.route("/edit", methods=['POST'])
@login_required
@validate_request("team_id")
def team_edit():
    """编辑项目组"""
    name = request.json.get("name")
    comments = request.json.get("comments")
    team_id = request.json["team_id"]
    if not name and not comments:
        return get_json_result(data=True, retmsg='没有改动内容', retcode=100)
    try:
        update_data =dict()
        update_data["updator"] = current_user.username
        update_data["comments"] = comments
        if name:
            update_data["name"] = name
        GroupService.update_by_id(team_id, update_data)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='编辑失败', retcode=100)


@manager.route("/delete", methods=['POST'])
@login_required
@validate_request("team_id")
def team_delete():
    """删除项目组"""
    team_id = request.json["team_id"]
    try:
        user_group_df = pd.DataFrame(UserGroupService.query(group_id=team_id).dicts())
        user_ids = [] if user_group_df.empty else user_group_df.user_id.dropna().unique().tolist()
        user_update_dict = {"status": StatusEnum.IN_VALID.value, "updator": current_user.username,
                            "update_time": datetime_format(datetime.now())}
        GroupService.total_delete(team_id, user_ids, user_update_dict)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='删除失败', retcode=100)


@manager.route("/user/delete", methods=['POST'])
@login_required
@validate_request("origin_team_id", "user_ids")
def user_delete():
    """删除项目组中的用户"""
    origin_team_id = request.json["origin_team_id"]
    user_ids = list(set(request.json["user_ids"]))
    try:
        UserGroupService.user_delete(origin_team_id, user_ids)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='移动失败', retcode=100)


@manager.route("/user/move", methods=['POST'])
@login_required
@validate_request("origin_team_id", "target_team_id", "user_ids")
def user_move():
    """用户移动项目组"""
    origin_team_id = request.json["origin_team_id"]
    target_team_id = request.json["target_team_id"]
    user_ids = list(set(request.json["user_ids"]))
    try:
        UserGroupService.user_move(target_team_id, origin_team_id, user_ids, current_user.username)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='移动失败', retcode=100)


@manager.route("/user/copy", methods=['POST'])
@login_required
@validate_request("target_team_id", "user_ids")
def user_copy():
    """用户复制至项目组"""
    target_team_id = request.json["target_team_id"]
    user_ids = list(set(request.json["user_ids"]))
    creator = current_user.username
    create_time = get_format_time()
    try:
        filters = [UserGroupService.model.group_id == target_team_id]
        user_group_objs = UserGroupService.filter_scope_list("user_id", user_ids, filters=filters)
        exist_user_id = [user_group_obj.user_id for user_group_obj in user_group_objs]
        copy_user_id = set(user_ids).difference(set(exist_user_id))
        if not copy_user_id:
            return get_json_result(data=True)
        user_group_list = []
        for user_id in copy_user_id:
            user_group_list.append({
                "id": get_uuid(),
                "user_id": user_id,
                "group_id": target_team_id,
                "creator": creator,
                "create_time": create_time
            })
        if user_group_list:
            UserGroupService.insert_many(user_group_list)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg='复制移动失败', retcode=100)
