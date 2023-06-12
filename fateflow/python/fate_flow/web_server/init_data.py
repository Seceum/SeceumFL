import os
import time
import uuid
import datetime
import pandas as pd
import numpy as np


from fate_arch.common.file_utils import load_json_conf_real_time
from fate_flow.settings import stat_logger
from fate_flow.utils.base_utils import get_fate_flow_directory
from fate_flow.web_server.db.db_models import init_database_tables as init_web_db, StudioPartyInfo
from fate_flow.web_server.db.ras_manage import RsaKeyManager
from fate_flow.web_server.db_service.algorithm_service import AlgorithmInfoService
from fate_flow.web_server.db_service.auth_service import UserService, PermissionService, GroupService
from fate_flow.web_server.db_service.event_service import EventService
from fate_flow.web_server.fl_config import eggroll_route_table_path, PARTY_ID
from fate_flow.web_server.utils.common_util import datetime_format


def init_auth_group():
    group_info = {
        "id": uuid.uuid1().hex,
        "name": "未分组",
        "creator": "system",
    }
    GroupService.save(**group_info)


def init_superuser():
    user_info = {
        "id": uuid.uuid1().hex,
        "alternative_id": uuid.uuid1().hex,
        "password": "admin",
        "nickname": "管理员",
        "username": "admin",
        "is_superuser": True,
        "creator": "system",
        "status": "1",
    }
    UserService.save(**user_info)


def init_sys_permission(data_dir):
    file_path = os.path.join(data_dir, "studio_auth_permission.csv")
    df = pd.read_csv(file_path, dtype={"p_id": str, "code": str, "is_superuser_auth": int})
    df["is_superuser_auth"] = np.where(df.is_superuser_auth == 1, True, False)
    df["create_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["creator"] = "system"
    df["id"] = [uuid.uuid1().hex for i in range(df.shape[0])]
    df.fillna('', inplace=True)
    PermissionService.insert_many(df.to_dict(orient='records'))

def init_sys_event(data_dir):
    file_path = os.path.join(data_dir, "studio_event.csv")
    df = pd.read_csv(file_path,dtype={"p_id": str, "code": str})
    df["create_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["creator"] = "system"
    df["id"] = [uuid.uuid1().hex for i in range(df.shape[0])]
    df.fillna('', inplace=True)
    EventService.insert_many(df.to_dict(orient='records'))

def init_algorithm_info(data_dir):
    file_path = os.path.join(data_dir, "studio_algorithm.csv")
    df = pd.read_csv(file_path)
    df["create_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["creator"] = "system"
    df["id"] = [uuid.uuid1().hex for i in range(df.shape[0])]
    df.fillna('', inplace=True)
    AlgorithmInfoService.insert_many(df.to_dict(orient='records'))

def init_node_info():
    try:
        config = load_json_conf_real_time(conf_path=eggroll_route_table_path)
        node_objs = StudioPartyInfo.select()
        # 删除数据库中多余的节点(eggroll中不存在的节点)
        for node in node_objs:
            if node.id not in config["route_table"]:
                StudioPartyInfo.delete().where(StudioPartyInfo.id == node.id).execute()
        # 根据eggroll路由表,
        # 不存在新建，
        # 存在则更新
        for party_id, item in config["route_table"].items():
            predict_party_ip = item["default"][0]["ip"]
            if party_id == "default" or party_id == PARTY_ID:
                continue
            predict_port = item["default"][0]["port"]
            party_name = item["default"][0].get("name", party_id)
            if not StudioPartyInfo.query(id=party_id).first():
                command_body = {
                    "id": party_id,
                    "creator": "system",
                    "party_name": party_name,
                    "create_time": datetime_format(datetime.datetime.now()),
                    "predict_party_ip": predict_party_ip,
                    "predict_port": predict_port,
                    'ping_status': '正常',
                }
                StudioPartyInfo.insert(command_body).execute()
            else:
                command_body = {
                    "predict_party_ip": predict_party_ip,
                    "predict_port": predict_port,
                }
                StudioPartyInfo.update(**command_body).where(StudioPartyInfo.id == party_id).execute()
    except Exception as e:
        stat_logger.error("解析eggroll失败%s" % str(e))

def init_web_data():
    start_time = time.time()
    project_dir = get_fate_flow_directory()
    data_dir = os.path.join(project_dir, "python", "fate_flow", "web_server", "data")
    if not PermissionService.get_all().count():
        init_sys_permission(data_dir)
    if not UserService.get_all().count():
        init_superuser()
    # if not GroupService.get_all().count():
    #     init_auth_group()
    if not AlgorithmInfoService.get_all().count():
        init_algorithm_info(data_dir)
    if not AlgorithmInfoService.get_all().count():
        init_algorithm_info(data_dir)
    if not EventService.get_all().count():
        init_sys_event(data_dir)
    RsaKeyManager.init()
    init_node_info()
    print("init web data success:{}".format(time.time() - start_time))


if __name__ == '__main__':
    init_web_db()
    init_web_data()
