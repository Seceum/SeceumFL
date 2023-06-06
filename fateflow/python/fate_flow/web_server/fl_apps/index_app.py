import pandas as pd
from flask_login import login_required, current_user
from peewee import JOIN
from fate_flow.web_server.db.db_models import StudioProjectInfo, StudioProjectCanvas, \
    StudioProjectSample, StudioSampleInfo, StudioSampleAuthorize, StudioProjectParty
from fate_flow.web_server.db_service.model_service import ModelInfoExtendService
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.utils.df_apply import format_time
from fate_flow.web_server.utils.enums import StatusEnum, RoleTypeEnum, SampleTypeEnum, OwnerEnum, ApproveStatusEnum, \
    UserAuthEnum
from fate_flow.web_server.utils.reponse_util import get_json_result, have_permission_code, validate_permission_code
from fate_flow.web_server.fl_config import config
import numpy as np


@manager.route('/node_statistics', methods=['POST'])
@login_required
# @validate_permission_code(UserAuthEnum.SYSTEM_USER_NODE.value,UserAuthEnum.INDEX.value)
@validate_permission_code(UserAuthEnum.INDEX.value)
def own_data_list():
    """节点统计"""
    party_list = list(PartyInfoService.query(status=StatusEnum.VALID.value).dicts())
    total_party_nums = len(party_list)
    valid__partys_num = 0
    for party in party_list:
        if party["ping_status"] == "正常":
            valid__partys_num += 1
    data = {"total_partys_num": total_party_nums, "valid__partys_num": valid__partys_num}
    return get_json_result(data=data)


@manager.route('/modle_statistics', methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.INDEX.value)
# @validate_permission_code(UserAuthEnum.MODEL.value,UserAuthEnum.INDEX.value)
def model_count():
    """模型统计"""
    response_data = {"guest_model_num": 0, "guest_publish_num": 0, "host_model_num": 0, "host_publish_num": 0}
    if have_permission_code(UserAuthEnum.MODEL_GUEST.value):
        guest_model_df = pd.DataFrame(ModelInfoExtendService.get_by_role(RoleTypeEnum.GUEST.value).distinct().dicts())
        if not guest_model_df.empty:
            response_data["guest_model_num"] = len(guest_model_df)
            response_data["guest_publish_num"] = sum(guest_model_df["status"] == "已发布")
    if have_permission_code(UserAuthEnum.MODEL_HOST.value):
        host_model_df = pd.DataFrame(ModelInfoExtendService.get_by_role(RoleTypeEnum.HOST.value).distinct().dicts())
        if not host_model_df.empty:
            response_data["host_model_num"] = len(host_model_df)
            response_data["host_publish_num"] = sum(host_model_df["status"] == "已发布")
    return get_json_result(data=response_data)


@manager.route('/sample_statistics_and_ratio', methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.INDEX.value)
def sample_statistics_and_ratio():
    """数据统计和占比和数据审批"""
    response_data = {
        "sample_detail": {"own_sample": 0, "external_sample": 0, "v_sample": 0,
                          "own_ratio": "0%", "external_ratio": "0%", "v_ratio": "0%", },
        "sample_statistics": {"sample_approve_num": "0%", "waitting_approve_num": "0%"}
    }
    if have_permission_code(UserAuthEnum.DATA_GUEST.value):
        auth_projects = current_user.get_auth_projects()
        own_external_sample = StudioSampleInfo.select(). \
            where(StudioSampleInfo.status == StatusEnum.VALID.value)
        df = pd.DataFrame(own_external_sample.dicts())
        own_sample_num = 0
        external_sample_num = 0
        if not df.empty:
            own_sample_num = int(np.array(df["owner"] == OwnerEnum.OWN.value).sum())
            if have_permission_code(UserAuthEnum.DATA_HOST.value):
                external_sample_num = int(np.array(df["owner"] == OwnerEnum.OTHER.value).sum())
        v_sample_num = StudioProjectSample.select().where(StudioProjectSample.project_id.in_(auth_projects),
                                                          StudioProjectSample.sample_type == SampleTypeEnum.FUSION.value).count()
        total_sample = own_sample_num + external_sample_num + v_sample_num
        if total_sample != 0:
            own_ratio = "%.2f%%" % (own_sample_num * 100 / total_sample)
            external_ratio = "%.2f%%" % (external_sample_num * 100 / total_sample)
            v_ratio = "%.2f%%" % (v_sample_num * 100 / total_sample)
        else:
            own_ratio = 0
            external_ratio = 0
            v_ratio = 0
        response_data["sample_detail"]["own_sample"] = own_sample_num
        response_data["sample_detail"]["external_sample"] = external_sample_num
        response_data["sample_detail"]["v_sample"] = v_sample_num
        response_data["sample_detail"]["own_ratio"] = own_ratio
        response_data["sample_detail"]["external_ratio"] = external_ratio
        response_data["sample_detail"]["v_ratio"] = v_ratio
    if have_permission_code(UserAuthEnum.DATA_APPROVE_GUEST.value):
        approve_num_df = pd.DataFrame(StudioSampleAuthorize.select(StudioSampleAuthorize.approve_result).where(
            StudioSampleAuthorize.owner == OwnerEnum.OWN.value).dicts())
        if not approve_num_df.empty:
            response_data["sample_statistics"]["sample_approve_num"] = len(approve_num_df)
            if have_permission_code(UserAuthEnum.DATA_APPROVE_GUEST_APPLY.value):
                response_data["sample_statistics"]["waitting_approve_num"] = int(np.array(
                    approve_num_df["approve_result"] == ApproveStatusEnum.APPLY.value).sum())
        else:
            response_data["sample_statistics"]["sample_approve_num"] = 0
            response_data["sample_statistics"]["waitting_approve_num"] = 0
    return get_json_result(data=response_data)


@manager.route('/project_job_statistics_and_run', methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.INDEX.value)
def project_job_statistics_and_run():
    """项目，任务,执行结果统计,最近任务"""
    response_data = {
        "project_statistics": {"guest_project_num": 0, "guest_job_num": 0, "host_project_num": 0, "host_job_num": 0},
        "average_statistics": {},
        "execute_statistics": {
            "success_num": 0, "failed_and_time_out_num": 0, "running_waitint_num": 0, "cannel_num": 0,
            "success_ratio": "0%", "failed_and_time_out_ratio": "0%", "running_waitint_ratio": "0%",
            "cannel_ratio": "0%"
        },
        "recent_statistics": [],
    }
    if have_permission_code(UserAuthEnum.PROJECT.value):
        if have_permission_code(UserAuthEnum.PROJECT_HOST.value):
            host_project = StudioProjectInfo.select().where(
                StudioProjectInfo.role_type == RoleTypeEnum.HOST.value)
            if host_project:
                host_job_num = host_project.join(StudioProjectCanvas, JOIN.INNER,
                                                 on=(StudioProjectInfo.id == StudioProjectCanvas.project_id)).count()
                response_data["project_statistics"]["host_project_num"] = host_project.count()
                response_data["project_statistics"]["host_job_num"] = host_job_num
        if have_permission_code(UserAuthEnum.PROJECT_GUEST.value):
            auth_projects = current_user.get_auth_projects()
            if auth_projects:
                project_df = pd.DataFrame(StudioProjectInfo. \
                                          select(StudioProjectInfo.id.alias("project_id"),
                                                 StudioProjectInfo.create_time,
                                                 ).where(StudioProjectInfo.id.in_(auth_projects)).dicts())
                year_month_count = project_df.groupby(
                    [project_df.create_time.dt.year, project_df.create_time.dt.month]).apply(
                    lambda x: len(x["project_id"].unique())).to_dict()
                for k, v in year_month_count.items():
                    year, month, project_num = k[0], k[1], v
                    if response_data["average_statistics"].get(year):
                        response_data["average_statistics"][year][month] = {"project_num": project_num, "job_num": 0}
                    else:
                        response_data["average_statistics"][year] = {
                            month: {"project_num": project_num, "job_num": 0}}

                project_canvas_job_status_data = StudioProjectInfo. \
                    select(StudioProjectInfo.id.alias("project_id"), StudioProjectInfo.name.alias("project_name"),
                           StudioProjectCanvas.id.alias("canvas_id"), StudioProjectCanvas.job_type,
                           StudioProjectCanvas.job_name, StudioProjectCanvas.update_time,
                           StudioProjectCanvas.create_time, StudioProjectCanvas.status,
                           ). \
                    join(StudioProjectCanvas, JOIN.INNER, on=(StudioProjectInfo.id == StudioProjectCanvas.project_id)). \
                    where(StudioProjectInfo.id.in_(auth_projects)). \
                    order_by(StudioProjectCanvas.update_time.desc()).distinct()
                if project_canvas_job_status_data:
                    local_proj = set([d["project_id"] for d in
                                      StudioProjectParty.select(StudioProjectParty.project_id).where(
                                          StudioProjectParty.project_id.in_(auth_projects)).dicts()])
                    df = pd.DataFrame(project_canvas_job_status_data.dicts())
                    df["curr_party_id"] = df["project_id"].map(
                        lambda x: str(config.local_party_id) if x not in local_proj else "")
                    # 项目数和job数
                    job_num = len(df)
                    response_data["project_statistics"]["guest_project_num"] = len(auth_projects)
                    response_data["project_statistics"]["guest_job_num"] = job_num

                    # 最近job
                    recent_statistics_df = df.copy()[:10]
                    recent_statistics_df["format_time"] = recent_statistics_df["update_time"].apply(format_time)
                    recent_statistics_df = recent_statistics_df[
                        ["project_id", "canvas_id", "job_type", "job_name", "status", "format_time", "project_name",
                         "curr_party_id"]]
                    recent_statistics_df.rename(columns={"status": "f_status"}, inplace=True)
                    response_data["recent_statistics"] = recent_statistics_df.to_dict("records")
                    success_num = sum(df["status"] == "success")
                    failed_and_time_out_num = sum(df["status"].isin(["failed", "timeout"]))
                    running_waitint_num = sum(df["status"].isin(["running", "waiting", "ready", "pass", "save"]))
                    cannel_num = sum(df["status"] == "canceled")
                    success_ratio = "%.2f%%" % (success_num * 100 / job_num)
                    failed_and_time_out_ratio = "%.2f%%" % (failed_and_time_out_num * 100 / job_num)
                    running_waitint_ratio = "%.2f%%" % (running_waitint_num * 100 / job_num)
                    cannel_ratio = "%.2f%%" % (cannel_num * 100 / job_num)
                    response_data["execute_statistics"]["success_num"] = success_num
                    response_data["execute_statistics"]["failed_and_time_out_num"] = failed_and_time_out_num
                    response_data["execute_statistics"]["running_waitint_num"] = running_waitint_num
                    response_data["execute_statistics"]["cannel_num"] = cannel_num
                    response_data["execute_statistics"]["success_ratio"] = success_ratio
                    response_data["execute_statistics"]["failed_and_time_out_ratio"] = failed_and_time_out_ratio
                    response_data["execute_statistics"]["running_waitint_ratio"] = running_waitint_ratio
                    response_data["execute_statistics"]["cannel_ratio"] = cannel_ratio

                    # 对月分组进行统计
                    year_month_count = df.groupby([df.create_time.dt.year, df.create_time.dt.month]).apply(
                        lambda x: len(x)).to_dict()
                    for k, v in year_month_count.items():
                        year, month, job_num = k[0], k[1], v
                        if response_data["average_statistics"].get(year):
                            if response_data["average_statistics"].get(year, {}).get(month):
                                response_data["average_statistics"][year].get(month, {})["job_num"] = job_num
                            else:
                                response_data["average_statistics"][year][month] = {"project_num": 0,
                                                                                    "job_num": job_num}
                        else:
                            response_data["average_statistics"][year] = {
                                month: {"project_num": 0, "job_num": job_num}}
                    return get_json_result(data=response_data)
                else:
                    response_data["project_statistics"]["guest_project_num"] = len(auth_projects)
                    return get_json_result(data=response_data)
    return get_json_result(data=response_data)
