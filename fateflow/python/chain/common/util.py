import requests
import os

from werkzeug.security import generate_password_hash

from fate_arch.common import file_utils
from fate_arch.common.log import getLogger
from fate_flow.web_server.db.db_models import StudioPartyInfo, WebDataBaseModel, StudioChainInfo, StudioProjectInfo, \
    StudioProjectCanvas, StudioAuthUser, StudioModelInfoExtend, StudioSampleInfo
from fate_flow.web_server.db_service.chain_service import ChainService
from chain.common.enum import StoreType
from datetime import datetime
from fate_flow.web_server.utils.common_util import get_uuid, datetime_format
config_path = os.path.join("conf", "chain_config.yaml")
conf = file_utils.load_yaml_conf(config_path)
headers = {
    'currentChains': str({"key":conf["key"],"name":conf["name"],"id":conf["id"]}),
}


def store_send(data,try_times=2):
    exception = None
    for t in range(try_times):
        try:
            response = requests.post(conf["store_url"], json=data, headers=headers,timeout=3)
            return response.json()
        except Exception as e:
            exception = e
    else:
        raise exception


chain_logger = getLogger("chain")

def insert_chain_data_update_status(insert_store_list,chain_obj):
    if insert_store_list:
        insert_store_list[-1]["is_latest"] = True
        ChainService.insert_many(insert_store_list, batch_size=100)
        if chain_obj:
            chain_obj.is_latest = False
            chain_obj.save()

def store_upload(data_type,model):
    chain_logger.info("%s start"%data_type)
    chain_obj = ChainService.query(is_latest=True, type=data_type).first()
    if chain_obj:
        last_store_time = chain_obj.last_store_time
        if model == StudioProjectCanvas:
            objs = model.select().where(
                            model.create_time > last_store_time).order_by(model.create_time,
                                                                                            model.update_time)
        else:
            objs = model.select().where(
                    (model.update_time > last_store_time) | (
                            model.create_time > last_store_time)).order_by(model.create_time,
                                                                                            model.update_time)
    else:
        if conf.get("last_store_time"):
            store_starttime=conf.get("last_store_time")
        else:
            store_starttime = "2022-11-01"
        objs = model.select().where(        (model.update_time > store_starttime) | (
                        model.create_time > store_starttime)).order_by(model.create_time,model.update_time)
    insert_store_list = []
    if objs:
        for obj in objs:
            if not (obj.create_time or obj.update_time):
                continue
            request_data={}
            for k ,v in  obj.to_dict().items():
                if v:
                    request_data[k]=v
            if request_data.get("db_password"):
                del request_data["db_password"]
            request_data["type"]=data_type
            request_data = {"data": str(request_data)}
            try:
                response = store_send(request_data)
                chain_logger.info(str(response))
            except Exception as e:
                chain_logger.error(str(e)+str(request_data))
                break
            if response["state"] == 200:
                insert_store_list.append({
                    "id": get_uuid(),
                    "type": data_type,
                    "is_latest": False,
                    "last_store_time": obj.update_time if obj.update_time else obj.create_time,
                    "store_data": request_data,
                    "store_return": response["data"],
                    "create_time": datetime_format(datetime.now()),
                })
        insert_chain_data_update_status(insert_store_list,chain_obj)
    chain_logger.info("%s end length %s"%(data_type,len(insert_store_list)))



if __name__ == '__main__':
    # store_upload(data_type=StoreType.PARTY.value,model=StudioPartyInfo)
    # store_upload(data_type=StoreType.TASK_PROJECT.value,model=StudioProjectInfo)
    # store_upload(data_type=StoreType.TASK_CANVAS.value,model=StudioProjectCanvas)
    # store_upload(data_type=StoreType.DATA_USER.value,model=StudioAuthUser)
    # store_upload(data_type=StoreType.DATA_MODEL.value,model=StudioModelInfoExtend)
    store_upload(data_type=StoreType.DATA_SAMPLE.value,model=StudioSampleInfo)
#
