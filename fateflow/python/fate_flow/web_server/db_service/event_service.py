from fate_flow.db.db_models import DB
from fate_flow.web_server.db.db_models import StudioEvent, StudioEventHistory
from fate_flow.web_server.db_service.common_service import CommonService


class EventService(CommonService):
    model = StudioEvent

    @classmethod
    @DB.connection_context()
    def update_event(cls,type,codes):
        with DB.atomic():
            if type =="log":
                cls.model.update({"log": None}).execute()
                for log_event_code in codes:
                    cls.model.update({"log":True}).where(cls.model.code==log_event_code).execute()
            elif type =="chain":
                cls.model.update({"chain": None}).execute()
                for chain_event_code in codes:
                    cls.model.update({"chain":True}).where(cls.model.code==chain_event_code).execute()
            else:
                raise Exception("类型error")

class StudioEventHistoryService(CommonService):
    model = StudioEventHistory

    @classmethod
    @DB.connection_context()
    def update_event(cls,type,codes):
        with DB.atomic():
            if type =="log":
                cls.model.update({"log": None}).execute()
                for log_event_code in codes:
                    cls.model.update({"log":True}).where(cls.model.code==log_event_code).execute()
            elif type =="chain":
                cls.model.update({"chain": None}).execute()
                for chain_event_code in codes:
                    cls.model.update({"chain":True}).where(cls.model.code==chain_event_code).execute()
            else:
                raise Exception("类型error")