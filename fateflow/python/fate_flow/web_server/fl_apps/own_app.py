import os, re
import shutil
from datetime import datetime
import pandas as pd
from collections import defaultdict
from flask import request, send_file
from flask_login import login_required, current_user
from fate_arch import storage
from fate_arch.common.file_utils import get_project_base_directory
from fate_arch.storage import StorageTableOrigin
from fate_flow.entity.run_status import FederatedSchedulingStatusCode
from fate_flow.settings import stat_logger
from fate_flow.utils import job_utils
from fate_arch.session import Session
from fate_flow.manager.data_manager import DataTableTracker
from fate_flow.utils.detect_utils import validate_request
from fate_flow.web_server.db.db_models import StudioSampleInfo, StudioProjectUsedSample, StudioProjectInfo
from fate_flow.web_server.db_service.sample_service import SampleService, SampleFieldsService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.fl_scheduling_apps.fl_command import FL_Scheduler
from fate_flow.web_server.utils.common_util import get_uuid, get_df_types, get_field_type, read_mysql_table, \
    datetime_format, get_format_time
from fate_flow.web_server.utils.df_apply import sample_on_off_chinese_status
from fate_flow.web_server.utils.enums import SampleDataEnum, OwnerEnum, StatusEnum, SamplePublishStatusEnum, \
    UserAuthEnum
from fate_flow.web_server.utils.hdfs_util import HDFSUtil
from fate_flow.web_server.utils.upload_utils import Diy_upload
from fate_flow.web_server.utils.reponse_util import get_json_result, validate_permission_code


@manager.route('/list', methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_GUEST.value)
def own_data_list():
    """自有数据展示列表，前端分页"""

    need_all = request.json.get("need_all", False)
    smp_type = request.json.get("sample_type")

    cols = [SampleService.model.id, SampleService.model.name,
            SampleService.model.type, SampleService.model.sample_type,
            SampleService.model.file_path, SampleService.model.sample_count,
            SampleService.model.comments, SampleService.model.publish_status, SampleService.model.status,
            SampleService.model.create_time, SampleService.model.creator, SampleService.model.update_time]
    if not need_all:
        if smp_type:
            sample_list = list(SampleService.query(owner=OwnerEnum.OWN.value, sample_type=smp_type,
                                                   status=StatusEnum.VALID.value, cols=cols, reverse=True).dicts())
        else:
            sample_list = list(SampleService.query(owner=OwnerEnum.OWN.value,
                                                   status=StatusEnum.VALID.value, cols=cols, reverse=True).dicts())
    else:
        if smp_type:
            sample_list = list(
                SampleService.query(owner=OwnerEnum.OWN.value, sample_type=smp_type, cols=cols, reverse=True).dicts())
        else:
            sample_list = list(SampleService.query(owner=OwnerEnum.OWN.value, cols=cols, reverse=True).dicts())

    sample_ids = []
    is_superuser = current_user.is_superuser
    user_name = current_user.username
    for sample in sample_list:
        o_file_name = os.path.basename(sample["file_path"]) if sample["file_path"] else ""
        sample["file_name"] = o_file_name
        sample["publish_status"] = sample_on_off_chinese_status(sample["publish_status"])
        if sample["status"] != StatusEnum.VALID.value: sample["publish_status"] = "已删除"
        sample["can_edit"] = True if is_superuser or sample["creator"] == user_name else False
        sample_ids.append(sample["id"])
        sample["update_time"] = sample["update_time"] if sample["update_time"] else ""

    sample_project_objs = SampleService.sample_join_projects(sample_ids)
    sample_project_dict = defaultdict(list)

    for sample_project_obj in sample_project_objs.objects():
        sample_project_dict[sample_project_obj.sample_id].append(sample_project_obj.name)

    for sample_i in sample_list:
        join_project = sample_project_dict.get(sample_i["id"], [])
        sample_i["join_project"] = join_project
        sample_i["join_project_count"] = str(len(join_project))

    return get_json_result(data=sample_list)


@manager.route("/add", methods=['POST'])
@login_required
@validate_request("name", "sample_type", "type")
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_GUEST.value, UserAuthEnum.DATA_GUEST_CREATE.value)
def add_sample():
    """自有数据_新建样本_数据配置"""
    request_data = request.json
    namespace = config.namespace
    name = request_data["name"]
    create_type = request_data["type"].upper()
    # 处理参数
    obj = SampleService.query(name=name, status=StatusEnum.VALID.value)
    if obj:
        return get_json_result(data=False, retmsg="样本名称已存在", retcode=100)
    conf_json = {
        "namespace": namespace,
        "name": name,
    }
    schema = None
    id_delimiter = request_data.get("id_delimiter", ",")
    in_serialized = 1
    sess = Session()
    if create_type == SampleDataEnum.LOCAL.value:
        table = sess.get_table(
            name=name, namespace="experiment"
        )
        if not table:
            return get_json_result(retcode=100, retmsg='请先上传本地文件')
        file_path = request_data["file_path"]
        df = pd.read_csv(file_path, nrows=300)
        sample_count = table.meta.count
    else:
        if create_type == SampleDataEnum.MYSQL.value:
            request_data["file_path"] = request_data["db_tablename"]
            conf_json["engine"] = SampleDataEnum.MYSQL.value
            db = request_data["db_database"]
            table_name = request_data["db_tablename"]
            db_user = request_data["db_username"]
            passwd = request_data["db_password"]
            host = request_data["db_host"]
            port = int(request_data["db_port"])
            conf_json["address"] = {
                "user": db_user,
                "passwd": passwd,
                "host": host,
                "port": port,
                "db": db,
                "name": table_name
            }
        elif create_type == SampleDataEnum.FLHIVE.value:
            conf_json["address"] = {
                "user": request_data["db_username"],
                "passwd": request_data["db_password"],
                "host": request_data["db_host"],
                "port": int(request_data["db_port"]),
                "name": request_data["db_tablename"],
                "db": request_data["db_database"],
            }
            request_data["file_path"] = request_data["db_tablename"]
            conf_json["engine"] = SampleDataEnum.FLHIVE.value
        elif create_type == SampleDataEnum.HBASE.value:
            request_data["file_path"] = request_data["db_tablename"]
            conf_json["address"] = {
                "host": request_data["db_host"],
                "port": int(request_data["db_port"]),
                "name": request_data["db_tablename"],
                "namespace": request_data.get("namespace") if request_data.get("namespace") else "default",
            }
            conf_json["engine"] = SampleDataEnum.HBASE.value
        elif create_type == SampleDataEnum.ORACLE.value:
            conf_json["engine"] = SampleDataEnum.ORACLE.value
            conf_json["address"] = {
                "user": request_data["db_username"],
                "passwd": request_data["db_password"],
                "host": request_data["db_host"],
                "port": int(request_data["db_port"]),
                "name": request_data["db_tablename"],
                "dsn": request_data["db_dsn"],
            }
            request_data["file_path"] = request_data["db_tablename"]
        elif create_type == SampleDataEnum.POSTGRESQL.value:
            request_data["file_path"] = request_data["db_tablename"]
            conf_json["engine"] = SampleDataEnum.POSTGRESQL.value
            conf_json["address"] = {
                "user": request_data["db_username"],
                "password": request_data["db_password"],
                "host": request_data["db_host"],
                "port": int(request_data["db_port"]),
                "name": request_data["db_tablename"],
                "database": request_data["db_database"],
            }
        elif create_type == SampleDataEnum.HDFS.value:
            in_serialized = 0
            conf_json["engine"] = SampleDataEnum.HDFS.value
            node_name = request_data["node_name"]
            file_path = request_data["file_path"]
            conf_json["address"] = {
                "name_node": node_name,
                "path": file_path
            }
        address = storage.StorageTableMeta.create_address(storage_engine=conf_json["engine"],
                                                          address_dict=conf_json["address"])
        storage_session = sess.storage(storage_engine=conf_json["engine"], options=None)
        flag, err_msg, table = storage_session.verify_conn(address=address, name=name, namespace=namespace,
                                                           partitions=config.partition,
                                                           hava_head=request_data.get("head"), schema=schema,
                                                           id_delimiter=id_delimiter, in_serialized=in_serialized,
                                                           origin=request_data.get("origin",
                                                                                   StorageTableOrigin.TABLE_BIND))
        if not table:
            return get_json_result(retcode=100,
                                   retmsg=err_msg)
        flag, msg, df, schema = table.read_fl_table(sql=request_data.get("sql"), part_of_data=True)
        if not flag:
            return get_json_result(data=False, retmsg=msg, retcode=100)
        table.create_meta(hava_head=request_data.get("head"), schema=schema,
                          id_delimiter=id_delimiter, in_serialized=in_serialized,
                          origin=request_data.get("origin", StorageTableOrigin.TABLE_BIND))
        sample_count = table.count()
    sess.destroy_all_sessions()
    types_values = df.dtypes.values
    types = get_df_types(types_values)
    field_data = get_field_type(df, types)
    sample_id = get_uuid()
    create_time = get_format_time()
    request_data["sample_count"] = sample_count
    request_data["publish_status"] = SamplePublishStatusEnum.UNPUBLISHED.value
    request_data["owner"] = OwnerEnum.OWN.value
    request_data["creator"] = current_user.username
    request_data["create_time"] = create_time
    request_data["party_id"] = config.local_party_id
    request_data["id"] = sample_id
    request_data["party_name"] = config.local_party_name
    for sample_dict in field_data:
        sample_dict["creator"] = current_user.username
        sample_dict["id"] = get_uuid()
        sample_dict["sample_id"] = sample_id
        sample_dict["create_time"] = create_time
    try:
        SampleService.create_sample(request_data, field_data)
        DataTableTracker.create_table_tracker(
            table_name=name,
            table_namespace=namespace,
            entity_info={"have_parent": False},
        )
    except Exception as e:
        return get_json_result(data=False,
                               retmsg="Sorry！数据保存失败！{}".format(re.sub(r"(^[0-9]+,|^.*Error\(|[\(\)'\"]+)", "", str(e))),
                               retcode=100)

    return get_json_result(data={"sample_id": sample_id, "sample_name": name})


@manager.route("/upload", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_GUEST.value, UserAuthEnum.DATA_GUEST_CREATE.value)
def upload_sample():
    """自有数据_新建样本_数据配置_本地文件上传"""
    stat_logger.info("upload start............")
    request_data = request.form
    stat_logger.info("request.form get............")
    namespace = config.namespace
    name = request_data["name"]
    if not name:
        return get_json_result(data=False, retmsg="请输入样本名称", retcode=100)
    obj = SampleService.query(name=name)
    if obj:
        return get_json_result(data=False, retmsg="样本名称已存在", retcode=100)
    job_id = job_utils.generate_job_id()
    file = request.files['file']
    filename = os.path.join(job_utils.get_job_directory(job_id), 'fate_upload_tmp', file.filename)
    temp_party_filename = os.path.join(job_utils.get_job_directory(job_id), 'temp_party', file.filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    os.makedirs(os.path.dirname(temp_party_filename), exist_ok=True)
    try:
        file.save(filename)
        if os.stat(filename).st_size <= 0:
            return get_json_result(data=False, retcode=100, retmsg='上传文件不能为空')
        df = pd.read_csv(filename)
        num = len(df) if len(df) < 300 else 300
        df.sample(num).to_csv(temp_party_filename, index=False)
    except Exception as e:
        shutil.rmtree(os.path.join(job_utils.get_job_directory(job_id), 'fate_upload_tmp'))
        shutil.rmtree(os.path.join(job_utils.get_job_directory(job_id), 'temp_party'))
        stat_logger.exception(e)
        return get_json_result(data=False, retmsg="样本格式或数据有误，请上传正确的csv或txt", retcode=100)
    job_config = {'table_name': name, 'namespace': namespace,
                  'head': True, 'partitions': config.partition, 'drop': 1,
                  'file': filename,
                  'name': name, 'destroy': True}

    try:
        fl_upload = Diy_upload()
        fl_upload.diy_run(job_id, job_config)
    except Exception as e:
        stat_logger.exception(e)
        return get_json_result(data="上传失败", retcode=100)
    data = {
        "file_path": temp_party_filename,
    }
    return get_json_result(data=data)


@manager.route("/delete_upload", methods=['POST'])
@login_required
@validate_request("name")
def delete_upload_file():
    """自有数据_新建样本_数据配置_本地文件上传删除"""
    # 删除fate表里面的记录
    # 删除本地上传文件？
    namespace = config.namespace
    name = request.json["name"]
    data_table_meta = storage.StorageTableMeta(name=name, namespace=namespace)
    if data_table_meta:
        data_table_meta.destroy_metas()
    return get_json_result(data=True)


@manager.route("/delete/<string:sample_id>", methods=['POST'])
@login_required
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_GUEST.value, UserAuthEnum.DATA_GUEST_DELETE.value)
def delete_sample(sample_id):
    """自有数据_删除样本"""
    obj = StudioProjectUsedSample.query(sample_id=sample_id,
                                        ).first()
    if obj:
        project_obj = StudioProjectInfo.query(id=obj.project_id,
                                              ).first()
        return get_json_result(retcode=100, retmsg="Sorry！项目名是%s正在使用，不可删除！" % project_obj.name)

    del_num = StudioSampleInfo.delete().where(StudioSampleInfo.id == sample_id).execute()
    if not del_num:
        return get_json_result(data=False, retmsg="{}-样本不存在".format(sample_id))
    endpoint = "delete_sample"
    status_code, response = FL_Scheduler.sample_command(sample_id, endpoint)
    if status_code != FederatedSchedulingStatusCode.SUCCESS:
        return get_json_result(data=True, retmsg=response)
    else:
        return get_json_result(data=True, retmsg="success")


@manager.route("/on_off_line", methods=['POST'])
@login_required
@validate_request("sample_id", "operate")
@validate_permission_code(UserAuthEnum.DATA.value, UserAuthEnum.DATA_GUEST.value,
                          UserAuthEnum.DATA_GUEST_ONLINE_OFFLINE.value)
def on_off_line():
    """样本 上下线"""
    request_data = request.json
    sample_id = request_data["sample_id"]
    sample_obj = StudioSampleInfo.query(id=sample_id).first()
    if not sample_obj:
        return get_json_result(data=False, retmsg="{}-样本不存在".format(request_data["sample_id"]))
    publish_status = request_data["operate"]
    if publish_status == "0":
        publish_status = SamplePublishStatusEnum.OFF_LINE.value
    # todo 删除样本，对项目有什么影响
    # todo 要通知guest方，样本已经下架,federated_api失败，是否要重新发送？
    endpoint = "modify_publish_status/%s" % publish_status
    sample_field_cols = [SampleFieldsService.model.sample_id, SampleFieldsService.model.field_name,
                         SampleFieldsService.model.field_type, SampleFieldsService.model.field_sort,
                         SampleFieldsService.model.distribution_type, SampleFieldsService.model.data_type,
                         SampleFieldsService.model.field_description, SampleFieldsService.model.positive_value, ]
    sample_field_list = list(SampleFieldsService.query(sample_id=sample_id, cols=sample_field_cols).dicts())
    command_body = {"sample_id": sample_id,
                    "sample_party_id": config.local_party_id,
                    "publish_status": publish_status,
                    "sample_type": sample_obj.sample_type,
                    "sample_count": sample_obj.sample_count,
                    "sample_name": sample_obj.name,
                    "comments": sample_obj.comments,
                    "sample_field_list": sample_field_list
                    }
    status_code, response = FL_Scheduler.sample_command(sample_id, endpoint, command_body)
    if status_code != FederatedSchedulingStatusCode.SUCCESS:
        return get_json_result(data=True, retmsg=response)
    else:
        return get_json_result(data=True, retmsg="success")


@manager.route("/get_fields", methods=['POST'])
@login_required
@validate_request("type")
def get_sample_fields():
    """自有数据_新建样本_样本标注展示"""
    # float、int 分布 连续型
    # str 分布 离散型
    # id（ID） y(y) 其他是标签业务属性
    # 获取到数据（本地数据、mysql、HDFS）
    request_data = request.json
    sample_type = request_data["type"]
    try:
        msg = "success"
        if sample_type.upper() == SampleDataEnum.MYSQL.value:
            db_tablename = request_data["db_tablename"]
            db_username = request_data["db_username"]
            db_password = request_data["db_password"]
            host = request_data["db_host"]
            port = int(request_data["db_port"])
            db_name = request_data["db_database"]
            engine_url = "mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8".format(
                user=db_username,
                password=db_password,
                host=host, port=port,
                db_name=db_name)
            df = read_mysql_table(engine_url, db_tablename)
            if not df.empty:
                types = get_df_types(df.dtypes.values)
                field_data = get_field_type(df, types)
            else:
                field_data = []
        elif sample_type.upper() == SampleDataEnum.HDFS.value:
            node_name = request_data["node_name"]
            file_path = request_data["file_path"]
            flag, df = HDFSUtil(node_name, file_path).read_hdfs()
            if not flag:
                return get_json_result(data=False, retmsg=df, retcode=100)
            types = get_df_types(df.dtypes.values)
            field_data = get_field_type(df, types)
        elif sample_type == SampleDataEnum.LOCAL.value:
            file_path = request_data["file_path"]
            # 本地(csv、txt)
            df = pd.read_csv(file_path, nrows=300)
            types = get_df_types(df.dtypes.values)
            field_data = get_field_type(df, types)
        else:
            field_data = []
    except Exception as e:
        msg = str(e)
        field_data = []
    data = {
        "all_field_type": ["int", "float", "str", "bool"],
        "all_data_type": ["Y", "ID", "特征"],
        "all_distribution_type": ["连续型", "离散型"],
        "data": field_data
    }
    return get_json_result(data=data, retmsg=msg)


@manager.route("/add_fields/<string:sample_id>", methods=['POST'])
@login_required
def add_sample_fields(sample_id):
    """自有数据_新建样本_样本标注保存"""
    # todo 是否存在重复保存的列？
    sample_field_list = request.json["sample_field_list"]
    if not sample_field_list:
        return get_json_result(data=False, retcode=100, retmsg="无保存内容")
    if not SampleService.query(id=sample_id):
        return get_json_result(data=False, retcode=100, retmsg="{}-样本不存在".format(sample_id))
    create_time = datetime_format(datetime.now())
    for sample_dict in sample_field_list:
        sample_dict["creator"] = current_user.username
        sample_dict["id"] = get_uuid()
        sample_dict["sample_id"] = sample_id
        sample_dict["create_time"] = create_time
    SampleFieldsService.insert_many(sample_field_list)
    return get_json_result(data=True)


@manager.route("/edit_fields/<string:sample_id>", methods=['POST'])
@login_required
def edit_sample_fields(sample_id):
    """自有数据_样本标注展示列表编辑（前端可以把有改动的数据发送过来）"""
    sample_field_list = request.json["sample_field_list"]
    if not sample_field_list:
        return get_json_result(data=False, retcode=100, retmsg="无编辑内容")
    sample_obj = SampleService.query(id=sample_id).first()
    if not sample_obj:
        return get_json_result(data=False, retcode=100, retmsg="{}-样本不存在".format(sample_id))
    if not (current_user.username == sample_obj.creator or current_user.is_superuser):
        return get_json_result(data=False, retcode=100, retmsg="不是管理员，或创建者，不能对样本标注")
    for field in sample_field_list:
        field["sample_id"] = sample_id
        field["updator"] = current_user.username
    SampleFieldsService.update_many_by_id(sample_field_list)
    if sample_obj.status == SamplePublishStatusEnum.PUBLISHED.value:
        endpoint = "edit_fields"
        for i in sample_field_list:
            del i["updator"]
        command_body = {"sample_field_list": sample_field_list}
        if sample_obj.publish_status == SamplePublishStatusEnum.PUBLISHED.value:
            status_code, response = FL_Scheduler.sample_command(sample_id, endpoint, command_body, specific_dest=True)
            if status_code != FederatedSchedulingStatusCode.SUCCESS:
                return get_json_result(retcode=100, data=True, retmsg=response)
    return get_json_result(data=True, retmsg="success")


@manager.route("/get_publish_sample", methods=['POST'])
@login_required
def get_publish_sample():
    """自有数据_获取自有数据发布的样本"""
    sample_objs = SampleService.query_publish_sample()
    data = list(sample_objs.dicts())
    return get_json_result(data=data)


@manager.route("/get_csv", methods=['GET'])
@login_required
def get_csv():
    """数据上传 样本案例"""
    file_path = os.path.join(get_project_base_directory(),
                             "fateflow/python/fate_flow/web_server/data/breast_hetero_guest.csv")
    return send_file(file_path, mimetype="text/csv", as_attachment=True)
