from datetime import datetime
import pandas as pd
import peewee
from flask import request
from flask_login import login_required, current_user
from fate_flow.settings import ENGINES, stat_logger
from fate_flow.utils.api_utils import federated_api, get_data_error_result
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db_service.algorithm_service import SampleAlgorithmService
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.db_service.sample_service import SampleAuthorizeService, SampleService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.common_util import datetime_format
from fate_flow.web_server.utils.df_apply import out_approve_result_apply, external_status, concat_col, \
    approve_times_limits, approve_fusion_count, approve_result_to_sample_status, sample_chinese_status, \
    status_and_publish_status
from fate_flow.web_server.utils.enums import OwnerEnum, ApproveOutStatusChineseEnum, ApproveStatusEnum, UserAuthEnum
from fate_flow.web_server.utils.reponse_util import get_json_result, validate_permission_code
from playhouse.shortcuts import model_to_dict


@manager.route("/partner", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_HOST.value)
def partner():
    """获得所有外部合作方"""
    sample_df = pd.DataFrame(
        SampleService.query(owner=OwnerEnum.OTHER.value, cols=[SampleService.model.party_id],
                            reverse=True).dicts()).drop_duplicates(keep="first")

    if sample_df.empty: return get_json_result(data=[])

    party_ids = list(set(sample_df.party_id.tolist()))
    party_df = pd.DataFrame(PartyInfoService.get_by_ids(party_ids, cols=[PartyInfoService.model.id.alias("party_id"),
                                                                         PartyInfoService.model.party_name]).dicts())
    if party_df.empty: return get_data_error_result(100, "Sorry, 画布保存失败！")
    sample_df = sample_df.merge(party_df, left_on='party_id', right_on="party_id", how="left")
    return get_json_result(data=sample_df.to_dict("records"))


@manager.route("/list", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_HOST.value)
def get_external_data_list():
    """外部数据展示列表，前端分页"""
    smp_type = request.json.get("sample_type")
    sample_cols = [SampleService.model.id.alias("sample_id"), SampleService.model.name,
                   SampleService.model.party_id, SampleService.model.status,
                   SampleService.model.comments, SampleService.model.publish_status,
                   SampleService.model.type, SampleService.model.sample_type,
                   SampleService.model.sample_count,
                   SampleService.model.create_time, SampleService.model.update_time]

    pid = str(request.json.get("party_id", ""))

    if smp_type:
        sample_df = pd.DataFrame(
            SampleService.query(owner=OwnerEnum.OTHER.value, sample_type=smp_type, cols=sample_cols,
                                reverse=True).dicts())
    else:
        sample_df = pd.DataFrame(
            SampleService.query(owner=OwnerEnum.OTHER.value, cols=sample_cols, reverse=True).dicts())

    if sample_df.empty: return get_json_result(data=[])
    if pid: sample_df = sample_df.loc[sample_df.party_id == pid, :]
    if sample_df.empty: return get_json_result(data=[])

    if not pid:
        party_ids = list(set(sample_df.party_id.tolist()))
        party_df = pd.DataFrame(
            PartyInfoService.get_by_ids(party_ids, cols=[PartyInfoService.model.id.alias("party_id"),
                                                         PartyInfoService.model.party_name]).dicts())
        if party_df.empty:
            sample_df["party_id"] = ""
            sample_df["party_name"] = ""
        else:
            sample_df = sample_df.merge(party_df, left_on='party_id', right_on="party_id", how="left")

    auth_cols = [SampleAuthorizeService.model.sample_id, SampleAuthorizeService.model.approve_result,
                 SampleAuthorizeService.model.fusion_times_limits,
                 SampleAuthorizeService.model.current_fusion_count, SampleAuthorizeService.model.total_fusion_count,
                 SampleAuthorizeService.model.fusion_limit, SampleAuthorizeService.model.fusion_deadline]
    auth_list = SampleAuthorizeService.query(owner=OwnerEnum.OTHER.value, apply_party_id=config.local_party_id,
                                             cols=auth_cols).dicts()
    for i in auth_list:
        if i["fusion_times_limits"] is None:
            i["fusion_times_limits"] = ""

    auth_df = pd.DataFrame(auth_list)
    if sample_df.empty:
        data_list = []
    elif auth_df.empty:
        sample_df["approve_result"] = ApproveOutStatusChineseEnum.NOT_APPLY.value
        sample_df["publish_status"] = sample_df.apply(lambda x: external_status(x["publish_status"]),
                                                      axis=1)
        sample_df["fusion_times_limits"] = ""
        sample_df["current_fusion_count"] = ""
        sample_df["fusion_deadline"] = ""
        sample_df["algorithm_name"] = ""
        sample_df.fillna("", inplace=True)
        sample_df["id"] = sample_df["sample_id"]
        data_list = sample_df.to_dict("records")
    else:
        auth_df2 = auth_df.iloc[:, :-2].astype(str)
        auth_df2[["fusion_limit", "fusion_deadline"]] = auth_df[["fusion_limit", "fusion_deadline"]]
        df = sample_df.merge(auth_df2, left_on="sample_id", right_on="sample_id", how="left")
        sample_ids = df.sample_id.dropna().unique().tolist()
        al_cols = [SampleAlgorithmService.model.sample_id, SampleAlgorithmService.model.algorithm_name]
        al_df = pd.DataFrame(
            [i.to_dict() for i in SampleAlgorithmService.filter_scope_list("sample_id", sample_ids, cols=al_cols)])

        if not al_df.empty:
            al_df = al_df.groupby(al_df["sample_id"]).apply(concat_col).reset_index(drop=True)
            df = df.merge(al_df, left_on="sample_id", right_on="sample_id", how='left')
        else:
            df["algorithm_id"] = ""
            df["algorithm_name"] = ""

        df["publish_status"] = df.apply(lambda x: external_status(x["publish_status"]), axis=1)
        df.fillna("", inplace=True)
        df["fusion_times_limits"] = df.apply(approve_times_limits, axis=1)
        df["current_fusion_count"] = df.apply(approve_fusion_count, axis=1)
        # 下面3行，过滤出approve_result已经审核，发布状态是用效，样本状态用效
        if pid:
            df["status"] = df["approve_result"].apply(approve_result_to_sample_status)
            df["status"] = df["status"].apply(sample_chinese_status)
            df["status"] = df.apply(status_and_publish_status, axis=1)
            df = df.loc[df.status != "未申请", :]
            df = df.loc[df.status != "申请中", :]
            df = df.loc[df.status != "未授权", :]
        # else:
        #     df["status"] = df["status"].apply(sample_chinese_status)
        #     # df.sort_values(by='fusion_deadline', ascending=False, inplace=True)
        #     # df = df.loc[df.status == SampleStatusEnum.VALID.value, :]
        #     # df = df.loc[df.publish_status == SampleStatusChineseEnum.VALID.value, :]

        df["approve_result"] = df["approve_result"].apply(out_approve_result_apply)
        df["id"] = df["sample_id"]
        data_list = df.to_dict("records")

    return get_json_result(data=data_list)


@manager.route("/auth_apply", methods=['POST'])
@login_required
@validate_request("sample_id")
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_HOST.value, UserAuthEnum.DATA_HOST_APPLY.value)
def auth_apply():
    """外部数据_授权申请"""
    # 修改授权状态
    request_data = request.json
    sample_id = request_data["sample_id"]
    apply_time = datetime_format(datetime.now())
    try:
        sample_obj = SampleService.query(id=sample_id).get()
        party_obj = PartyInfoService.query(id=sample_obj.party_id).get()
    except peewee.DoesNotExist:
        return get_json_result(data=False, retmsg='party_id or sample_id does not exist', retcode=100)
    approve_party_name = party_obj.party_name
    approve_party_id = sample_obj.party_id
    apply_party_id = config.local_party_id
    apply_party_name = config.local_party_id
    sample_name = sample_obj.name
    auth_objs = SampleAuthorizeService.query(approve_party_id=approve_party_id,
                                             apply_party_id=apply_party_id,
                                             sample_id=sample_id, owner=OwnerEnum.OTHER.value)
    origin_auth_dict = model_to_dict(auth_objs[0]) if auth_objs else {}
    SampleAuthorizeService.get_or_create(approve_party_id, apply_party_id, sample_id,
                                         OwnerEnum.OTHER.value,
                                         ApproveStatusEnum.APPLY.value, current_user.username,
                                         apply_time=apply_time, approve_party_name=approve_party_name,
                                         apply_party_name=apply_party_name, sample_name=sample_name)
    job_id = "external_apply_auth_forward"
    endpoint = "/approve/guest_apply_auth"
    json_body = {
        "apply_party_id": apply_party_id,
        "sample_id": sample_id,
        "apply_time": apply_time,
    }
    try:
        ret = federated_api(job_id=job_id,
                            method='POST',
                            endpoint=endpoint,
                            src_role="guest",
                            src_party_id=config.local_party_id,
                            dest_party_id=approve_party_id,
                            json_body=json_body,
                            federated_mode=ENGINES["federated_mode"])
        if ret["retcode"]:
            filters = [SampleAuthorizeService.model.approve_party_id == approve_party_id,
                       SampleAuthorizeService.model.apply_party_id == apply_party_id,
                       SampleAuthorizeService.model.sample_id == sample_id,
                       SampleAuthorizeService.model.owner == OwnerEnum.OTHER.value,
                       ]
            if not auth_objs:
                SampleAuthorizeService.filter_delete(filters)
            else:
                SampleAuthorizeService.filter_update(filters, origin_auth_dict)
            data = {"party_id": approve_party_id, "error_info": ret["retmsg"]}
            msg = "error"
            return get_json_result(data=data, retmsg=msg, retcode=100)
        else:
            data = ret["data"]
            msg = "success"
            return get_json_result(data=data, retmsg=msg)
    except Exception as e:
        filters = [SampleAuthorizeService.model.approve_party_id == approve_party_id,
                   SampleAuthorizeService.model.apply_party_id == apply_party_id,
                   SampleAuthorizeService.model.sample_id == sample_id,
                   SampleAuthorizeService.model.owner == OwnerEnum.OTHER.value,
                   SampleAuthorizeService.model.approve_result == ApproveStatusEnum.APPLY.value]
        if not auth_objs:
            SampleAuthorizeService.filter_delete(filters)
        else:
            SampleAuthorizeService.filter_update(filters, origin_auth_dict)
        stat_logger.error(e)
        return get_json_result(data=str(e), retmsg="授权申请失败", retcode=100)
