from datetime import datetime

from fate_flow.web_server.db.db_models import StudioPartyInfo
from fate_flow.web_server.db_service.common_service import CommonService
from fate_flow.db.db_models import DB
from fate_flow.web_server.utils.common_util import datetime_format


class PartyInfoService(CommonService):
    model = StudioPartyInfo

    @classmethod
    @DB.connection_context()
    def update_status(cls, pid, status, user):
        update_time = datetime_format(datetime.now())
        with DB.atomic():
            update_dict = {cls.model.status: status, cls.model.updator: user,
                           cls.model.update_time: datetime_format(update_time)}
            update_obj = cls.model.update(update_dict).where(cls.model.id == pid)
            update_obj.execute()

    @classmethod
    @DB.connection_context()
    def get_partys(cls):
        partys =  cls.model.select(StudioPartyInfo.id, StudioPartyInfo.train_party_ip)
        return partys



