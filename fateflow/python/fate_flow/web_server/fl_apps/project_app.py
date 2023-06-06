from datetime import datetime

import numpy as np

from flask import request
import pandas as pd
from collections import Counter
from flask_login import login_required, current_user
import random
import string
from fate_client.pipeline.constant import FederatedSchedulingStatusCode
from fate_flow.web_server.db.db_models import StudioSampleInfo, StudioVSampleInfo, StudioProjectInfo, \
    StudioProjectUser, StudioProjectSample, StudioAuthUser, StudioProjectParty, StudioProjectCanvas
from fate_flow.web_server.db_service.model_service import ModelInfoExtendService, ProjectUsedModelService
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.db_service.project_service import ProjectInfoService, ProjectUserService, \
    ProjectSampleService, ProjectPartyService, ProjectUsedSampleService, ProjectCanvasService
from fate_flow.web_server.db_service.job_service import JobContentService
from fate_flow.web_server.db_service.sample_service import SampleService, VSampleInfoService, SampleAuthorizeService, \
    SampleFieldsService
from fate_flow.web_server.db_service.auth_service import UserService, UserGroupService
from fate_flow.web_server.fl_scheduling_apps.fl_command import FL_Scheduler
from fate_flow.web_server.utils.common_util import get_uuid, model_can_remove, datetime_format, get_role_type

from fate_flow.web_server.utils.df_apply import concat_col, sample_can_remove
from fate_flow.web_server.utils.enums import RoleTypeEnum, StatusEnum, OwnerEnum, SampleTypeEnum, ApproveStatusEnum, \
    UserAuthEnum, SampleStatusEnum
from fate_flow.component_env_utils.env_utils import import_component_output_depend
from fate_flow.manager.data_manager import TableStorage
from fate_flow.operation.job_saver import JobSaver
from fate_flow.settings import stat_logger, ENGINES
from fate_flow.utils.api_utils import error_response, federated_api
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.utils.job_utils import get_component_output_tables_meta
from fate_flow.web_server.utils.df_apply import status_chinese_apply
from fate_flow.web_server.utils.reponse_util import get_json_result, have_permission_code, validate_permission_code, \
    validate_project_id, validate_canvas_id
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.license_util import check_license
from fate_flow.web_server.pipeline_wrapper import WrapperFactory
from fate_flow.utils.job_utils import generate_job_id
from fate_flow.web_server.pipeline_wrapper.canvas_jobs import update_canvas4hosts


@manager.route("/list", methods=['POST'])
@login_required
@validate_request("is_join")
@validate_permission_code(UserAuthEnum.PROJECT.value)
def project_list():
    """项目管理_我发起的、我参与的（前端分页）"""
    is_join = int(request.json["is_join"])
    role_type =get_role_type(is_join)
    if role_type==RoleTypeEnum.GUEST.value and not have_permission_code(UserAuthEnum.PROJECT_GUEST.value):
        return get_json_result(retcode=100, retmsg="no permission_code")
    elif role_type==RoleTypeEnum.HOST.value and not have_permission_code(UserAuthEnum.PROJECT_HOST.value):
        return get_json_result(retcode=100, retmsg="no permission_code")

    cols = [ProjectInfoService.model.id.alias("project_id"), ProjectInfoService.model.name.alias("project_name"),
            ProjectInfoService.model.comments, ProjectInfoService.model.creator,
            ProjectInfoService.model.guest_party_id, ProjectInfoService.model.create_time,ProjectInfoService.model.project_activation_code,ProjectInfoService.model.host_own,ProjectInfoService.model.host_own_id]
    project_df = pd.DataFrame(ProjectInfoService.query(status=StatusEnum.VALID.value, role_type=role_type,
                                                       cols=cols).dicts())
    current_user_id = current_user.id
    if project_df.empty: return get_json_result(data=[])

    if not is_join:
        # as guest
        project_ids = project_df.project_id.unique().tolist()
        project_user_df = pd.DataFrame([project_user.to_dict() for project_user in ProjectUserService.filter_scope_list(
            "project_id", project_ids, cols=[ProjectUserService.model.project_id, ProjectUserService.model.user_id])])
        if current_user.is_superuser:
            df = project_df
        else:
            user_project_ids = project_user_df[project_user_df.user_id == current_user_id][
                "project_id"].dropna().unique().tolist() if not project_user_df.empty else []
            create_project_ids = project_df[project_df.creator == current_user.username]["project_id"].unique().tolist()
            auth_projects = user_project_ids + create_project_ids
            if not auth_projects:  return get_json_result(data=[])
            df = project_df[project_df.project_id.isin(auth_projects)]

        auth_project_id = df.project_id.unique().tolist()
        project_party_df = pd.DataFrame([project_party.to_dict() for project_party in
                                         ProjectPartyService.filter_scope_list("project_id", auth_project_id,
                                                                               cols=[
                                                                                   ProjectPartyService.model.project_id,
                                                                                   ProjectPartyService.model.party_id])])
        if project_party_df.empty:
            df["party_id"] = ""
            df["party_name"] = ""
        else:
            party_df = pd.DataFrame(PartyInfoService.get_all(cols=[PartyInfoService.model.id.alias("party_id"),
                                                                   PartyInfoService.model.party_name]).dicts())
            party_info_df = project_party_df.merge(party_df, left_on='party_id', right_on='party_id', how='inner')
            df = df.merge(party_info_df, left_on='project_id', right_on='project_id', how='left')

        if project_user_df.empty:
            df["user_id"] = ""
        else:
            user_df = pd.DataFrame([user_obj.to_dict() for user_obj in UserService.filter_scope_list("id",
                                                                                                     project_user_df.user_id.dropna().unique().tolist(),
                                                                                                     cols=[
                                                                                                         UserService.model.id,
                                                                                                         UserService.model.nickname])])
            user_df.rename(columns={"id": "user_id"}, inplace=True)
            if not user_df.empty and not project_user_df.empty:
                user_info_df = user_df.merge(project_user_df, left_on='user_id', right_on='user_id', how='inner')
                df = df.merge(user_info_df, left_on='project_id', right_on='project_id', how='left')

        df.rename(columns={"party_name": "partners", "user_id": "modeler_ids", "nickname": "modeler"}, inplace=True)
        create_user_df = pd.DataFrame([user_obj.to_dict() for user_obj in UserService.filter_scope_list(
            "username",
            df.creator.dropna().unique().tolist(),
            cols=[
                UserService.model.nickname,
                UserService.model.username])])
        create_user_df.rename(columns={"nickname": "creator_nickname"}, inplace=True)
        df = df.merge(create_user_df, left_on='creator', right_on='username', how='left')

        df = df.groupby(df["project_id"]).apply(concat_col).reset_index(drop=True)
    else:
        # as parterner
        if current_user.is_superuser:
            project_df = project_df
        else:
            auth_project_ids = [i["project_id"] for i in
                                StudioProjectUser.select().where(
                                    StudioProjectUser.user_id == current_user.id).dicts()]
            project_df = project_df[
                (project_df['host_own'] == False) | (project_df['project_id'].isin(auth_project_ids))]
        guest_ids = list(set(project_df.guest_party_id.tolist()))
        party_cols = [PartyInfoService.model.id, PartyInfoService.model.party_name]
        party_df = pd.DataFrame(
            [i.to_dict() for i in PartyInfoService.filter_scope_list("id", guest_ids, cols=party_cols)])
        if party_df.empty:
            df = project_df
            df["guest_party_name"] = ""
        else:
            party_df.rename(columns={"id": "guest_party_id", "party_name": "guest_party_name"}, inplace=True)
            df = project_df.merge(party_df, left_on='guest_party_id', right_on='guest_party_id', how='left')
        create_user_df = pd.DataFrame(StudioAuthUser.select(StudioAuthUser.id, StudioAuthUser.nickname
                                                            ).dicts())
        df = df.merge(create_user_df, left_on='host_own_id', right_on='id', how='left')
    # check out if executed
    cnvs = pd.DataFrame([p.to_dict() for p in ProjectCanvasService.filter_scope_list("project_id", list(df["project_id"]),
                                                               cols=[ProjectCanvasService.model.id,
                                                                     ProjectCanvasService.model.project_id
                                                                     ])
                         ])
    if cnvs.empty:
        df["exec_total"] = 0
        df.drop_duplicates(inplace=True)
        df.fillna('', inplace=True)
        df.sort_values(by='create_time', ascending=False, inplace=True)
        return get_json_result(data=df.to_dict(orient="records"))

    jbs = pd.DataFrame(dict(Counter([j.canvas_id for j in \
                        JobContentService.filter_scope_list("canvas_id", list(set(cnvs["id"])),
                                                            cols=[JobContentService.model.canvas_id])])),
                       index=["exec_count"]
                       ).T
    jbs.index.name = "cid"
    jbs.reset_index(inplace=True)
    cnvs = cnvs.merge(jbs, left_on='id', right_on='cid', how='left').fillna(0)
    proj_cnt = cnvs[["project_id", "exec_count"]].groupby(["project_id"])["exec_count"].sum()
    df = df.merge(proj_cnt.reset_index(), left_on='project_id', right_on="project_id", how='left').drop_duplicates()
    df["exec_count"].fillna(0, inplace=True)
    df["exec_total"] = df["exec_count"].astype(int)
    for c in ["exec_count"]:del df[c]

    df.drop_duplicates(inplace=True)

    df.fillna('', inplace=True)
    df.sort_values(by='create_time', ascending=False, inplace=True)
    df["is_own"] = df["host_own_id"].apply(lambda x:x==current_user.id)
    return get_json_result(data=df.to_dict(orient="records"))


@manager.route("/query_modeler", methods=['POST'])
@login_required
def query_modeler():
    """项目管理_我发起的_新建项目_查询建模人员"""
    project_id = request.json.get("project_id") if request.json else None
    user_cols = [UserService.model.id, UserService.model.username, UserService.model.nickname]
    current_user_id = current_user.id
    if project_id:
        project_obj = ProjectInfoService.get_or_none(id=project_id)
        if not project_obj:
            return get_json_result(data=False, retcode=100, retmsg='项目不存在')
        current_user_id = UserService.get_or_none(username=project_obj.creator).id
    else:
        project_obj = None
    if current_user.is_superuser:
        user_df = pd.DataFrame(UserService.query(status=StatusEnum.VALID.value, cols=user_cols).dicts())
    else:
        team_ids = [i.group_id for i in UserGroupService.query(user_id=current_user_id)]
        user_ids = [user_group.user_id for user_group in UserGroupService.filter_scope_list("group_id", team_ids)]

        user_df = pd.DataFrame(user_obj.to_dict() for user_obj in UserService.filter_scope_list("id", user_ids,
                                                                                                filters=[
                                                                                                    UserService.model.status == StatusEnum.VALID.value],
                                                                                                cols=user_cols))
    if user_df.empty:
        return get_json_result(data=[])
    if project_obj:
        remove_user = project_obj.creator
        user_df = user_df[user_df.username != remove_user]
        is_selected_used = [i.user_id for i in ProjectUserService.query(project_id=project_id)]
        user_df["is_selected"] = np.where(user_df.id.isin(is_selected_used), True, False)
    else:
        user_df = user_df[user_df.id != current_user_id]
        user_df["is_selected"] = False
    user_df.sort_values(by='nickname', ascending=False, inplace=True)
    user_df.rename(columns={"id": "modeler_id", "nickname": "modeler_name"}, inplace=True)
    data = user_df.to_dict("records")
    return get_json_result(data=data)


@manager.route("/add", methods=['POST'])
@login_required
@validate_request("project_name", "party_ids")
@validate_permission_code(UserAuthEnum.PROJECT.value,UserAuthEnum.PROJECT_GUEST.value,UserAuthEnum.PROJECT_GUEST_CREATE.value)
def add_project():
    """项目管理_我发起的_新建项目"""
    request_data = request.json
    project_name = request_data["project_name"]
    comments = request_data.get("comments", "")
    modelers = request_data.get("modelers", [])
    party_ids = request_data["party_ids"]
    project_objs = ProjectInfoService.query(name=project_name)
    if project_objs:
        return get_json_result(data=False, retcode=100, retmsg='项目名称已存在')
    project_id = get_uuid()
    project_data = {
        "name": project_name,
        "role_type": RoleTypeEnum.GUEST.value,
        "status": StatusEnum.VALID.value,
        "creator": current_user.username,
        "comments": comments,
        "id": project_id,
        "project_activation_code":   ''.join(random.sample(string.ascii_letters + string.digits, 6))
    }
    try:
        ProjectInfoService.create_project(project_data, modelers, party_ids)
        error_info = {}
        for h in party_ids:
            ret = federated_api(job_id=generate_job_id(),
                                method='POST',
                                endpoint="/project/host_project_add",
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=h,
                                json_body={"project_id": project_id, "project_name": project_name,
                                           "project_comments": comments, "guest_party_id": config.local_party_id,
                                           "status": StatusEnum.VALID.value, "src_party_id": config.local_party_id
                                           },
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                stat_logger.error(f"{h}: {ret['retmsg']}")
                error_info[h] = ret["retmsg"]

        data = {"project_id": project_id, "project_name": project_name}
        retmsg = ""
        for h,msg in error_info.items(): retmsg += f"合作方（{h}）创建项目出错：{msg}！"
        return get_json_result(data=data, retmsg =retmsg)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=str(e), retcode=100, retmsg='创建失败')

@manager.route("/host_project_add", methods=['POST'])
@check_license
def host_training_run():
    req_data = request.json
    project_id = req_data["project_id"]
    project_name = req_data["project_name"]
    comments = req_data["project_comments"]
    guest_party_id = req_data["guest_party_id"]
    status = req_data["status"]
    user = "{}-{}".format("out_party_id", req_data["src_party_id"])
    if not ProjectInfoService.query(id=project_id):
        project_save_dict = {
            "id": project_id,
            "name": project_name,
            "comments": comments,
            "role_type": RoleTypeEnum.HOST.value,
            "guest_party_id": guest_party_id,
            "status": status,
            "creator": user
        }
        ProjectInfoService.save(**project_save_dict)
    return get_json_result(data=True)


@manager.route("/edit/<string:project_id>", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.PROJECT.value,UserAuthEnum.PROJECT_GUEST.value,UserAuthEnum.PROJECT_GUEST_UPDATE.value)
@validate_project_id
def edit_project(project_id):
    """项目管理_我发起的_编辑项目"""
    request_data = request.json
    if not request_data:
        return get_json_result(data=False, retcode=100, retmsg='没有更新内容')
    user_ids = request_data.get("modelers")
    party_ids = request_data.get("party_ids")
    comments = request_data.get("comments")
    if not ProjectInfoService.query(id=project_id):
        return get_json_result(data=False, retcode=100, retmsg=f'项目id{project_id}不存在')
    if comments is not None:
        ProjectInfoService.update_by_id(project_id, {"comments": comments})
    if user_ids:
        ProjectUserService.update_by_project(project_id, user_ids, current_user.username)
    elif isinstance(user_ids, (list, tuple)) and len(user_ids) == 0:
        ProjectUserService.filter_delete([ProjectUserService.model.project_id == project_id])
    if party_ids:
        ProjectPartyService.update_by_project(project_id, party_ids, current_user.username)
    elif isinstance(user_ids, (list, tuple)) and len(user_ids) == 0:
        ProjectPartyService.filter_delete([ProjectPartyService.model.project_id == project_id])
    return get_json_result(data=True)


@manager.route("/delete/<string:project_id>", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.PROJECT.value,UserAuthEnum.PROJECT_GUEST.value,UserAuthEnum.PROJECT_GUEST_DELETE.value)
@validate_project_id
def delete_project(project_id):
    """项目管理_我发起的_删除项目"""
    try:
        objs = StudioProjectParty.select().where(StudioProjectParty.project_id == project_id).execute()
        if len(objs) > 0:
            status_code, response = FL_Scheduler.project_command("delete_project", request.json,
                                                                 specific_para=[("host",[obj.party_id for obj in objs])])
            if status_code != FederatedSchedulingStatusCode.SUCCESS:
                return get_json_result(data=False, retcode=100, retmsg="删除失败")
        ProjectInfoService.delete_by_id(project_id)
        StudioProjectParty.delete().where(StudioProjectParty.project_id == project_id).execute()
        StudioProjectSample.delete().where(StudioProjectSample.project_id == project_id).execute()
        StudioProjectUser.delete().where(StudioProjectUser.project_id == project_id).execute()
        StudioProjectCanvas.delete().where(StudioProjectCanvas.project_id == project_id).execute()
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retcode=100, retmsg='删除失败')

@manager.route("/refresh_project_activation_code", methods=['POST'])
@login_required
@validate_request("project_id")
@validate_project_id
def refresh_project_activation_code():
    project_activation_code = get_uuid()
    StudioProjectInfo.update(project_activation_code=project_activation_code).where(StudioProjectInfo.id==request.json["project_id"]).execute()
    # StudioProjectActivationCode.delete().where(StudioProjectActivationCode.project_id==request.json["project_id"]).execute()
    return get_json_result()

@manager.route("/verify_project_activation_code", methods=['POST'])
@validate_request("project_id","project_activation_code")
@login_required
def verify_project_activation_code():
    request_data = request.json
    project_id = request_data["project_id"]
    project_activation_code = request_data["project_activation_code"]
    if StudioProjectUser.query(project_id=project_id,  role_type="host",is_own=True).first():
        return get_json_result(retcode=100,retmsg="拥有者已存在")


    obj = StudioProjectInfo.query(id=project_id).first()
    if obj:
        # if not current_user.is_superuser:
        party_id = obj.guest_party_id
        status_code, response = FL_Scheduler.project_command("verify_project_activation_code_do",request.json,
                                                             specific_para=[("guest", [party_id])])
        if status_code != FederatedSchedulingStatusCode.SUCCESS:
            return get_json_result(data=False, retcode=100, retmsg="验证失败")
        StudioProjectUser.insert({"id":get_uuid(),"project_id":project_id,"user_id":current_user.id,"is_own":True,"role_type":"host","create_time":datetime_format(datetime.now()),"creator":current_user.username,"project_activation_code":project_activation_code}).execute()
        StudioProjectInfo.update(host_own=True,host_own_id=current_user.id).where(StudioProjectInfo.id==project_id).execute()
    return get_json_result()

@manager.route("/host_project_as_owner", methods=['POST'])
@validate_request("project_id","user_id")
@login_required
def host_project_as_owner():
    request_data = request.json
    project_id = request_data["project_id"]
    user_id = request_data["user_id"]
    if StudioProjectUser.query(project_id=project_id, user_id=user_id, role_type="host", is_own=True).first():
        return get_json_result(retcode=100,retmsg="拥有者已存在")
    StudioProjectUser.insert(
        {"id": get_uuid(), "project_id": project_id, "user_id": user_id,
         "role_type": "host", "create_time": datetime_format(datetime.now()), "creator": current_user.username,"is_own":True
         }).execute()
    StudioProjectInfo.update(host_own=True, host_own_id=user_id).where(
        StudioProjectInfo.id == project_id).execute()
    return get_json_result()

@manager.route("/edit_host_project_user", methods=['POST'])
@validate_request("project_id","user_ids")
@login_required
def edit_host_project_user():
    request_data = request.json
    project_id = request_data["project_id"]
    user_ids = request_data["user_ids"]
    StudioProjectUser.delete().where(StudioProjectUser.project_id==project_id,StudioProjectUser.role_type=="host",StudioProjectUser.is_own==False).execute()
    for user_id in user_ids:
        StudioProjectUser.insert(
            {"id": get_uuid(), "project_id": project_id, "user_id": user_id,
             "role_type": "host", "create_time": datetime_format(datetime.now()), "creator": current_user.username
             }).execute()
    return get_json_result()

@manager.route("/get_host_project_user", methods=['POST'])
@validate_request("project_id")
@login_required
def get_host_project_user():
    request_data = request.json
    project_id = request_data["project_id"]
    is_selected_used = [i["user_id"] for i in
                        StudioProjectUser.select(StudioProjectUser.user_id).where(StudioProjectUser.project_id == project_id,
                                                                                  StudioProjectUser.is_own == False,
                                                                                  StudioProjectUser.role_type == "host").dicts()]
    if not is_selected_used:
        return get_json_result(data=[])
    user_df = pd.DataFrame(StudioAuthUser.query(status=StatusEnum.VALID.value, is_superuser=False,
                                                cols=[StudioAuthUser.id, StudioAuthUser.nickname]).dicts())
    user_df["is_selected"] = np.where(user_df.id.isin(is_selected_used), True, False)
    return get_json_result(data=user_df.to_dict("records"))

@manager.route("/detail", methods=['POST'])
@login_required
@validate_request("is_join", "project_id")
@validate_project_id
def project_detail():
    request_data = request.json
    is_join = int(request_data["is_join"])
    project_id = request_data["project_id"]

    project_canvas_df = pd.DataFrame(ProjectCanvasService.query(project_id=project_id, reverse=True,
                                                                order_by="create_time").dicts())
    if project_canvas_df.empty: return get_json_result(data=[])

    project_canvas_df.rename(columns={"id": "canvas_id"}, inplace=True)

    if not is_join: # as guest
        # get creator info
        create_user_df = pd.DataFrame([user_obj.to_dict() for user_obj in \
                                       UserService.filter_scope_list("username",
                                                                     project_canvas_df.creator.dropna().unique().tolist(),
                                                                     cols=[
                                                                         UserService.model.nickname,
                                                                         UserService.model.username
                                                                     ])
                                       ])
        create_user_df.rename(columns={"nickname": "creator_nickname"}, inplace=True)
        df = project_canvas_df.merge(create_user_df, left_on='creator', right_on='username', how='left')

        # get parterner info
        project_sample_party_df = pd.DataFrame(ProjectUsedSampleService.query(project_id=project_id,
                                                                              sample_type=SampleTypeEnum.ORIGIN.value,
                                                                              cols=[
                                                                                  ProjectUsedSampleService.model.project_id,
                                                                                  ProjectUsedSampleService.model.party_id]).dicts())
        if not project_sample_party_df.empty:
            all_party_ids = project_sample_party_df.party_id.unique().tolist()
            party_ids = list(filter(lambda x: x != config.local_party_id, all_party_ids))
            party_df = pd.DataFrame(
                PartyInfoService.get_by_ids(party_ids, cols=[PartyInfoService.model.id.alias("party_id"),
                                                             PartyInfoService.model.party_name]).dicts())
            if party_df.empty:
                df["party_id"] = ""
                df["party_name"] = ""
            else:
                project_party_df = project_sample_party_df.merge(party_df, left_on="party_id", right_on="party_id",
                                                                 how="inner")

                project_party_df = project_party_df.groupby(party_df["party_id"]).apply(concat_col).reset_index(drop=True)
                df = df.merge(project_party_df, left_on="project_id", right_on="project_id", how="left")
        else:
            df["party_id"] = ""
            df["party_name"] = ""
    else: # as host
        project_sample_party_df = pd.DataFrame(ProjectUsedSampleService.query(project_id=project_id,
                                                                              sample_type=SampleTypeEnum.ORIGIN.value,
                                                                              party_id=config.local_party_id,
                                                                              cols=[
                                                                                  ProjectUsedSampleService.model.canvas_id,
                                                                                  ProjectUsedSampleService.model.sample_id,
                                                                                  ProjectUsedSampleService.model.create_time
                                                                              ]
                                                                              ).dicts())
        if not project_sample_party_df.empty:
            # retain latest host sample that's been just used
            def latest_one(x):
                xx = x.sort_values(by='create_time', ascending=True)
                return xx.iloc[-1,:]
            project_sample_party_df = project_sample_party_df.groupby(project_sample_party_df["canvas_id"]).apply(latest_one).reset_index(drop=True)
            del project_sample_party_df["create_time"]

            sample_ids = project_sample_party_df.sample_id.unique().tolist()
            sample_df = pd.DataFrame([i.to_dict() for i in SampleService.filter_scope_list("id", sample_ids, cols=[
                SampleService.model.id, SampleService.model.name])])
            sample_df.rename(columns={"id": "sample_id", "name": "sample_name"}, inplace=True)
            project_sample_df = project_sample_party_df.merge(sample_df, left_on="sample_id", right_on="sample_id",
                                                              how="inner")

            # canvas_sample 去重，根据canvas_id 获取
            project_sample_df.drop_duplicates(subset=["canvas_id","sample_id"], keep='last', inplace=True)
            project_sample_df = project_sample_df.groupby(project_sample_df["canvas_id"]).apply(concat_col).reset_index(
                drop=True)
            df = project_canvas_df.merge(project_sample_df, left_on="canvas_id", right_on="canvas_id", how="left")
        else:
            df = project_canvas_df
            df["sample_id"] = ""
            df["sample_name"] = ""
        job_names = df.job_name.dropna().unique().tolist()
        model_filters = [ModelInfoExtendService.model.role_type == RoleTypeEnum.HOST.value, ModelInfoExtendService.model.project_id == project_id]
        job_name_list = [i.job_name for i in
                         ModelInfoExtendService.filter_scope_list("job_name", job_names, filters=model_filters,
                                                                  cols=[ModelInfoExtendService.model.job_name])]
        if job_name_list:
            job_name_count = dict(Counter(job_name_list))
            model_count_df = pd.DataFrame(job_name_count, index=["model_count"]).T
            model_count_df.index.name = "job_name"
            model_count_df.reset_index(inplace=True)
            df = df.merge(model_count_df, left_on="job_name", right_on="job_name", how='left')
            df["model_count"] = df["model_count"].fillna(0).astype(int)
        else:
            df["model_count"] = 0

    # checkout if executed before
    exec_list = [i.canvas_id for i in JobContentService.filter_scope_list("canvas_id", list(set(df["canvas_id"])),cols=[JobContentService.model.canvas_id])]
    if exec_list:
        cnt = pd.DataFrame(dict(Counter(exec_list)), index=["exec_count"]).T
        cnt.index.name = "cid"
        cnt.reset_index(inplace=True)
        df = df.merge(cnt, left_on="canvas_id", right_on="cid", how='left')
        df["exec_count"] = df["exec_count"].fillna(0).astype(int)
    else:
        df["exec_count"] = 0

    df = df.groupby(df["canvas_id"]).apply(concat_col).reset_index(drop=True)
    df.sort_values(by='create_time', ascending=False, inplace=True)
    df.fillna("", inplace=True)

    for c in ["canvas_content", "cid"]:
        if c in df.columns: del df[c]
    canvas_id = request_data.get("canvas_id")
    if canvas_id:
        df = df[df.canvas_id == canvas_id].reset_index(drop=True)
    return get_json_result(data=df.to_dict(orient="records"))


def delete_canvas(cid):
    JobContentService.filter_delete([JobContentService.model.canvas_id == cid])
    ProjectUsedSampleService.filter_delete([ProjectUsedSampleService.model.canvas_id == cid])
    ProjectUsedModelService.filter_delete([ProjectUsedModelService.model.canvas_id == cid])
    ProjectCanvasService.delete_by_id(cid)
    return True

@manager.route("/detail/delete", methods=['POST'])
@login_required
@validate_request("canvas_id")
@validate_permission_code(UserAuthEnum.PROJECT.value,UserAuthEnum.PROJECT_GUEST.value)
@validate_canvas_id
def project_detail_delete():
    """项目管理_我发起的_项目详情_任务删除"""
    canvas_id = request.json["canvas_id"]
    try:
        update_canvas4hosts(canvas_id, "/project/detail/host/delete", {"canvas_id": canvas_id})
        delete_canvas(canvas_id)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retcode=100, retmsg='删除失败')


@manager.route("/detail/host/delete", methods=['POST'])
@check_license
@validate_request("canvas_id")
def project_detail_delete4host():
    """项目管理_我发起的_项目详情_任务删除"""
    canvas_id = request.json["canvas_id"]
    try:
        delete_canvas(canvas_id)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retcode=100, retmsg='删除失败')


@manager.route("/sample", methods=['POST'])
@login_required
@validate_request("project_id")
@validate_project_id
def query_sample():
    """项目管理_我发起的、我参与的_项目详情_样本"""
    project_id = request.json["project_id"]
    cols = {StudioSampleInfo.id, StudioSampleInfo.name, StudioSampleInfo.party_id, StudioSampleInfo.party_name,
            StudioSampleInfo.status, StudioSampleInfo.owner, ProjectUsedSampleService.model.create_time}
    df = pd.DataFrame(list(ProjectUsedSampleService.join_by_sample(project_id, cols=cols).dicts()))
    if df.empty:
        return get_json_result(data=[])
    my_sample_df = df[df.owner == OwnerEnum.OWN.value].reset_index(drop=True)
    out_sample_df = df[(df.owner == OwnerEnum.OTHER.value)].reset_index(drop=True)
    out_sample_ids = out_sample_df.id.dropna().unique().tolist()
    if out_sample_ids:
        auth_cols = [SampleAuthorizeService.model.sample_id, SampleAuthorizeService.model.approve_result,
                     SampleAuthorizeService.model.fusion_times_limits, SampleAuthorizeService.model.fusion_deadline,
                     SampleAuthorizeService.model.fusion_limit, SampleAuthorizeService.model.current_fusion_count,
                     SampleAuthorizeService.model.total_fusion_count]
        sample_auth_df = pd.DataFrame(
            [i.to_dict() for i in
             SampleAuthorizeService.filter_scope_list("sample_id", out_sample_ids, cols=auth_cols)])
        if sample_auth_df.empty:
            out_sample_df["status"] = SampleStatusEnum.NOT_FIND.value
        else:
            out_auth_df = out_sample_df.merge(sample_auth_df, left_on='id', right_on='sample_id', how='left')
            out_sample_df["status"] = out_auth_df.apply(sample_can_remove, axis=1)
    res_df = pd.concat([my_sample_df, out_sample_df], axis=0)
    # model_train_samples_set = list(set([used_sample.sample_id for used_sample in
    #                                     ProjectUsedSampleService.query(project_id=project_id,
    #                                                                    sample_type=SampleTypeEnum.ORIGIN.value)]))
    res_df["can_remove"] = False
    res_df.drop_duplicates(subset='id', keep='last', inplace=True)
    res_df.status = res_df.status.apply(status_chinese_apply)
    res_df["type"] = ["origin"]*len(res_df)
    res_df.sort_values(by='create_time', ascending=False, inplace=True)
    data = res_df.to_dict("records")
    return get_json_result(data=data)


@manager.route("/import_sample", methods=['POST'])
@login_required
@validate_request("project_id")
@validate_project_id
def import_sample():
    """项目管理_我发起的_项目详情_导入样本列表展示"""
    project_id = request.json["project_id"]
    data = {
        "all_sample_type": [],
        "all_party_name": [],
        "data": []
    }
    try:
        party_ids = [project_party.party_id for project_party in ProjectPartyService.query(project_id=project_id)]
        if not party_ids:
            return get_json_result(data=data)
        cols = [SampleService.model.id, SampleService.model.name, SampleService.model.party_id,
                SampleService.model.party_name, SampleService.model.owner, SampleService.model.create_time,
                SampleService.model.sample_type, SampleService.model.sample_count, SampleService.model.comments]
        my_sample = pd.DataFrame(list(SampleService.query(status=StatusEnum.VALID.value,
                                                          owner=OwnerEnum.OWN.value, cols=cols).dicts()))
        out_sample_filters = [SampleService.model.party_id.in_(party_ids),
                              SampleService.model.owner == OwnerEnum.OTHER.value,
                              SampleAuthorizeService.model.approve_result.in_([ApproveStatusEnum.AGREE.value,
                                                                               ApproveStatusEnum.APPLY.value]),
                              SampleService.model.status == StatusEnum.VALID.value]
        out_cols = [SampleAuthorizeService.model.approve_result, SampleAuthorizeService.model.fusion_times_limits,
                    SampleAuthorizeService.model.fusion_limit, SampleAuthorizeService.model.total_fusion_count,
                    SampleAuthorizeService.model.current_fusion_count,
                    SampleAuthorizeService.model.fusion_deadline] + cols
        out_sample = pd.DataFrame(
            list(SampleService.get_auth_sample(cols=out_cols, filters=out_sample_filters).dicts()))
        out_sample["auth_status"] = out_sample.apply(sample_can_remove, axis=1)
        out_sample = out_sample[out_sample.auth_status == StatusEnum.VALID.value]
        res_df = pd.concat([my_sample, out_sample], axis=0)
        if res_df.empty:
            return get_json_result(data=[])
        remove_sample_ids = [i.sample_id for i in ProjectSampleService.query(project_id=project_id)]
        res_df = res_df[~(res_df.id.isin(remove_sample_ids))]
        # todo
        all_sample_ids = res_df.id.unique().tolist()
        sample_field_df = pd.DataFrame(i.to_dict() for i in
                                       SampleFieldsService.filter_scope_list("sample_id", all_sample_ids, filters=[
                                           SampleFieldsService.model.data_type == "特征"],
                                                                             cols=[SampleFieldsService.model.sample_id,
                                                                                   SampleFieldsService.model.field_name]))
        field_df = pd.DataFrame(sample_field_df["sample_id"].value_counts())
        field_df.rename(columns={"sample_id": "feature_count"}, inplace=True)
        field_df.index.name = "sample_id"
        field_df.reset_index(inplace=True)
        res_df = res_df.merge(field_df, left_on="id", right_on="sample_id", how="left")
        res_df["sample_count"] = res_df["sample_count"].fillna(0).astype(int)
        res_df["feature_count"] = res_df["feature_count"].fillna(0).astype(int)
        res_df.fillna('', inplace=True)
        res_df.drop_duplicates(subset='id', keep='first', inplace=True)
        res_df.sort_values(by='create_time', ascending=False, inplace=True)
        all_party_name = res_df.party_name.unique().tolist()
        local_name = "本地节点"
        if all_party_name.count(local_name):
            all_party_name.pop(all_party_name.index(local_name))
            all_party_name.insert(0,local_name )
        data["all_party_name"] = all_party_name
        data["all_sample_type"] = sorted(res_df.sample_type.unique().tolist())
        data["data"] = res_df.to_dict("records")
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=data, retmsg=str(e))


@manager.route("/import_sample/add", methods=['POST'])
@login_required
@validate_request('project_id', 'sample_ids')
@validate_project_id
def import_sample_add():
    """项目管理_我发起的_项目详情_导入样本"""
    sample_ids = request.json["sample_ids"]
    project_id = request.json["project_id"]
    sample_ids_list = list(set(sample_ids))
    try:
        ProjectSampleService.update_by_project(project_id, sample_ids_list, current_user.username)
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retcode=100, retmsg=str(e))


@manager.route("/sample/remove", methods=['POST'])
@login_required
@validate_request("project_id", "sample_id")
@validate_project_id
def remove_sample():
    """项目管理_我发起的_项目详情_移除样本"""
    sample_id = request.json["sample_id"]
    project_id = request.json["project_id"]
    try:
        filters = [ProjectSampleService.model.project_id == project_id,
                   ProjectSampleService.model.sample_id == sample_id]
        num = ProjectSampleService.filter_delete(filters)
        if not num:
            return get_json_result(data=False, retcode=100, retmsg=f'{project_id}project_id-{sample_id}sample_id不存在')
        else:
            return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retcode=100, retmsg=str(e))


@manager.route("/v_sample", methods=['POST'])
@login_required
@validate_request('project_id')
@validate_project_id
def query_vSample():
    """项目管理_我发起的_项目详情_融合样本"""
    project_id = request.json["project_id"]
    job_type = request.json.get("job_type")
    filters={}
    if job_type:
        filters=  [StudioProjectSample.job_type == job_type]
    cols = [StudioVSampleInfo.id.alias("v_sample_id"), StudioVSampleInfo.v_name.alias('name'),
            StudioVSampleInfo.mix_type,StudioVSampleInfo.party_info,StudioVSampleInfo.job_id,
            StudioVSampleInfo.component_name, StudioVSampleInfo.create_time]
    try:
        df = pd.DataFrame(ProjectSampleService.join_by_Vsample(project_id, cols=cols,filters=filters).dicts())
        if df.empty:
            return get_json_result(data=[])
        used_samples = [i.sample_id for i in ProjectUsedSampleService.query(project_id=project_id, cols=[
            ProjectUsedSampleService.model.sample_id])]
        sample_status_dict = ProjectSampleService.get_sample_status(df.party_info.to_list())
        df["v_sample_status"] = df.party_info.apply(ProjectSampleService.get_v_sample_status,
                                                    args=(sample_status_dict,))
        df["can_remove"] = np.where(df.v_sample_id.isin(set(used_samples)), False, True)

        df["type"] = ["fusion"] * len(df)
        df["component_name"] = df["component_name"].map(lambda x: WrapperFactory(x, 1))
        return get_json_result(data=df.to_dict(orient="records"))
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e))


@manager.route("/v_sample/remove", methods=['POST'])
@login_required
@validate_request('v_sample_id')
def v_sample_remove():
    """项目管理_我发起的_项目详情_融合样本_删除"""
    try:
        VSampleInfoService.delete_by_id(request.json["v_sample_id"])
        return get_json_result(data=True)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg="删除失败")


@manager.route("/v_sample/download", methods=["GET"])
@login_required
def vSample_downLoad():
    """项目管理_我发起的_项目详情_下载融合样本"""
    sample_id = request.args.to_dict().get("sample_id")
    if not sample_id:
        return get_json_result(retmsg='缺少sample_id 参数错误', retcode=101)
    flag, sample_obj = VSampleInfoService.get_by_id(sample_id)
    if not flag:
        return get_json_result(retmsg=f'{sample_id} 融合样本不存在')
    job_id = sample_obj.job_id
    sample_name = sample_obj.v_name
    component_name = sample_obj.component_name
    role = sample_obj.role
    party_id = sample_obj.party_id
    request_data = {'function': 'component_output_data',
                    'job_id': job_id,
                    'party_id': party_id,
                    'role': role,
                    'component_name': component_name,
                    'local': {'party_id': party_id, 'role': role}
                    }
    tasks = JobSaver.query_task(only_latest=True, job_id=job_id,
                                component_name=component_name,
                                role=role, party_id=party_id)
    if not tasks:
        raise ValueError(f'no found task, please check if the parameters are correct:{sample_id}')
    import_component_output_depend(tasks[0].f_provider_info)
    try:
        output_tables_meta = get_component_output_tables_meta(task_data=request_data)
    except Exception as e:
        stat_logger.exception(e)
        return error_response(210, str(e))
    limit = request_data.get('limit', -1)
    if not output_tables_meta:
        return error_response(response_code=210, retmsg='no data')
    if limit == 0:
        return error_response(response_code=210, retmsg='limit is 0')
    file_name = '{}_{}_{}_{}.tar.gz'.format(sample_name, job_id, role, party_id)
    return TableStorage.send_table(output_tables_meta, file_name, limit=limit, need_head=True)


@manager.route("/model", methods=['POST'])
@login_required
@validate_request("project_id")
@validate_project_id
def query_project_model():
    """项目管理_我发起的、我参与的_项目详情_模型"""
    cols = [ModelInfoExtendService.model.id.alias("model_id"), ModelInfoExtendService.model.name.alias("model_name"),
            ModelInfoExtendService.model.version.alias("model_version"), ModelInfoExtendService.model.job_id,
            ModelInfoExtendService.model.status, ModelInfoExtendService.model.approve_status,
            ModelInfoExtendService.model.mix_type,ModelInfoExtendService.model.create_time]
    try:
        df = pd.DataFrame(list(ModelInfoExtendService.query(project_id=request.json["project_id"],
                                                            cols=cols).dicts()))
        if df.empty:
            data = []
        else:
            used_models = set([used_model.model_version for used_model in
                               ProjectUsedModelService.query(project_id=request.json["project_id"],
                                                             cols=[ProjectUsedModelService.model.model_version])])
            df["is_used"] = np.where(df.model_version.isin(used_models), True, False)
            df["can_remove"] = model_can_remove(df)
            df.sort_values(by='create_time', ascending=False, inplace=True)
            data = df.to_dict("records")
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e))


@manager.route("/node", methods=['POST'])
@login_required
def query_project_node():
    """项目管理_我发起的_新建项目合作方节点"""
    cols = [PartyInfoService.model.id.alias("party_id"), PartyInfoService.model.party_name]
    project_id = request.json.get("project_id") if request.json else None
    try:
        df = pd.DataFrame(PartyInfoService.query(status=StatusEnum.VALID.value, cols=cols).dicts())
        if df.empty:
            return get_json_result(data=[])
        if project_id:
            project_sample_ids = list(
                set([i.sample_id for i in ProjectSampleService.query(project_id=project_id)]))
            can_not_remove_party_ids = set([i.party_id for i in
                                            SampleService.filter_scope_list("id", project_sample_ids,
                                                                            cols=[SampleService.model.party_id])])
            selected_party_ids = set([i.party_id for i in ProjectPartyService.query(project_id=project_id)])
            df["can_remove"] = np.where(df.party_id.isin(can_not_remove_party_ids), False, True)
            df["is_selected"] = np.where(df.party_id.isin(selected_party_ids), True, False)
        else:
            df["can_remove"] = True
            df["is_selected"] = False
        df.sort_values(by="party_name", inplace=True)
        data = df.to_dict("records")
        return get_json_result(data=data)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=[], retmsg=str(e))


@manager.route("/canvas_add", methods=['POST'])
@login_required
@validate_request("job_name", "job_type", "project_id")
def task_add():
    """项目管理_我发起的_新建任务"""
    job_name = request.json["job_name"]
    job_type = request.json["job_type"]
    project_id = request.json["project_id"]
    try:
        if ProjectCanvasService.get_or_none(job_name=job_name, project_id=project_id):
            return get_json_result(data=True, retmsg="任务名称{}已存在".format(job_name), retcode=100)
        canvas_id = get_uuid()
        canvas_dicts = {
            "id": canvas_id,
            "job_name": job_name,
            "job_type": job_type,
            "project_id": project_id,
            "creator": current_user.username
        }
        ProjectCanvasService.save(**canvas_dicts)

        error_info = {}
        for p in ProjectPartyService.get_join_party([project_id]).dicts():
            ret = federated_api(job_id=generate_job_id(),
                                method='POST',
                                endpoint="/project/host_canvas_add",
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=p["party_id"],
                                json_body={"project_id": project_id, "job_name": job_name,
                                           "job_type": job_type, "canvas_id": canvas_id,
                                           "user_name": current_user.username},
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                stat_logger.error(f"{p['party_id']}: {ret['retmsg']}")
                error_info[p['party_id']] = ret["retmsg"]

        return get_json_result(data={"canvas_id": canvas_id})
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=str(e), retmsg="新建任务失败", retcode=100)

@manager.route("/host_canvas_add", methods=['POST'])
@check_license
@validate_request("job_name", "job_type", "project_id", "canvas_id", "user_name")
def host_canvas_add():
    """项目管理_我发起的_新建任务"""
    job_name = request.json["job_name"]
    job_type = request.json["job_type"]
    project_id = request.json["project_id"]
    canvas_id = request.json["canvas_id"]
    username = request.json["user_name"]
    try:
        if ProjectCanvasService.get_or_none(job_name=job_name, project_id=project_id):
            return get_json_result(data=True, retmsg="任务名称{}已存在".format(job_name), retcode=100)

        canvas_dicts = {
            "id": canvas_id,
            "job_name": job_name,
            "job_type": job_type,
            "project_id": project_id,
            "creator": username
        }
        ProjectCanvasService.save(**canvas_dicts)
        return get_json_result(data={"canvas_id": canvas_id})
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data=str(e), retmsg="新建任务失败", retcode=100)

@manager.route("/partner", methods=['POST'])
@login_required
@validate_request("project_id")
@validate_project_id
def partner():
    project_id = request.json["project_id"]
    return get_json_result(
        data=pd.DataFrame(ProjectPartyService.get_join_party([project_id]).dicts()).to_dict("records"))
