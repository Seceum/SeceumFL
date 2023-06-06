from fate_flow.settings import ENGINES, stat_logger
from fate_flow.utils.api_utils import federated_api
from fate_flow.web_server.db_service.algorithm_service import AlgorithmInfoService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.enums import MixTypeChineseEnum


def check_sample_auth(job_type, party_info, parser):
    party_list = [i["party_id"] for i in party_info["host"]]
    if len(party_list) != len(set(party_list)):
        return False, '样本所属合作方不能重复'
    if job_type in [MixTypeChineseEnum.intersection.value, MixTypeChineseEnum.union.value]:
        used_modules = set([block_v.module for _, block_v in parser.blocks.items()])
        all_algorithm_modules = set(
            [sample_algorithm.module_name for sample_algorithm in AlgorithmInfoService.get_all()])
        used_algorithm_modules = list(used_modules.intersection(all_algorithm_modules))
    else:
        used_algorithm_modules = []
    endpoint = "/model_train/host_job_sample_auth"
    for out_party in party_info["host"]:
        dest_party_id = out_party["party_id"]
        json_body = {
            "sample_id": out_party["sample_id"],
            "sample_name": out_party["sample_name"],
            "apply_party_id": config.local_party_id,
            "module_names": used_algorithm_modules,
            "job_type": job_type
        }
        try:
            ret = federated_api(job_id="model_train_auth",
                                method='POST',
                                endpoint=endpoint,
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=dest_party_id,
                                json_body=json_body,
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                return False, "合作方样本{}权限验证失败".format(out_party["sample_name"])
            if not ret["data"]:
                return False, ret["retmsg"]
        except Exception as e:
            stat_logger.exception(e)
            return False, "合作方样本{}权限验证失败".format(out_party["sample_name"])
    return True, "success"


def notify_host_job_end(job_id, party_info, canvas_obj, project_obj, used_model_id=None, used_model_version=None):
    error_info = {}
    endpoint = "/model_train/host_training_run"
    for out_party in party_info["host"]:
        dest_party_id = out_party["party_id"]
        json_body = {
            "project_id": project_obj.id,
            "project_name": project_obj.name,
            "guest_party_id": config.local_party_id,
            "project_comments": project_obj.comments,
            "job_id": job_id,
            "canvas_id": canvas_obj.id,
            "job_name": canvas_obj.job_name,
            "sample_id": out_party["sample_id"],
            "job_type": canvas_obj.job_type,
            "apply_party_id": config.local_party_id,
            "used_model_id": used_model_id,
            "used_model_version": used_model_version,
        }
        try:
            ret = federated_api(job_id=job_id,
                                method='POST',
                                endpoint=endpoint,
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=dest_party_id,
                                json_body=json_body,
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                error_info[dest_party_id] = ret["retmsg"]
        except Exception as e:
            stat_logger.exception(e)
            error_info[dest_party_id] = str(e)
    return error_info

def convent_canceled_status(data):
    # input data=[{"a":1,"status":"canceled"},{"b":1,"status":"waiting"},{"c":1,"status":"success"}]
    # out data=[{"a":1,"status":"canceled"},{"b":1,"status":"canceled"},{"c":1,"status":"success"}]
    flag =False
    for i in data:
        if i["status"]=="canceled":
            flag=True
            break
    if flag==True:
        for i in data:
            if i["status"] == "waiting":
                i["status"]="canceled"
    return data