import json
import operator
import time
from copy import deepcopy
from datetime import datetime

from fate_flow.settings import ENGINES, stat_logger
from fate_flow.utils import cron, job_utils
from fate_flow.utils.api_utils import federated_api
from fate_flow.utils.log_utils import detect_logger
from fate_flow.web_server.db.db_models import StudioModelInfoExtend, StudioSampleInfo, StudioSampleAuthorize
from fate_flow.web_server.db_service.sample_service import SampleAuthorizeService, SampleService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.common_util import datetime_format, pull_approval_result, model_id_get_hosts, \
    get_format_time
from fate_flow.web_server.utils.enums import PublishStatusChineseEnum, APPROVEChineseEnum, RoleTypeEnum, StatusEnum, \
    SamplePublishStatusEnum, OwnerEnum, StatusChineseEnum, SampleStatusEnum
from fate_flow.pipelined_model import publish_model


class Publish_detector(cron.Cron):
    def run_do(self):
        self.detect_model_publish()
        self.detect_sample_status()


    @classmethod
    def detect_model_publish(cls):
        detect_logger().info('start detect_model_publish')
        try:
            objs = StudioModelInfoExtend.query(**{"status": "未发布", "approve_progress": 100, "role_type": "guest"})
            if not objs:
                return
            obj = objs[0]
            obj_json = obj.to_dict()
            service_name = obj.service_name
            model_id = obj_json["id"]
            model_version = obj_json["version"]
            federated_mode = ENGINES["federated_mode"]
            hosts = model_id_get_hosts(obj.id)
            status = PublishStatusChineseEnum.FAILD.value
            retcode, retmsg, host_approval_result = pull_approval_result(obj.id, obj.version, hosts)
            if retcode:
                obj.status = PublishStatusChineseEnum.FAILD.value
                obj.approve_status = APPROVEChineseEnum.APPROVE_FALSE.value
                obj.save()
            for host_id, host_obj in host_approval_result.items():
                if host_obj["approve_result"] != "1":
                    obj.status = PublishStatusChineseEnum.FAILD.value
                    obj.approve_status = APPROVEChineseEnum.APPROVE_FALSE.value
                    obj.save()
                    cls.notify_host_publish_return(hosts, federated_mode, model_id, model_version, obj, status)
                    return
            obj.status = PublishStatusChineseEnum.RUNNING.value
            obj.approve_status = APPROVEChineseEnum.APPROVE_TRUE.value
            obj.save()
            """
            err, fake_mdinfo = offlinePred(obj_json)
            if len(err.keys()) > 0:
                obj.status = PublishStatusChineseEnum.FAILD.value
                obj.save()
                detect_logger().error(f"{err}")
                return
            model_version = fake_mdinfo["model_version"]
            model_id = fake_mdinfo["model_id"]
            """

            config_data = {'initiator': {'party_id': '', 'role': 'guest'},
                           'role': {'guest': []},
                           'job_parameters': {'model_id': '',
                                              'model_version': ''}}

            try:
                deploy_res = federated_api(job_id=job_utils.generate_job_id(),
                                           method='POST',
                                           endpoint='/model/deploy',
                                           src_party_id=config.local_party_id,
                                           dest_party_id=config.local_party_id,
                                           src_role="guest",
                                           json_body={"model_id": model_id, "model_version": model_version},
                                           federated_mode=federated_mode)
                if deploy_res["retcode"]:
                    obj.service_end_time = datetime_format(datetime.now())
                    obj.publish_result = "deploy_error retmsg" + deploy_res["retmsg"] + " deploy_res " + str(deploy_res)
                    obj.status = PublishStatusChineseEnum.FAILD.value
                    obj.save()
                    return

                deploy_data = deploy_res["data"]
                if deploy_data.get("host"):
                    config_data["role"]["host"] = list(deploy_data.get("host").keys())
                guest = list(deploy_data["guest"].keys())
                arbiter = deploy_data.get("arbiter")
                initiator_party_id = guest[0]
                config_data["initiator"]["party_id"] = initiator_party_id
                config_data["role"]["guest"] = guest
                config_data["job_parameters"]["model_id"] = deploy_data["model_id"]
                config_data["job_parameters"]["model_version"] = deploy_data["model_version"]
                config_data["service_id"] = service_name
                if arbiter:
                    config_data["role"]["arbiter"] = list(arbiter.keys())
                load_res = federated_api(job_id=job_utils.generate_job_id(),
                                         method='POST',
                                         endpoint='/model/load',
                                         src_party_id=config.local_party_id,
                                         dest_party_id=config.local_party_id,
                                         src_role=RoleTypeEnum.GUEST.value,
                                         json_body=config_data,
                                         federated_mode=federated_mode)
                if load_res["retcode"]:
                    obj.service_end_time = datetime_format(datetime.now())
                    obj.publish_result = "load_error retmsg" + load_res["retmsg"] + " load_res " + str(load_res)
                    stat_logger.exception(str(load_res))
                    obj.status = PublishStatusChineseEnum.FAILD.value
                    obj.save()
                    raise Exception(str(obj.publish_result ))

                bind_config = deepcopy(config_data)
                bind_config["servings"] = []
                bind_config["service_id"] = service_name
                bind_res = federated_api(job_id=job_utils.generate_job_id(),
                                         method='POST',
                                         endpoint='/model/bind',
                                         src_party_id=config.local_party_id,
                                         dest_party_id=config.local_party_id,
                                         src_role="guest",
                                         json_body=bind_config,
                                         federated_mode=federated_mode)
                if bind_res["retcode"]:
                    obj.service_end_time = datetime_format(datetime.now())
                    obj.publish_result = "bind_error retmsg" + bind_res["retmsg"] + " bind_res " + str(bind_res)
                    obj.status = PublishStatusChineseEnum.FAILD.value
                    obj.save()
                    raise Exception(str(obj.publish_result ))

            except Exception as e:
                obj.service_end_time = datetime_format(datetime.now())
                obj.publish_result = "unknown exception error  " + str(e)
                obj.status = PublishStatusChineseEnum.FAILD.value
                obj.save()
                stat_logger.exception(e)

                cls.notify_host_publish_return(hosts, federated_mode, model_id, model_version, obj, status)
                return
            # 更新状态
            # todo 多方更新？每次deploy都会有新的model_id 生成
            obj.service_end_time = datetime_format(datetime.now())
            obj.publish_result = "success"
            obj.status = PublishStatusChineseEnum.PUBLISHED.value
            obj.save()
            status = PublishStatusChineseEnum.PUBLISHED.value
            cls.notify_host_publish_return(hosts, federated_mode, model_id, model_version, obj,status)
        except Exception as e:
            detect_logger().exception(e)
        finally:
            detect_logger().info('finish detect running job')

    @classmethod
    def notify_host_publish_return(cls, hosts, federated_mode, model_id, model_version, obj,status):
        error_info = {}
        for _party_id in hosts:
            update_status_body = {
                "model_id": model_id,
                "model_version": model_version,
                "role_type": RoleTypeEnum.HOST.value,
                "party_id": _party_id,
                "status": status
            }
            try:
                update_res = federated_api(job_id=job_utils.generate_job_id(),
                                           method='POST',
                                           endpoint='/model_manage_schedule/model_update_status',
                                           src_party_id=config.local_party_id,
                                           dest_party_id=_party_id,
                                           src_role=RoleTypeEnum.GUEST.value,
                                           json_body=update_status_body,
                                           federated_mode=federated_mode)
                if update_res["retcode"]:
                    error_info[_party_id] = update_res["retmsg"]
            except Exception as e:
                error_info[_party_id] = str(e)
                obj.service_end_time = datetime_format(datetime.now())
                obj.publish_result = str(obj.publish_result) + str(error_info)
                obj.status = status
                obj.save()

    def detect_sample_status(cls):
        detect_logger().info('start detect sample_status')
        st =time.time()
        #第一次 审批，修改为过期
        host_samples_ids = StudioSampleInfo.select(StudioSampleInfo.id) \
            .join(StudioSampleAuthorize, join_type='INNER', on=(StudioSampleInfo.id == StudioSampleAuthorize.sample_id)). \
            where(StudioSampleInfo.owner == OwnerEnum.OTHER.value,
                  operator.or_(StudioSampleAuthorize.current_fusion_count >= StudioSampleAuthorize.fusion_times_limits,
                               StudioSampleAuthorize.fusion_deadline < get_format_time().date())).distinct()
        StudioSampleInfo.update({"status": SampleStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value,
                                 "publish_status": SamplePublishStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value}).where(
            StudioSampleInfo.id.in_([i.id for i in host_samples_ids])).execute()
        #当多次审批时，截止日斯往后延，样本仍可用
        host_samples_ids = StudioSampleInfo.select(StudioSampleInfo.id) \
            .join(StudioSampleAuthorize, join_type='INNER',
                  on=(StudioSampleInfo.id == StudioSampleAuthorize.sample_id)). \
            where(StudioSampleInfo.owner == OwnerEnum.OTHER.value,
                  StudioSampleAuthorize.fusion_deadline >= get_format_time().date(),
                  StudioSampleAuthorize.approve_result==SampleStatusEnum.VALID.value,
                  operator.or_(StudioSampleAuthorize.current_fusion_count < StudioSampleAuthorize.fusion_times_limits,
                               StudioSampleAuthorize.fusion_times_limits == None)
                  ).distinct().execute()
        StudioSampleInfo.update({"status": SampleStatusEnum.VALID.value,
                                 "publish_status": SamplePublishStatusEnum.PUBLISHED.value}).where(
            StudioSampleInfo.id.in_([i.id for i in host_samples_ids])).execute()
        detect_logger().info('end detect sample_status %s'%(time.time()-st))


def offlinePred(mdl_info):
    job_content = json.loads(mdl_info["job_content"])
    for v,p in job_content.get("model_versions", []):
        if p[0].lower().find("predict") == 0: return {}, v

    try:
        fake_mdinfo, cpn_lst = publish_model.fakePredict(job_content, config.local_party_id)
        publish_model.composeDAG(job_content, "guest", fake_mdinfo, config.local_party_id, cpn_lst)
    except Exception as e:
        return {"guest": str(e)}, None
    error_info = {}
    for h in list(set(model_id_get_hosts(mdl_info["id"]))):
        try:
            res = federated_api(job_id=job_utils.generate_job_id(),
                                           method='POST',
                                           endpoint='/model_manage/host_compose_dag',
                                           src_party_id=config.local_party_id,
                                           dest_party_id=int(h),
                                           src_role=RoleTypeEnum.GUEST.value,
                                           json_body={"fake_model_info": fake_mdinfo, "component_list": cpn_lst, "job_content": job_content},
                                           federated_mode=ENGINES["federated_mode"])
            if res["retcode"]:
                error_info[h] = res["retmsg"]
        except Exception as e:
            error_info[h] = str(e)

    return error_info, fake_mdinfo


