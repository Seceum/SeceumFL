from datetime import datetime
from fate_flow.web_server.db.db_models import StudioProjectInfo, StudioProjectSample, StudioProjectUser, StudioAuthUser, \
    StudioSampleInfo, StudioVSampleInfo, StudioProjectParty, StudioPartyInfo, \
    StudioProjectUsedSample, StudioProjectCanvas
from fate_flow.web_server.db_service.common_service import CommonService
from fate_flow.db.db_models import DB, Job, Task, MachineLearningModelInfo
from fate_flow.web_server.db_service.sample_service import SampleService
from fate_flow.web_server.utils.common_util import get_uuid, datetime_format, get_format_time
from fate_flow.web_server.utils.enums import StatusEnum, SampleTypeEnum, SampleStatusChineseEnum, SampleStatusEnum
from peewee import JOIN, fn
from collections import Counter


class ProjectInfoService(CommonService):
    model = StudioProjectInfo

    @classmethod
    @DB.connection_context()
    def get_join_sample(cls, role_type):
        cols = [StudioProjectInfo.id, StudioProjectInfo.name,
                StudioProjectInfo.comments,
                StudioProjectInfo.guest_party_id, StudioProjectInfo.create_time, StudioProjectInfo.update_time,
                StudioProjectSample.sample_id]
        project_objs = StudioProjectInfo.select(*cols).join(StudioProjectSample, join_type=JOIN.LEFT_OUTER,
                                                            on=(cls.model.id ==
                                                                StudioProjectSample.project_id)).where(
            StudioProjectInfo.status == StatusEnum.VALID.value,
            StudioProjectInfo.role_type == role_type)
        return project_objs

    @classmethod
    @DB.connection_context()
    def get_project(cls, role_type):
        cols = [StudioProjectInfo.id, StudioProjectInfo.name,
                StudioProjectInfo.comments,
                StudioProjectInfo.guest_party_id, StudioProjectInfo.create_time, StudioProjectInfo.update_time]
        project_objs = cls.model.select(*cols).where(cls.model.role_type == role_type,
                                                     cls.model.status == StatusEnum.VALID.value)
        return project_objs

    @classmethod
    @DB.connection_context()
    def create_project(cls, project_data, user_ids, party_ids):
        with DB.atomic():
            cls.model(**project_data).save(force_insert=True)
            project_id = project_data["id"]
            user = project_data["creator"]
            create_time = datetime_format(datetime.now())
            if user_ids:
                project_user_data = []
                for user_id in user_ids:
                    user_dict = {
                        "id": get_uuid(),
                        "project_id": project_id,
                        "user_id": user_id,
                        "creator": user,
                        "create_time": create_time,
                    }
                    project_user_data.append(user_dict)
                StudioProjectUser.insert_many(project_user_data).execute()
            project_party_data = []
            for party_id in party_ids:
                user_dict = {
                    "id": get_uuid(),
                    "project_id": project_id,
                    "party_id": party_id,
                    "creator": user,
                    "create_time": create_time,
                }
                project_party_data.append(user_dict)
            if project_party_data:
                StudioProjectParty.insert_many(project_party_data).execute()

    @classmethod
    @DB.connection_context()
    def sum_count_by_party(cls):
        party_objs = cls.model.select(StudioProjectParty.party_id).join(
            StudioProjectParty, on=(
                    cls.model.id == StudioProjectParty.project_id)).where(
            cls.model.status == StatusEnum.VALID.value)
        party_list = [i["party_id"] for i in party_objs.dicts()]
        return dict(Counter(party_list))


class ProjectUserService(CommonService):
    model = StudioProjectUser

    @classmethod
    @DB.connection_context()
    def get_join_users(cls, project_ids):
        return cls.model.select(cls.model.project_id, StudioAuthUser.id.alias("user_id"), StudioAuthUser.username).join(
            StudioAuthUser, on=(
                    cls.model.user_id == StudioAuthUser.id), join_type=JOIN.LEFT_OUTER).where(
            cls.model.project_id.in_(project_ids))

    @classmethod
    @DB.connection_context()
    def update_by_project(cls, project_id, user_ids, user):
        obj = cls.model.select().where(cls.model.project_id == project_id)
        project_user_data = []
        with DB.atomic():
            if obj:
                create_time = obj.get().create_time
                cls.model.delete().where(cls.model.project_id == project_id).execute()
                current = datetime_format(datetime.now())
                for user_id in user_ids:
                    user_dict = {
                        "id": get_uuid(),
                        "project_id": project_id,
                        "user_id": user_id,
                        "creator": user,
                        "create_time": create_time,
                        "update_time": current,
                    }
                    project_user_data.append(user_dict)
            else:
                create_time = datetime_format(datetime.now())
                for user_id in user_ids:
                    user_dict = {
                        "id": get_uuid(),
                        "project_id": project_id,
                        "user_id": user_id,
                        "creator": user,
                        "create_time": create_time,
                    }
                    project_user_data.append(user_dict)
            if project_user_data:
                cls.model.insert_many(project_user_data).execute()


class JobService(CommonService):
    model = Job


class ProjectSampleService(CommonService):
    model = StudioProjectSample

    @classmethod
    @DB.connection_context()
    def join_by_sample(cls, project_id, filters=None, cols=None):
        filters = filters if filters else []
        if cols:
            objs = cls.model.select(*cols).join(StudioSampleInfo,
                                                on=(cls.model.sample_id == StudioSampleInfo.id)).where(
                cls.model.project_id == project_id, cls.model.sample_type == SampleTypeEnum.ORIGIN.value, *filters)
        else:
            objs = cls.model.select().join(StudioSampleInfo, on=(cls.model.sample_id == StudioSampleInfo.id)).where(
                cls.model.project_id == project_id, cls.model.sample_type == SampleTypeEnum.ORIGIN.value, *filters)
        return objs

    @classmethod
    @DB.connection_context()
    def join_by_Vsample(cls, project_id, filters=None, cols=None):
        filters = filters if filters else []
        if cols:
            objs = cls.model.select(*cols).join(StudioVSampleInfo,
                                                on=(cls.model.sample_id == StudioVSampleInfo.id)).where(
                cls.model.project_id == project_id, cls.model.sample_type == SampleTypeEnum.FUSION.value,
                *filters).order_by(cls.model.getter_by("create_time").desc())
        else:
            objs = cls.model.select().join(StudioVSampleInfo, on=(cls.model.sample_id == StudioVSampleInfo.id)).where(
                cls.model.project_id == project_id, cls.model.sample_type == SampleTypeEnum.FUSION.value,
                *filters).order_by(cls.model.getter_by("create_time").desc())
        return objs

    @classmethod
    @DB.connection_context()
    def update_by_project_bak(cls, project_id, sample_ids, user, sample_type=SampleTypeEnum.ORIGIN.value):
        obj = cls.model.select().where(cls.model.project_id == project_id, sample_type == sample_type)
        project_sample_data = []
        with DB.atomic():
            if obj:
                create_time = obj.get().create_time
                creator = obj.get().creator
                cls.model.delete().where(cls.model.project_id == project_id,
                                         cls.model.sample_type == sample_type).execute()
                current = datetime_format(datetime.now())
                for sample_id in sample_ids:
                    user_dict = {
                        "id": get_uuid(),
                        "project_id": project_id,
                        "sample_id": sample_id,
                        "updator": user,
                        "creator": creator,
                        "create_time": create_time,
                        "update_time": current,
                        "sample_type": sample_type,
                    }
                    project_sample_data.append(user_dict)
            else:
                create_time = datetime_format(datetime.now())
                for sample_id in sample_ids:
                    user_dict = {
                        "id": get_uuid(),
                        "project_id": project_id,
                        "sample_id": sample_id,
                        "creator": user,
                        "create_time": create_time,
                        "sample_type": sample_type
                    }
                    project_sample_data.append(user_dict)
            if project_sample_data:
                cls.model.insert_many(project_sample_data).execute()

    @classmethod
    @DB.connection_context()
    def update_by_project(cls, project_id, sample_ids, user, sample_type=SampleTypeEnum.ORIGIN.value):
        exist_sample_ids = [i.sample_id for i in
                            cls.model.select().where(cls.model.project_id == project_id, sample_type == sample_type)]
        project_sample_data = []
        insert_sample_ids = set(sample_ids).difference(set(exist_sample_ids))
        create_time = datetime_format(datetime.now())
        for sample_id in insert_sample_ids:
            user_dict = {
                "id": get_uuid(),
                "project_id": project_id,
                "sample_id": sample_id,
                "creator": user,
                "create_time": create_time,
                "sample_type": sample_type
            }
            project_sample_data.append(user_dict)
        if project_sample_data:
            cls.model.insert_many(project_sample_data).execute()

    @classmethod
    def get_v_sample_status(cls, party_info,sample_status_dict):
        sample_infos = party_info["host"]
        sample_infos.insert(0, party_info["guest"])
        for i in sample_infos:
            sample_status = sample_status_dict.get(i["sample_id"])
            if not sample_status:
                return SampleStatusChineseEnum.NOT_FIND.value
            elif sample_status==SampleStatusEnum.DELETE.value:
                return SampleStatusChineseEnum.DELETE.value
            elif sample_status==SampleStatusEnum.OFF_LINE.value:
                return SampleStatusChineseEnum.OFF_LINE.value
            elif sample_status==SampleStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value:
                return SampleStatusChineseEnum.OFF_LINE.value
        return SampleStatusChineseEnum.VALID.value

    @classmethod
    def get_sample_status(cls, v_sample_party_infos):
        all_origin_sample_list = []
        for v_sample_obj in v_sample_party_infos:
            sample_infos = v_sample_obj["host"]
            sample_infos.insert(0, v_sample_obj["guest"])
            all_origin_sample_list.extend([i["sample_id"] for i in sample_infos])
        sample_status_list = SampleService.query(
            filters=[SampleService.model.id.in_(list(set(all_origin_sample_list)))]).dicts()
        sample_status_dict = {i["id"]: i["status"] for i in sample_status_list}
        return sample_status_dict
    # @classmethod
    # @DB.connection_context()
    # def delete_by_sample(cls, project_id, sample_id):
    #     num = cls.model.delete().where(cls.model.project_id == project_id, cls.model.sample_id == sample_id).execute()
    #     return num


class TaskService(CommonService):
    model = Task

    @classmethod
    @DB.connection_context()
    def get_run_ip(cls, job_id, role, party_id):
        return cls.model.select(cls.model.f_run_ip, cls.model.f_create_time).where(cls.model.f_job_id == job_id,
                                                                                   cls.model.f_role == role,
                                                                                   cls.model.f_party_id == party_id,
                                                                                   cls.model.f_run_ip.is_null(
                                                                                       False)).order_by(
            cls.model.f_create_time.asc())

    @classmethod
    @DB.connection_context()
    def get_fusion_task(cls, job_id, role, party_id, only_latest=True):
        fusion_tuple = ('Intersection', 'Union')
        objs = cls.model.select().where(cls.model.f_job_id == job_id, cls.model.f_role == role,
                                        cls.model.f_party_id == party_id, cls.model.f_component_module.in_(
                fusion_tuple)).order_by(cls.model.f_create_time.asc())
        if only_latest and objs:
            objs = objs.first()
        return objs


class MLModelService(CommonService):
    model = MachineLearningModelInfo


class ProjectUsedSampleService(CommonService):
    model = StudioProjectUsedSample

    @classmethod
    @DB.connection_context()
    def insert_by_party_info(cls, project_id, canvas_id, job_id, party_info, sample_type, user_name):
        save_used_sample = []
        used_sample_list = [party_info["guest"]]
        used_sample_list.extend(party_info["host"])
        create_time = get_format_time()
        for used_info in used_sample_list:
            save_used_sample.append({
                "id": get_uuid(),
                "project_id": project_id,
                "sample_id": used_info["sample_id"],
                "party_id": used_info["party_id"],
                "sample_type": sample_type,
                "job_id": job_id,
                "canvas_id": canvas_id,
                "create_time": create_time,
                "creator": user_name
            })
        cls.model.insert_many(save_used_sample).execute()

    @classmethod
    @DB.connection_context()
    def insert_by_ids(cls, project_id, canvas_id, job_id, sample_ids, sample_type, user_name, party_id=None):
        save_used_sample = []
        create_time = get_format_time()
        for fusion_sample_id in sample_ids:
            temp_dict = {
                "id": get_uuid(),
                "project_id": project_id,
                "sample_id": fusion_sample_id,
                "sample_type": sample_type,
                "job_id": job_id,
                "party_id": party_id,
                "canvas_id": canvas_id,
                "create_time": create_time,
                "creator": user_name
            }
            save_used_sample.append(temp_dict)
        if save_used_sample:
            cls.model.insert_many(save_used_sample).execute()
    @classmethod
    @DB.connection_context()
    def join_by_sample(cls, project_id, filters=None, cols=None):
        filters = filters if filters else []
        if cols:
            objs = cls.model.select(*cols).join(StudioSampleInfo,
                                                on=(cls.model.sample_id == StudioSampleInfo.id)).where(
                cls.model.project_id == project_id, cls.model.sample_type == SampleTypeEnum.ORIGIN.value, *filters)
        else:
            objs = cls.model.select().join(StudioSampleInfo, on=(cls.model.sample_id == StudioSampleInfo.id)).where(
                cls.model.project_id == project_id, cls.model.sample_type == SampleTypeEnum.ORIGIN.value, *filters)
        return objs
class ProjectCanvasService(CommonService):
    model = StudioProjectCanvas


class ProjectPartyService(CommonService):
    model = StudioProjectParty

    @classmethod
    @DB.connection_context()
    def get_join_party(cls, project_ids):
        return cls.model.select(cls.model.project_id, cls.model.party_id, StudioPartyInfo.party_name).join(
            StudioPartyInfo, on=(
                    cls.model.party_id == StudioPartyInfo.id), join_type=JOIN.LEFT_OUTER).where(
            cls.model.project_id.in_(project_ids))

    @classmethod
    @DB.connection_context()
    def update_by_project(cls, project_id, party_ids, user):
        obj = cls.model.select().where(cls.model.project_id == project_id)
        project_user_data = []
        with DB.atomic():
            if obj:
                create_time = obj.get().create_time
                cls.model.delete().where(cls.model.project_id == project_id).execute()
                current = datetime_format(datetime.now())
                for party_id in party_ids:
                    user_dict = {
                        "id": get_uuid(),
                        "project_id": project_id,
                        "party_id": party_id,
                        "creator": user,
                        "create_time": create_time,
                        "update_time": current,
                    }
                    project_user_data.append(user_dict)
            else:
                create_time = datetime_format(datetime.now())
                for party_id in party_ids:
                    user_dict = {
                        "id": get_uuid(),
                        "project_id": project_id,
                        "party_id": party_id,
                        "creator": user,
                        "create_time": create_time,
                    }
                    project_user_data.append(user_dict)
            if project_user_data:
                cls.model.insert_many(project_user_data).execute()
