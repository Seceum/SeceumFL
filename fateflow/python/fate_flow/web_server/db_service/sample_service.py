import operator
from collections import Counter
from datetime import datetime

import peewee
from flask_login import current_user

from fate_flow.db.db_models import DB
from fate_flow.web_server.db.db_models import StudioSampleInfo, StudioProjectSample, StudioProjectInfo, \
    StudioSampleFields, StudioSampleAuthorize, StudioPartyInfo, StudioVSampleInfo, StudioSampleAlgorithm, \
    StudioProjectUsedSample, StudioSampleAuthorizeHistory
from fate_flow.web_server.db_service.common_service import CommonService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.common_util import get_uuid, get_format_time, datetime_format
from fate_flow.web_server.utils.enums import OwnerEnum, StatusEnum, ApproveStatusEnum


class SampleService(CommonService):
    model = StudioSampleInfo

    @classmethod
    @DB.connection_context()
    def update_status(cls, party_id, sample_id, owner, user, **kwargs):
        update_dict = {cls.model.updator: user,
                       cls.model.update_time: get_format_time()}
        update_dict.update(kwargs)
        update_num = cls.model.update(update_dict).where(
            cls.model.id == sample_id, cls.model.party_id == party_id, cls.model.owner == owner).execute()
        return update_num

    @classmethod
    @DB.connection_context()
    def sample_join_projects(cls, sample_ids):
        # 项目状态有效、无效,
        # todo join 优化
        project_list = StudioProjectUsedSample.select(StudioProjectUsedSample.sample_id, StudioProjectUsedSample.project_id,
                                                  StudioProjectInfo.name).join(StudioProjectInfo, on=(
                StudioProjectUsedSample.project_id == StudioProjectInfo.id)).where(
            StudioProjectUsedSample.sample_id.in_(sample_ids), StudioProjectUsedSample.sample_type == OwnerEnum.OWN.value,
                                                           StudioProjectInfo.status == StatusEnum.VALID.value)
        return project_list

    @classmethod
    @DB.connection_context()
    def sample_join_party(cls, sample_ids):
        # todo join 优化
        project_list = cls.model.select(cls.model.id.alias('sample_id'), StudioPartyInfo.id.alias("party_id"),
                                        StudioPartyInfo.party_name).join(
            StudioPartyInfo, on=(cls.model.party_id == StudioPartyInfo.id)).where(cls.model.id.in_(sample_ids))
        return project_list

    @classmethod
    @DB.connection_context()
    def sample_info(cls):
        project_list = cls.model.select(cls.model.id, cls.model.name, cls.model.party_id,
                                        StudioPartyInfo.party_name, cls.model.owner).join(StudioPartyInfo,
                                                                                          join_type=peewee.JOIN.LEFT_OUTER,
                                                                                          on=(
                                                                                                  cls.model.party_id == StudioPartyInfo.id)).where(
            cls.model.status == StatusEnum.VALID.value)
        return project_list

    @classmethod
    @DB.connection_context()
    def sample_names(cls, sample_ids):
        #sample_ids: str or list of str
        if not sample_ids:return
        if isinstance(sample_ids, list) and len(sample_ids) == 1:sample_ids = sample_ids[0]

        if isinstance(sample_ids, str):
            return cls.model.select(cls.model.id, cls.model.name).where(cls.model.id == sample_ids).dicts()

        return cls.model.select(cls.model.id, cls.model.name).where(cls.model.id.in_(sample_ids)).dicts()

    @classmethod
    @DB.connection_context()
    def sample_name_type(cls, sample_ids):
        #sample_ids: str or list of str
        if not sample_ids:return
        if isinstance(sample_ids, list) and len(sample_ids) == 1:sample_ids = sample_ids[0]

        if isinstance(sample_ids, str):
            return cls.model.select(cls.model.id, cls.model.name,cls.model.type).where(cls.model.id == sample_ids).dicts()

        return cls.model.select(cls.model.id, cls.model.name,cls.model.type).where(cls.model.id.in_(sample_ids)).dicts()

    @classmethod
    @DB.connection_context()
    def get_auth_sample(cls, cols=None, filters=None):
        filters = filters if filters else []
        auth_sample_objs = cls.model.select(*cols).join(StudioSampleAuthorize, join_type=peewee.JOIN.LEFT_OUTER,
                                                        on=(cls.model.id == StudioSampleAuthorize.sample_id)).where(
            *filters)
        return auth_sample_objs

    @classmethod
    @DB.connection_context()
    def query_publish_sample(cls):
        project_list = cls.model.select(cls.model.id, cls.model.name, cls.model.sample_type, cls.model.type,
                                        cls.model.comments, cls.model.create_time).where(
            cls.model.owner == OwnerEnum.OWN.value, cls.model.publish_status == StatusEnum.VALID.value)
        return project_list

    @classmethod
    @DB.connection_context()
    def create_sample(cls, sample_dict, field_list, batch_size=100):
        with DB.atomic():
            cls.model(**sample_dict).save(force_insert=True)
            # for i in range(0, len(field_list), batch_size):
            #     StudioSampleFields.insert_many(field_list[i:i + batch_size]).execute()
            for i in field_list:
                StudioSampleFields(**i).save(force_insert=True)

    @classmethod
    @DB.connection_context()
    def sum_count_by_party(cls, owner, status):
        return cls.model.select(cls.model.party_id, peewee.fn.COUNT(cls.model.party_id).alias(
            "open_sample_count")).where(cls.model.owner == owner, cls.model.status == status).group_by(
            cls.model.party_id)

    @classmethod
    @DB.connection_context()
    def sum_count_by_party(cls, owner, status):
        party_objs = cls.model.select(cls.model.party_id).where(cls.model.owner == owner, cls.model.status == status)
        party_list = [i["party_id"] for i in party_objs.dicts()]
        return dict(Counter(party_list))



class SampleFieldsService(CommonService):
    model = StudioSampleFields

    @classmethod
    @DB.connection_context()
    def get_by_sample_info(cls, sample_ids, cols, **kwargs):
        filters = []
        for k, v in kwargs.items():
            filters.append(operator.attrgetter(k)(cls.model) == v)
        feature_objs = cls.model.select(*cols).join(StudioSampleInfo, on=(
                cls.model.sample_id == StudioSampleInfo.id)).where(StudioSampleInfo.id.in_(sample_ids), *filters)
        return feature_objs


    @classmethod
    @DB.connection_context()
    def is_samples_field_different(cls, sample_ids):
        fnms = set([])
        nm = ""
        for id in sample_ids:
            rcds = cls.model.select(cls.model.field_name, StudioSampleInfo.name)\
                .join(StudioSampleInfo, on=(cls.model.sample_id == StudioSampleInfo.id))\
                .where(cls.model.sample_id == id).dicts()

            if not nm: nm = rcds[0]["name"]
            flds = set([r["field_name"] for r in rcds])
            if len(fnms) == 0: fnms = flds
            if len(fnms)!= len(flds) or len(fnms | flds) > len(fnms):
                return (nm, rcds[0]["name"])
    @classmethod
    @DB.connection_context()
    def delete_by_sample_id(cls, sample_id):
        cls.model.delete().where(cls.model.sample_id == sample_id).execute()

class VSampleInfoService(CommonService):
    model = StudioVSampleInfo


class SampleAuthorizeService(CommonService):
    model = StudioSampleAuthorize

    @classmethod
    @DB.connection_context()
    def get_apply_party(cls, sample_id):
        # todo join 优化
        party_info_objs = cls.model.select(StudioPartyInfo.id, StudioPartyInfo.train_party_ip,
                                           StudioPartyInfo.train_party_ip).join(StudioPartyInfo, on=(
                cls.model.apply_party_id == StudioPartyInfo.id)).where(cls.model.sample_id == sample_id,
                                                                       cls.model.owner == OwnerEnum.OWN.value,
                                                                       cls.model.approve_party_id == config.local_party_id)
        return party_info_objs

    @classmethod
    @DB.connection_context()
    def get_apply_auth(cls, approve_party_id, apply_party_id, owner=OwnerEnum.OTHER.value):
        return cls.model.select(cls.model.sample_id, cls.model.approve_result).where(
            cls.model.owner == owner, cls.model.approve_party_id == approve_party_id,
            cls.model.apply_party_id == apply_party_id)

    @classmethod
    @DB.connection_context()
    def update_auth_status(cls, approve_party_id, apply_party_id, sample_id, owner, approve_result, user):
        with DB.atomic():
            update_dict = {cls.model.approve_result: approve_result,
                           cls.model.updator: user,
                           cls.model.update_time: get_format_time()}
            update_obj = cls.model.update(update_dict).where(
                cls.model.sample_id == sample_id,
                cls.model.approve_party_id == approve_party_id,
                cls.model.apply_party_id == apply_party_id,
                cls.model.owner == owner)
            update_obj.execute()

    @classmethod
    @DB.connection_context()
    def update_by_id(cls, pid, **kwargs):
        with DB.atomic():
            update_obj = cls.model.update(kwargs).where(cls.model.id == pid)
            update_obj.execute()

    @classmethod
    @DB.connection_context()
    def get_or_create(cls, approve_party_id, apply_party_id, sample_id, owner, approve_result, user,
                      algorithm_sample_list=None, history=None,auth_obj=None, **kwargs):
        with DB.atomic():
            try:
                cls.model.select().where(cls.model.approve_party_id == approve_party_id,
                                         cls.model.apply_party_id == apply_party_id,
                                         cls.model.sample_id == sample_id, cls.model.owner == owner).get()
                update_dict = {
                    "approve_result": approve_result,
                    "updator": user,
                    "update_time": get_format_time(),
                }
                temp_dict = {k: v for k, v in kwargs.items() if
                             k in ["approve_time", "approve_result", "fusion_times_limits", "fusion_deadline",
                                   "fusion_limit", "apply_time"]}
                update_dict.update(temp_dict)
                if approve_result in [ApproveStatusEnum.CANCEL_AUTH.value, ApproveStatusEnum.REJECT.value]:
                    update_dict["fusion_deadline"] = None
                    update_dict["fusion_limit"] = None
                    update_dict["fusion_times_limits"] = None
                    update_dict["current_fusion_count"] = 0
                elif approve_result == ApproveStatusEnum.APPLY.value:
                    update_dict["approve_time"] = None
                elif approve_result == ApproveStatusEnum.AGREE.value and not update_dict.get("fusion_limit"):
                    update_dict["fusion_times_limits"] = None
                    update_dict["current_fusion_count"] = 0
                cls.model.update(update_dict).where(cls.model.approve_party_id == approve_party_id,
                                                    cls.model.apply_party_id == apply_party_id,
                                                    cls.model.sample_id == sample_id,
                                                    cls.model.owner == owner).execute()
                if history:#样本审批历史表
                    sample_obj = StudioSampleInfo.get_or_none(id=sample_id)
                    update_dict["sample_type"]  = sample_obj.sample_type
                    update_dict["apply_party_name"] =auth_obj.apply_party_name
                    update_dict["sample_name"] =sample_obj.name
                    update_dict["apply_time"] =auth_obj.apply_time
                    update_dict["approve_party_id"]=approve_party_id
                    update_dict["apply_party_id"]=apply_party_id
                    update_dict["sample_id"]=sample_id
                    update_dict["algorithm_name"]=",".join([al_obj["algorithm_name"] for al_obj in  algorithm_sample_list])
                    update_dict["id"] = get_uuid()
                    update_dict["approve_username"] = current_user.username
                    StudioSampleAuthorizeHistory(**update_dict).save(force_insert=True)
            except peewee.DoesNotExist:
                date_time_apply = get_format_time()
                create_dict = {
                    "id": get_uuid(),
                    "approve_result": approve_result,
                    "approve_party_id": approve_party_id,
                    "apply_party_id": apply_party_id,
                    "sample_id": sample_id,
                    "owner": owner,
                    "apply_time": date_time_apply,
                    "approve_time": date_time_apply,
                    "creator": user}
                create_dict.update(**kwargs)
                cls.model(**create_dict).save(force_insert=True)
            algorithm_sample_list = algorithm_sample_list if algorithm_sample_list else []
            if algorithm_sample_list and approve_result == ApproveStatusEnum.AGREE.value:
                StudioSampleAlgorithm.delete().where(StudioSampleAlgorithm.sample_id == sample_id).execute()
                StudioSampleAlgorithm.insert_many(algorithm_sample_list).execute()
            elif approve_result in [ApproveStatusEnum.CANCEL_AUTH.value, ApproveStatusEnum.REJECT.value]:
                StudioSampleAlgorithm.delete().where(StudioSampleAlgorithm.sample_id == sample_id).execute()

    @classmethod
    @DB.connection_context()
    def get_auth_sample(cls, owner=OwnerEnum.OTHER.value):
        cols = [cls.model.id, cls.model.sample_id, StudioSampleInfo.name, StudioSampleInfo.sample_type,
                cls.model.apply_party_id, cls.model.apply_party_name, cls.model.apply_time, cls.model.approve_party_id,
                cls.model.approve_party_name, cls.model.approve_result, cls.model.approve_time, cls.model.create_time,
                cls.model.current_fusion_count, cls.model.fusion_deadline, cls.model.fusion_limit,
                cls.model.total_fusion_count, cls.model.fusion_times_limits, ]
        auth_objs = cls.model.select(*cols).join(StudioSampleInfo,
                                                 on=(cls.model.sample_id == StudioSampleInfo.id)).where(
            cls.model.owner == owner).order_by(cls.model.create_time.desc())

        return auth_objs

    @classmethod
    @DB.connection_context()
    def update_auth(cls, auth_id, sample_id, update_auth_dicts, algorithm_sample_list):
        with DB.atomic():
            cls.model.update(update_auth_dicts).where(cls.model.id == auth_id).execute()
            if StudioSampleAlgorithm.query(sample_id):
                StudioSampleAlgorithm.delete().where(sample_id=sample_id).execute()
            if algorithm_sample_list:
                StudioSampleAlgorithm.insert_many(algorithm_sample_list)

    @classmethod
    @DB.connection_context()
    def count_no_approve(cls):
        return cls.model.select().where(cls.model.owner == OwnerEnum.OWN.value,
                                        cls.model.approve_result == ApproveStatusEnum.APPLY.value
                                        ).count()

    @classmethod
    @DB.connection_context()
    def auth_add_count(cls, party_info, num=1):
        with DB.atomic():
            for out_party in party_info["host"]:
                auth_objs = cls.model.select().where(cls.model.sample_id == out_party["sample_id"],
                                                     cls.model.apply_party_id == config.local_party_id,
                                                     cls.model.approve_party_id == out_party["party_id"])

                if auth_objs and auth_objs[0].approve_result in [ApproveStatusEnum.APPLY.value,
                                                                 ApproveStatusEnum.AGREE.value]:
                    auth_obj = auth_objs[0]
                    auth_obj.current_fusion_count = auth_obj.current_fusion_count + num
                    auth_obj.total_fusion_count = auth_obj.total_fusion_count + num
                    auth_obj.save()

class SampleAuthorizeHistoryService(CommonService):
    model = StudioSampleAuthorizeHistory

    @classmethod
    @DB.connection_context()
    def get_sample_history_by_smaple_id(cls,smaple_id):
        cols = [cls.model.id, cls.model.sample_id, cls.model.sample_name, cls.model.algorithm_name,
                cls.model.apply_party_id, cls.model.apply_party_name, cls.model.apply_time, cls.model.approve_party_id,
                cls.model.approve_party_name, cls.model.approve_result, cls.model.approve_time, cls.model.create_time,
                cls.model.current_fusion_count, cls.model.fusion_deadline, cls.model.fusion_limit,
                cls.model.total_fusion_count, cls.model.fusion_times_limits,cls.model.sample_type,cls.model.approve_username]
        auth_objs = cls.model.select(*cols).where(cls.model.sample_id==smaple_id).order_by(cls.model.create_time.desc())
        return auth_objs
