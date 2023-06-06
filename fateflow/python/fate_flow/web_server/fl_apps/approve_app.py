import pandas as pd
import numpy as np
import peewee
from flask import request
from flask_login import login_required, current_user

from fate_flow.settings import ENGINES, stat_logger
from fate_flow.utils.api_utils import federated_api
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db_service.algorithm_service import AlgorithmInfoService, SampleAlgorithmService
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.db_service.sample_service import SampleService, SampleAuthorizeService, \
    SampleAuthorizeHistoryService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.common_util import str2date, get_format_time, get_uuid
from fate_flow.web_server.utils.df_apply import own_approve_result_apply, concat_col, approve_times_limits, \
    approve_fusion_count
from fate_flow.web_server.utils.enums import OwnerEnum, ApproveStatusEnum, MixTypeEnum, MixTypeChineseEnum, UserAuthEnum
from fate_flow.web_server.utils.license_util import check_license
from fate_flow.web_server.utils.reponse_util import get_json_result, validate_permission_code


@manager.route("/guest_apply_auth", methods=['POST'])
# @validate_request("apply_party_id", "sample_id", "apply_time")
# @validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_APPROVE.value,UserAuthEnum.DATA_APPROVE_GUEST_APPLY.value)
@check_license
def guest_apply_auth():
    """用于guest方请求-授权状态改变"""
    request_data = request.json
    sample_id = request_data["sample_id"]
    apply_party_id = request_data["apply_party_id"]
    apply_time = request_data["apply_time"]
    user = "{}-{}".format("out_party_id", request_data["src_party_id"])
    try:
        party_obj = PartyInfoService.query(id=apply_party_id).get()
        sample_obj = SampleService.query(id=sample_id).get()
    except peewee.DoesNotExist:
        return get_json_result(data=False, retmsg='party_id or sample_id not exist', retcode=100)
    apply_party_name = party_obj.party_name
    approve_party_name = config.local_party_id
    sample_name = sample_obj.name
    flag = SampleAuthorizeService.get_or_create(config.local_party_id, apply_party_id, sample_id, OwnerEnum.OWN.value,
                                                ApproveStatusEnum.APPLY.value, user, apply_time=apply_time,
                                                apply_party_name=apply_party_name,
                                                approve_party_name=approve_party_name,
                                                sample_name=sample_name)
    return get_json_result(data=flag)


@manager.route("/host_approve_auth", methods=['POST'])
@check_license
def host_apply_auth():
    """用于host我方通知-授权状态改变"""
    request_data = request.json
    sample_id = request_data["sample_id"]
    party_id = request_data["party_id"]
    approve_time = request_data["approve_time"]
    approve_result = request_data["approve_result"]
    fusion_times_limits = request_data.get("fusion_times_limits", None)
    algorithm_module_names = list(set(request_data.get("algorithm_module_names", [])))
    fusion_limit = request_data.get("fusion_limit")
    req_deadline = request_data["fusion_deadline"]
    fusion_deadline = str2date(req_deadline).date() if req_deadline else None
    user = "{}-{}".format("out_party_id", request_data["src_party_id"])
    try:
        party_obj = PartyInfoService.query(id=party_id).get()
        sample_obj = SampleService.query(id=sample_id).get()
    except peewee.DoesNotExist:
        return get_json_result(data=False, retmsg=f'节点 {party_id} 或 样本 {sample_id} 不存在', retcode=100)
    apply_party_name = config.local_party_id
    approve_party_name = party_obj.party_name
    sample_name = sample_obj.name
    agree_update_dict = {}
    if approve_result == ApproveStatusEnum.AGREE.value:
        agree_update_dict["fusion_times_limits"] = fusion_times_limits
        agree_update_dict["fusion_deadline"] = fusion_deadline
        agree_update_dict["fusion_limit"] = fusion_limit
    algorithm_sample_list = []
    if algorithm_module_names:
        al_objs_list = AlgorithmInfoService.filter_scope_list("module_name", algorithm_module_names)
        for al_obj in al_objs_list:
            algorithm_sample_list.append({
                "id": get_uuid(),
                "sample_id": sample_id,
                "algorithm_id": al_obj.id,
                "module_name": al_obj.module_name,
                "algorithm_name": al_obj.name,
                "creator": user,
                "create_time": approve_time
            })

    SampleAuthorizeService.get_or_create(party_id, config.local_party_id, sample_id,
                                         OwnerEnum.OTHER.value,
                                         approve_result, user,
                                         approve_time=approve_time,
                                         apply_party_name=apply_party_name,
                                         approve_party_name=approve_party_name,
                                         sample_name=sample_name,
                                         algorithm_sample_list=algorithm_sample_list,
                                         **agree_update_dict)

    return get_json_result(data=True)


@manager.route("/list", methods=['POST'])
@login_required
@validate_request("type")
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_APPROVE.value)
def approve_list():
    """用于guest方请求-授权状态改变"""
    owner = str(request.json["type"])
    auth_sample_list = list(SampleAuthorizeService.get_auth_sample(owner=owner).dicts())
    data = {
        "all_apply_party_name": [],
        "all_approve_party_name": [],
        "all_sample_type": [],
        "all_algorithm_name": [],
        "all_approve_result": [],
        "data": []
    }
    if auth_sample_list:
        df = pd.DataFrame(auth_sample_list)
        sample_ids = df.sample_id.dropna().unique().tolist()
        al_cols = [SampleAlgorithmService.model.sample_id, SampleAlgorithmService.model.algorithm_name]
        al_df = pd.DataFrame(
            [i.to_dict() for i in SampleAlgorithmService.filter_scope_list("sample_id", sample_ids, cols=al_cols)])
        if not al_df.empty:
            data["all_algorithm_name"] = sorted(filter(lambda x: x, al_df.algorithm_name.dropna().unique().tolist()))
            al_df = al_df.groupby(al_df["sample_id"]).apply(concat_col).reset_index(drop=True)
            df = df.merge(al_df, left_on="sample_id", right_on="sample_id", how='left')
        else:
            df["algorithm_id"] = np.nan
            df["algorithm_name"] = ""
        data["all_apply_party_name"] = list(set(df.apply_party_name.tolist()))
        data["all_approve_party_name"] = list(set(df.approve_party_name.tolist()))
        data["all_sample_type"] = sorted(set(df.sample_type.dropna().tolist()), reverse=True)
        df.fillna("", inplace=True)
        df["fusion_times_limits"] = df.apply(approve_times_limits, axis=1)
        df["current_fusion_count"] = df.apply(approve_fusion_count, axis=1)
        df.approve_result = df.approve_result.apply(own_approve_result_apply)
        df.sort_values(by='apply_time', ascending=False, inplace=True)
        data["data"] = df.to_dict("records")
        all_approve_result = list(filter(lambda x: x, df.approve_result.dropna().unique().tolist()))
        data["all_approve_result"] = sorted(all_approve_result)
    return get_json_result(data=data)


@manager.route("/status", methods=['POST'])
@login_required
@validate_request("id", "operate", "sample_id")
def approve_status():
    """我授权的_审批"""
    # 同意:1，拒绝:2, 取消授权：3
    request_data = request.json
    pid = request_data["id"]
    approve_result = str(request_data["operate"])
    fusion_times_limits = request_data.get("fusion_times_limits", None)
    req_deadline = request_data.get("fusion_deadline")
    fusion_deadline = str2date(req_deadline).date() if req_deadline else None
    algorithm_module_names = list(set(request_data.get("algorithm_module_names", [])))
    if request_data.get("fusion_limit") is not None:
        fusion_limit = True if int(request_data["fusion_limit"]) else False
    else:
        fusion_limit = None
    if not fusion_limit:
        fusion_times_limits = None
    auth_obj = SampleAuthorizeService.get_or_none(id=pid)
    if not auth_obj:
        return get_json_result(data=False, retmsg=f'{pid} not exist', retcode=100)
    # 通知guest已经审批
    job_id = "approve_auth_notify_forward"
    endpoint = "/approve/host_approve_auth"
    approve_party_id = auth_obj.approve_party_id
    apply_party_id = auth_obj.apply_party_id
    sample_id = auth_obj.sample_id
    current = get_format_time()
    if approve_result == ApproveStatusEnum.AGREE.value and fusion_limit:
        pre_fusion_times_limits = auth_obj.fusion_times_limits if auth_obj.fusion_times_limits else 0
        fusion_times_limits = int(fusion_times_limits) if fusion_times_limits else 0
        fusion_times_limits = fusion_times_limits + pre_fusion_times_limits
    try:
        json_body = {
            "party_id": approve_party_id,
            "sample_id": sample_id,
            "approve_time": current,
            "approve_result": approve_result,
            "fusion_times_limits": fusion_times_limits,
            "fusion_limit": fusion_limit,
            "fusion_deadline": req_deadline,
            "algorithm_module_names": algorithm_module_names
        }
        ret = federated_api(job_id=job_id,
                            method='POST',
                            endpoint=endpoint,
                            src_role="guest",
                            src_party_id=config.local_party_id,
                            dest_party_id=apply_party_id,
                            json_body=json_body,
                            federated_mode=ENGINES["federated_mode"])
        if ret["retcode"]:
            error_info = {apply_party_id: ret["retmsg"]}
            return get_json_result(retmsg="error", data={"error_info": error_info}, retcode=100)
        else:
            agree_update_dict = {}
            if approve_result == ApproveStatusEnum.AGREE.value:
                agree_update_dict["fusion_times_limits"] = fusion_times_limits
                agree_update_dict["fusion_deadline"] = fusion_deadline
                agree_update_dict["fusion_limit"] = fusion_limit
            algorithm_sample_list = []
            user_name = current_user.username
            if algorithm_module_names:
                al_objs_list = AlgorithmInfoService.filter_scope_list("module_name", algorithm_module_names)
                for al_obj in al_objs_list:
                    algorithm_sample_list.append({
                        "id": get_uuid(),
                        "sample_id": sample_id,
                        "algorithm_id": al_obj.id,
                        "module_name": al_obj.module_name,
                        "algorithm_name": al_obj.name,
                        "creator": user_name,
                        "create_time": current
                    })
            SampleAuthorizeService.get_or_create(approve_party_id, apply_party_id, sample_id,
                                                 OwnerEnum.OWN.value,
                                                 approve_result, user_name,
                                                 approve_time=current,
                                                 algorithm_sample_list=algorithm_sample_list, history=True,
                                                 auth_obj=auth_obj,
                                                 **agree_update_dict)
            return get_json_result(data=ret["data"])
    except Exception as e:
        stat_logger.exception(e)
        error_info = {apply_party_id: str(e)}
        return get_json_result(retmsg="error", data={"error_info": error_info}, retcode=100)


@manager.route("/algorithm", methods=['POST'])
@login_required
@validate_request("sample_id")
def algorithm_list():
    """算法用途列表"""
    sample_id = request.json["sample_id"]
    sample_obj = SampleService.get_or_none(id=sample_id)
    if not sample_obj:
        return get_json_result(retmsg="样本id不存在", data=[], retcode=100)
    sample_type = sample_obj.sample_type
    cols = [AlgorithmInfoService.model.id.alias("algorithm_id"), AlgorithmInfoService.model.name.alias(
        "algorithm_name"), AlgorithmInfoService.model.module_name]
    # sample_alg_list = set([j.algorithm_id for j in SampleAlgorithmService.query(sample_id=sample_id)])
    if sample_type == MixTypeChineseEnum.intersection.value:
        df = pd.DataFrame(AlgorithmInfoService.query(mix_type=MixTypeEnum.intersection.value, cols=cols).dicts())
        data = df.to_dict("records")
    elif sample_type == MixTypeChineseEnum.union.value:
        df = pd.DataFrame(AlgorithmInfoService.query(mix_type=MixTypeEnum.union.value, cols=cols).dicts())
        data = df.to_dict("records")
    else:
        data = []
    return get_json_result(data=data)


@manager.route("/sample_approve_history", methods=['POST'])
@login_required
@validate_request("sample_id")
def sample_apply_history():
    """样本授权历史"""
    df = pd.DataFrame(SampleAuthorizeHistoryService.get_sample_history_by_smaple_id(request.json["sample_id"]).dicts())
    if not df.empty:
        df["fusion_times_limits"] = df.apply(approve_times_limits, axis=1)
        df.approve_result = df.approve_result.apply(own_approve_result_apply)
        df.sort_values(by='apply_time', ascending=False, inplace=True)
        return get_json_result(data=df.to_dict("records"))
    else:
        return get_json_result(data=[])
