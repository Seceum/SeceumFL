from fate_flow.web_server.db.db_models import StudioJobContent
from fate_flow.web_server.db_service.common_service import CommonService
from fate_flow.db.db_models import DB
from fate_flow.web_server.utils.common_util import get_uuid, get_format_time


class JobContentService(CommonService):
    model = StudioJobContent

    @classmethod
    def create_by_func(cls, canvas_id, job_content, user_name, **kwargs):
        p_id = get_uuid()
        save_dict = {
            "id": p_id,
            "canvas_id": canvas_id,
            "job_content": job_content,
            "is_latest": True,
            "creator": user_name,
        }
        for k, v in kwargs.items():
            if v:
                save_dict[k] = v
        cls.model(**save_dict).save(force_insert=True)
        return p_id


    @classmethod
    @DB.connection_context()
    def create_conf(cls, canvas_id, job_content_id, job_content, user_name, module_name,
                    job_name="", last_job_id=None, job_id=None, run_param=None,
                    party_info=None):
        with DB.atomic():
            # cls.model.update({"is_latest": False}).where(cls.model.canvas_id == canvas_id).execute() # drop is_latest
            if job_content_id:
                project_content_objs = cls.model.select().where(cls.model.id == job_content_id)
                if project_content_objs:
                    job_content_obj = project_content_objs[0]
                    if job_content_obj.job_id:
                        p_id = cls.create_by_func(canvas_id, job_content, user_name, module_name=module_name,
                                                  job_name=job_name,job_id=job_id, run_param=run_param,
                                                  party_info=party_info)
                    else:
                        p_id = job_content_obj.id
                        job_content_obj.job_content = job_content
                        job_content_obj.job_id = job_id
                        job_content_obj.run_param = run_param
                        job_content_obj.party_info = party_info
                        job_content_obj.job_name = job_name
                        # job_content_obj.is_latest = True # drop is_latest
                        job_content_obj.updator = user_name
                        job_content_obj.module_name = module_name
                        job_content_obj.last_job_id = last_job_id
                        job_content_obj.update_time = get_format_time()
                        job_content_obj.save()
                else:
                    p_id = cls.create_by_func(canvas_id, job_content, user_name, module_name=module_name,
                                              job_name=job_name, job_id=job_id, run_param=run_param,last_job_id=last_job_id,
                                              party_info=party_info)
            else:
                p_id = cls.create_by_func(canvas_id, job_content, user_name, module_name=module_name,
                                          job_name=job_name, job_id=job_id, run_param=run_param, last_job_id=last_job_id,
                                          party_info=party_info)
            return p_id

    @classmethod
    @DB.connection_context()
    def history_recover(cls, canvas_id, job_content_id):
        with DB.atomic():
            cls.model.update({"is_latest": False}).where(cls.model.canvas_id == canvas_id).execute()
            cls.model.update({"is_latest": True}).where(cls.model.id == job_content_id).execute()

    @classmethod
    @DB.connection_context()
    def get_latest(cls, canvas_id, cols=None):
        content_objs = JobContentService.query(canvas_id=canvas_id,
                                               # is_latest=True,
                                               reverse=True,
                                               order_by="create_time", cols=cols)

        if content_objs:
            return content_objs[0]
        else:
            return None

    @classmethod
    @DB.connection_context()
    def get_run_param(cls, job_id, cols=None):
        content_objs = JobContentService.query(job_id=job_id, cols=cols).dicts()

        if content_objs:
            return content_objs[0]
        else:
            return