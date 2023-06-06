import re
from datetime import datetime

from flask_login import current_user
from peewee import JOIN

from fate_flow.web_server.db.db_models import StudioModelInfoExtend, StudioProjectInfo, StudioProjectUsedModel, \
    StudioJobContent
from fate_flow.web_server.db_service.common_service import CommonService
from fate_flow.db.db_models import DB, Job
from fate_flow.web_server.utils.common_util import datetime_format, get_uuid, get_format_time
from fate_flow.web_server.utils.enums import RoleTypeEnum, APPROVEChineseEnum


class ModelInfoExtendService(CommonService):
    model = StudioModelInfoExtend

    @classmethod
    @DB.connection_context()
    def get_by_role(cls, role_type):
        cols = [cls.model.id, cls.model.name, cls.model.version, cls.model.job_id, cls.model.job_name,
                cls.model.sample_id, cls.model.sample_name, cls.model.project_id, cls.model.project_name,
                cls.model.initiator_party_id, cls.model.initiator_party_name, cls.model.status, Job.f_roles,
                cls.model.create_time,cls.model.mix_type,cls.model.approve_status,cls.model.service_reason,
                cls.model.file_name,cls.model.service_name, cls.model.creator]
        if role_type ==RoleTypeEnum.GUEST.value:
            cols.append(StudioJobContent.canvas_id)
            auth_projects = current_user.get_auth_projects()
            objs = cls.model.select(*cols).join(Job, on=(cls.model.version == Job.f_job_id),
                                                join_type=JOIN.LEFT_OUTER).join(StudioJobContent,on=(cls.model.version == StudioJobContent.job_id)).where(cls.model.project_id.in_(auth_projects),
                                                                             cls.model.role_type == role_type)
        else:
            objs = cls.model.select(*cols).join(Job, on=(cls.model.version == Job.f_job_id),
                                                join_type=JOIN.LEFT_OUTER).where(
                cls.model.role_type == role_type)
        return objs
    @classmethod
    @DB.connection_context()
    def get_import_model(cls, role_type):
        cols = [cls.model.id, cls.model.name, cls.model.version, cls.model.job_id, cls.model.job_name,
                cls.model.sample_id, cls.model.sample_name, cls.model.project_id, cls.model.project_name,
                cls.model.initiator_party_id, cls.model.initiator_party_name, cls.model.status,
                cls.model.create_time, cls.model.mix_type, cls.model.approve_status, cls.model.service_reason,
                cls.model.file_name,cls.model.service_name, cls.model.creator]
        if current_user.is_superuser:
            objs = cls.model.select(*cols).where(
                cls.model.role_type == role_type, cls.model.job_id == None)
        else:
            objs = cls.model.select(*cols).where(
                cls.model.role_type == role_type, cls.model.job_id == None,cls.model.creator==current_user.username)
        return objs
    @classmethod
    @DB.connection_context()
    def update_by_key(cls, model_id, model_version, role_type, party_id, user, **kwargs):
        update_dict = {cls.model.updator: user,
                       cls.model.update_time: datetime_format(datetime.now())}
        update_dict.update(kwargs)
        with DB.atomic():
            update_obj = cls.model.update(update_dict).where(
                cls.model.id == model_id, cls.model.version == model_version, cls.model.role_type == role_type,
                cls.model.party_id == party_id)
            res = update_obj.execute()



    @classmethod
    @DB.connection_context()
    def count_no_approve(cls):
        with DB.atomic():
            return cls.model.select().where(cls.model.role_type == RoleTypeEnum.HOST.value,
                                            cls.model.approve_status == APPROVEChineseEnum.APPROVE_WAITING.value).count()



class ProjectUsedModelService(CommonService):
    model = StudioProjectUsedModel

    @classmethod
    @DB.connection_context()
    def create_by_info(cls,project_id,job_id,job_type,model_id,model_version,canvas_id,user_name):
        used_model_dict = {
            "id": get_uuid(),
            "project_id": project_id,
            "model_id": model_id,
            "model_version": model_version,
            "mix_type": job_type,
            "job_id": job_id,
            "canvas_id": canvas_id,
            "creator": user_name,
            "create_time": get_format_time()
        }
        cls.model(**used_model_dict).save(force_insert=True)

