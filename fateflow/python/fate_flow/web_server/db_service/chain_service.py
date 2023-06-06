from fate_flow.db.db_models import DB
from fate_flow.web_server.db.db_models import StudioChainInfo
from fate_flow.web_server.db_service.common_service import CommonService


class ChainService(CommonService):
    model = StudioChainInfo
    #
    # @classmethod
    # @DB.connection_context()
    # def update_by_project_bak(cls, project_id, sample_ids, user, sample_type=SampleTypeEnum.ORIGIN.value):
    #     # obj = cls.model.select().where(cls.model.project_id == project_id, sample_type == sample_type)
    #     # project_sample_data = []
    #     with DB.atomic():
    #         data = {
    #             "id": get_uuid(),
    #             "type": "party",
    #             "is_latest": False,
    #             "last_store_time": None,
    #             "store_data": data,
    #             "store_return": "123",
    #             # "creator":None,
    #             # "store_return":"123",
    #             # "store_return":"123",
    #             # "store_return": res["data"],
    #         }
    #         res = store_send(data)
    #
    #         if obj:
    #             create_time = obj.get().create_time
    #             creator = obj.get().creator
    #             cls.model.delete().where(cls.model.project_id == project_id,
    #                                      cls.model.sample_type == sample_type).execute()
    #             current = datetime_format(datetime.now())
    #             for sample_id in sample_ids:
    #                 user_dict = {
    #                     "id": get_uuid(),
    #                     "project_id": project_id,
    #                     "sample_id": sample_id,
    #                     "updator": user,
    #                     "creator": creator,
    #                     "create_time": create_time,
    #                     "update_time": current,
    #                     "sample_type": sample_type,
    #                 }
    #                 project_sample_data.append(user_dict)
    #         else:
    #             create_time = datetime_format(datetime.now())
    #             for sample_id in sample_ids:
    #                 user_dict = {
    #                     "id": get_uuid(),
    #                     "project_id": project_id,
    #                     "sample_id": sample_id,
    #                     "creator": user,
    #                     "create_time": create_time,
    #                     "sample_type": sample_type
    #                 }
    #                 project_sample_data.append(user_dict)
    #         if project_sample_data:
    #             cls.model.insert_many(project_sample_data).execute()