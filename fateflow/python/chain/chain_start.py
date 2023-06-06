import os
from chain.common.enum import StoreType
from chain.common.util import store_upload, chain_logger
from fate_arch.common import file_utils
import datetime
from fate_flow.web_server.db.db_models import StudioModelInfoExtend, StudioSampleInfo, StudioAuthUser, \
    StudioProjectInfo, StudioProjectCanvas, StudioPartyInfo
from apscheduler.schedulers.blocking import BlockingScheduler

from fate_flow.web_server.utils.common_util import datetime_format


def detect_store_upload():
    chain_logger.info("start_time %s"%datetime_format(datetime.datetime.now()))
    store_upload(data_type=StoreType.PARTY.value, model=StudioPartyInfo)
    store_upload(data_type=StoreType.TASK_PROJECT.value, model=StudioProjectInfo)
    store_upload(data_type=StoreType.TASK_CANVAS.value, model=StudioProjectCanvas)
    store_upload(data_type=StoreType.DATA_USER.value, model=StudioAuthUser)
    store_upload(data_type=StoreType.DATA_MODEL.value, model=StudioModelInfoExtend)
    store_upload(data_type=StoreType.DATA_SAMPLE.value, model=StudioSampleInfo)
    chain_logger.info("end_time %s" % datetime_format(datetime.datetime.now()))

if __name__ == '__main__':
    config_path = os.path.join("conf", "chain_config.yaml")
    conf = file_utils.load_yaml_conf(config_path)
    # detect_store_upload()
    if conf["service"]:
        scheduler = BlockingScheduler(timezone="Asia/Shanghai")
        scheduler.add_job(detect_store_upload, trigger='interval', seconds=conf["seconds"],
                          next_run_time=datetime.datetime.now(), misfire_grace_time=30, coalesce=True,
                          replace_existing=True)
        scheduler.start()
