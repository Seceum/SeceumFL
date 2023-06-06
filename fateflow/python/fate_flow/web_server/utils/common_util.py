import os
import re
import shutil
import uuid
import pandas as pd
import numpy as  np
import zipfile
from datetime import datetime
from sqlalchemy import create_engine
from fate_flow.manager.data_manager import get_component_output_data_schema
from fate_flow.settings import ENGINES
from fate_flow.utils.api_utils import federated_api
from fate_flow.web_server.fl_config import url_code_dict
from fate_flow.web_server.utils.enums import APPROVEChineseEnum, PublishStatusChineseEnum, RoleTypeEnum
from fate_arch.common.base_utils import fate_uuid
from fate_arch.session import Session
from fate_flow.component_env_utils import feature_utils
from fate_flow.utils.base_utils import get_fate_flow_directory


def get_uuid():
    return uuid.uuid1().hex

def get_role_type(is_join):
    return RoleTypeEnum.HOST.value if is_join else RoleTypeEnum.GUEST.value

def datetime_format(date_time: datetime) -> datetime:
    return datetime(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute, date_time.second)


def get_format_time() -> datetime:
    return datetime_format(datetime.now())

def url_code(url):
    for pattern in url_code_dict.keys():
        if re.search(pattern,url):
            return url_code_dict[pattern],pattern
    return None,None
def str2date(date_time: str):
    return datetime.strptime(date_time, '%Y-%m-%d')


def elapsed2time(elapsed):
    seconds = elapsed / 1000
    minuter, second = divmod(seconds, 60)
    hour, minuter = divmod(minuter, 60)
    return '%02d:%02d:%02d' % (hour, minuter, second)


def get_df_types(d_types):
    type_list = []
    for a_type in d_types:
        tmp_type = str(a_type)
        if tmp_type.find("64") >= 0:
            type_list.append(tmp_type[0:tmp_type.rfind("64")])
        elif tmp_type.find("32") >= 0:
            type_list.append(tmp_type[0:tmp_type.rfind("32")])
        elif tmp_type == "object":
            type_list.append('str')
        else:
            type_list.append(tmp_type)

    return type_list


def get_field_type(df, df_type):
    field_list = []
    index = 0
    data = df.astype(str).to_dict("list")
    for col in df.columns:
        col_type = df_type[index]
        temp_dict = {"field_name": col, "field_type": col_type, "field_examples": (",".join(data[col][:10])[:256]),
                     "positive_value": "", "field_description": ""}
        if col_type != "str":
            temp_dict["distribution_type"] = "连续型"
        else:
            temp_dict["distribution_type"] = "离散型"
        if col.lower() == "id":
            temp_dict["data_type"] = "ID"
        elif col.lower() == "y":
            temp_dict["data_type"] = "Y"
            # temp_dict["positive_value"] = "1"
        else:
            temp_dict["data_type"] = "特征"
        field_list.append(temp_dict)
        index += 1
    return field_list

# 判断数据是否是int类型
def num_is_int(x):
    try:
        return int(float(x)) == float(x)
    except Exception as e:
        pass
    return False

# 判断数据是float类型
def num_is_float(x):
    try:
        if str(x) in ['inf',"infinity",'INF','INFINITY','True','NAN','nan','False','-inf','-INF','-INFINITY','-infinity','NaN','Nan']:
            return False
        else:
            flag = num_is_int(x)
            if not flag:
                flag = isinstance(eval(x),float)
            return flag
    except Exception as ex:
            return False

# 判断数据是否是bool类型
def num_is_bool(x):
    try:
        if str(x) in ['TRUE','FALSE','false','true','True','False',False,True]:
            return True

        if isinstance(eval(str(x)),bool) :
            return True
        else:
            return False
    except Exception as ex:
        return False

def get_field_type(df, df_type):
    import re
    field_list = []
    data = df.astype(str).to_dict("list")
    import numpy as np
    for index, col in enumerate(df.columns):
        col_type = df_type[index]
        """
        判断有问题的情形
        1 原始数据中有int,NAN为判断为float 类型
        2 hbase,hdfs中只有str,需要将str转换为float
        3 原始数据中有
        """


        if col_type == "str":
            u = df[col].dropna().nunique()
            temp = df[col].dropna().unique()
            # update by tjx 2023410
            if u == sum([num_is_int(x) for x in temp]):
                col_type = "int"
        if col_type == "str":
            u = df[col].dropna().nunique()
            temp = df[col].dropna().unique()
            if u == sum([num_is_bool(x) for x in temp]):
                col_type = "bool"
        if col_type == 'int':
            u = df[col].dropna().nunique()
            temp = df[col].dropna().unique()
            if u == sum([num_is_bool(x) for x in temp]):
                col_type = "bool"
        if col_type == "str":
            u = df[col].dropna().nunique()
            temp = df[col].dropna().unique()
            if u == sum([num_is_float(x) for x in temp]):
                col_type = "float"
        if col_type == 'float':
            u = df[col].dropna().nunique()
            temp = df[col].dropna().unique()
            if u == sum([num_is_int(x) for x in temp]):
                col_type = "int"

        temp_dict = {"field_name": col, "field_type": col_type, "field_examples": (",".join(data[col][:10])[:256]),
                     "positive_value": "", "field_description": ""}
        if re.search(r"id$", col, flags=re.IGNORECASE):temp_dict["data_type"] = "ID"
        elif col.lower() in ["y", "target"]:temp_dict["data_type"] = "Y"
        else:
            temp_dict["data_type"] = "特征"
            u = df[col].dropna().nunique()
            if u*1./len(df) < 0.1: temp_dict["distribution_type"] = "离散型"
            elif col_type != "str":temp_dict["distribution_type"] = "连续型"
            else: temp_dict["distribution_type"] = "离散型"

        field_list.append(temp_dict)

    return field_list


def read_mysql_table(engine_url, table_name):
    sql = f"select * from {table_name} limit 5"
    engine = create_engine(engine_url)
    # if engine.has_table(table_name):
    #     df = pd.read_sql(sql, engine)
    #     return df
    # else:
    #     return None
    df = pd.read_sql(sql, engine)
    return df


def add_role_info_zip(zip_file_path, role_type):
    date_time = datetime.now()
    ziphandler = zipfile.ZipFile(zip_file_path, "a", compression=zipfile.ZIP_DEFLATED)
    zipinfo = zipfile.ZipInfo('role_type.txt', date_time=(
        date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute, date_time.second))
    zipinfo.compress_type = ziphandler.compression
    ziphandler.writestr(zipinfo, role_type)
    ziphandler.close()


def get_zip_role_type(file_path, config_body):
    file_path_dir = file_path.replace(".zip", "")
    os.makedirs(file_path_dir, exist_ok=True)
    shutil.unpack_archive(file_path, file_path_dir)
    with open(os.path.join(file_path_dir, "role_type.txt")) as role_f:
        config_body["role"] = role_f.read()
    shutil.rmtree(file_path_dir)


def model_can_remove(df):
    # 未发布 + 审批中、 发布中 + 已同意、 已发布 + 已同意  已经使用的模型模型删除
    # 审批中、 发布中、 已发布，不能删除
    can_remove_ser = np.where(((df.status == PublishStatusChineseEnum.UNPUBLISHED.value) & (
        df.approve_status == APPROVEChineseEnum.APPROVE_running.value)) | (
                                  (df.status == PublishStatusChineseEnum.RUNNING.value) & (
                                  df.approve_status == APPROVEChineseEnum.APPROVE_TRUE.value)) | (
                                  (df.status == PublishStatusChineseEnum.PUBLISHED.value) & (
                                  df.approve_status == APPROVEChineseEnum.APPROVE_TRUE.value)) | (
                              df.is_used), False, True)
    # can_remove_ser = np.where((df.approve_status == APPROVEChineseEnum.APPROVE_running.value\
    #                           |df.status == PublishStatusChineseEnum.RUNNING.value\
    #                           |df.status == PublishStatusChineseEnum.PUBLISHED.value\
    #                           |df.is_used), False, True)
    return can_remove_ser


def valid_param(request_data, input_arguments):
    no_arguments = list(set(input_arguments).difference(set(request_data.keys())))
    if no_arguments:
        error_string = "required argument are missing: {}; ".format(",".join(no_arguments))
        return False, error_string
    else:
        return True, ""

def pull_approval_result(model_id,model_version,hosts):
    json_body = {"model_id": model_id, "model_version": model_version,"role_type":"host"}
    host_approval_result = {}
    retcode =0
    retmsg= ""
    for host_id in hosts:
        response = federated_api(job_id="",
                            method='POST',
                            endpoint="/model_manage_schedule/host_approval_result",
                            src_role="",
                            src_party_id="",
                            dest_party_id=host_id,
                            json_body=json_body,
                            federated_mode=ENGINES["federated_mode"])
        if response["retcode"]:
            retcode=response["retcode"]
            retmsg=response["retmsg"]
        host_approval_result[host_id] = response["data"]
    return retcode ,retmsg,host_approval_result

def model_id_get_hosts(model_id):
    return re.search("host-(.*?)#", model_id).group(1).split("_")
def model_id_get_arbiters(model_id):
    try:
        return re.search("arbiter-(.*?)#", model_id).group(1).split("_")
    except:
        return []
def model_id_get_guests(model_id):
    return re.search("guest-(.*?)#", model_id).group(1).split("_")

def get_fusion_data_file(output_tables_meta, tar_file_name, limit=-1, need_head=True):
    output_tmp_dir = os.path.join(get_fate_flow_directory(), 'tmp/{}/{}'.format(datetime.now().strftime("%Y%m%d"), fate_uuid()))
    os.makedirs(output_tmp_dir, exist_ok=True)
    output_data_file_path = "{}/{}.csv".format(output_tmp_dir, tar_file_name)
    for output_name, output_table_meta in output_tables_meta.items():
        output_data_count = 0
        with open(output_data_file_path, 'w') as fw:
            with Session() as sess:
                output_table = sess.get_table(name=output_table_meta.get_name(),
                                              namespace=output_table_meta.get_namespace())
                if output_table:
                    for k, v in output_table.collect():
                        data_line, is_str, extend_header = feature_utils.get_component_output_data_line(src_key=k,
                                                                                                        src_value=v,
                                                                                                        schema=output_table_meta.get_schema())
                        if output_data_count == 0:
                            header = get_component_output_data_schema(output_table_meta=output_table_meta,
                                                                      is_str=is_str,
                                                                      extend_header=extend_header)
                            if need_head and header and output_table_meta.get_have_head():
                                fw.write('{}\n'.format(','.join(header)))
                        fw.write('{}\n'.format(','.join(map(lambda x: str(x), data_line))))
                        output_data_count += 1
                        if output_data_count == limit:
                            break
    return output_data_file_path





