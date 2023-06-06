import os
import sys
import threading
import traceback
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

from fate_arch.common import FederatedMode, base_utils
from fate_arch.common.base_utils import json_dumps, current_timestamp
from fate_flow.db.db_models import Job, Task
from fate_flow.db.runtime_config import RuntimeConfig
from fate_flow.entity import RetCode, RunParameters
from fate_flow.entity.run_status import FederatedSchedulingStatusCode, TaskStatus, JobStatus
from fate_flow.entity.types import WorkerName, ResourceOperation
from fate_flow.manager.worker_manager import WorkerManager
from fate_flow.operation.job_saver import JobSaver
from fate_flow.operation.job_tracker import Tracker
from fate_flow.db.db_models import (DB, ModelOperationLog as OperLog)
from fate_flow.scheduler.dag_scheduler import DAGScheduler
from fate_flow.scheduler.federated_scheduler import FederatedScheduler
from fate_flow.settings import stat_logger, ENGINES, HOST, HTTP_PORT
from fate_flow.utils import job_utils, process_utils
from fate_flow.utils.api_utils import federated_api
from fate_flow.utils.authentication_utils import PrivilegeAuth
from fate_flow.utils.log_utils import start_log, schedule_logger, warning_log, failed_log
from fate_flow.utils.process_utils import get_std_path
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.db_service.project_service import ProjectSampleService, TaskService
from fate_flow.web_server.db_service.sample_service import VSampleInfoService, SampleFieldsService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.common_util import get_uuid, datetime_format
from fate_flow.web_server.utils.enums import SampleTypeEnum, MixTypeEnum, StatusEnum, FusionFieldControl, \
    FieldTypeChinese
from fate_flow.component_env_utils.env_utils import import_component_output_depend
from fate_arch.session import Session
from fate_flow.component_env_utils import feature_utils
from fate_flow.manager.data_manager import get_component_output_data_schema


def gen_data_access_job_config(config_data, access_module):
    job_runtime_conf = {
        "initiator": {},
        "job_parameters": {"common": {}},
        "role": {},
        "component_parameters": {"role": {"local": {"0": {}}}}
    }
    initiator_role = "local"
    initiator_party_id = config_data.get('party_id', 0)
    job_runtime_conf["initiator"]["role"] = initiator_role
    job_runtime_conf["initiator"]["party_id"] = initiator_party_id
    job_parameters_fields = {"task_cores", "eggroll_run", "spark_run", "computing_engine", "storage_engine",
                             "federation_engine"}
    for _ in job_parameters_fields:
        if _ in config_data:
            job_runtime_conf["job_parameters"]["common"][_] = config_data[_]
    job_runtime_conf["job_parameters"]["common"]["federated_mode"] = FederatedMode.SINGLE
    job_runtime_conf["role"][initiator_role] = [initiator_party_id]
    job_dsl = {
        "components": {}
    }

    if access_module == 'upload':
        parameters = {
            "head",
            "partition",
            "file",
            "namespace",
            "name",
            "delimiter",
            "storage_engine",
            "storage_address",
            "destroy",
            "extend_sid",
            "auto_increasing_sid",
            "block_size"
        }
        update_config(job_runtime_conf, job_dsl, initiator_role, parameters, access_module, config_data)

    if access_module == 'download':
        parameters = {
            "delimiter",
            "output_path",
            "namespace",
            "name"
        }
        update_config(job_runtime_conf, job_dsl, initiator_role, parameters, access_module, config_data)

    if access_module == 'writer':
        parameters = {
            "namespace",
            "name",
            "storage_engine",
            "address",
            "output_namespace",
            "output_name"
        }
        update_config(job_runtime_conf, job_dsl, initiator_role, parameters, access_module, config_data)
    return job_dsl, job_runtime_conf


def update_config(job_runtime_conf, job_dsl, initiator_role, parameters, access_module, config_data):
    job_runtime_conf["component_parameters"]['role'][initiator_role]["0"][f"{access_module}_0"] = {}
    for p in parameters:
        if p in config_data:
            job_runtime_conf["component_parameters"]['role'][initiator_role]["0"][f"{access_module}_0"][p] = \
                config_data[p]
    job_runtime_conf['dsl_version'] = 2
    job_dsl["components"][f"{access_module}_0"] = {
        "module": access_module.capitalize()
    }


def get_component_output_tables_meta(task_data):
    check_request_parameters(task_data)
    tracker = Tracker(job_id=task_data['job_id'], component_name=task_data['component_name'],
                      role=task_data['role'], party_id=task_data['party_id'])
    output_data_table_infos = tracker.get_output_data_info()
    output_tables_meta = tracker.get_output_data_table(output_data_infos=output_data_table_infos)
    return output_tables_meta


@DB.connection_context()
def check_request_parameters(request_data):
    if 'role' not in request_data and 'party_id' not in request_data:
        jobs = Job.select(Job.f_runtime_conf_on_party).where(Job.f_job_id == request_data.get('job_id', ''),
                                                             Job.f_is_initiator == True)
        if jobs:
            job = jobs[0]
            job_runtime_conf = job.f_runtime_conf_on_party
            job_initiator = job_runtime_conf.get('initiator', {})
            role = job_initiator.get('role', '')
            party_id = job_initiator.get('party_id', 0)
            request_data['role'] = role
            request_data['party_id'] = party_id


@DB.connection_context()
def model_operation_record(data: dict, oper_type, oper_status, remote_addr):
    try:
        if oper_type == 'migrate':
            OperLog.create(f_operation_type=oper_type,
                           f_operation_status=oper_status,
                           f_initiator_role=data.get("migrate_initiator", {}).get("role"),
                           f_initiator_party_id=data.get("migrate_initiator", {}).get("party_id"),
                           f_request_ip=remote_addr,
                           f_model_id=data.get("model_id"),
                           f_model_version=data.get("model_version"))
        elif oper_type == 'load':
            OperLog.create(f_operation_type=oper_type,
                           f_operation_status=oper_status,
                           f_initiator_role=data.get("initiator").get("role"),
                           f_initiator_party_id=data.get("initiator").get("party_id"),
                           f_request_ip=remote_addr,
                           f_model_id=data.get('job_parameters').get("model_id"),
                           f_model_version=data.get('job_parameters').get("model_version"))
        elif oper_type == 'bind':
            OperLog.create(f_operation_type=oper_type,
                           f_operation_status=oper_status,
                           f_initiator_role=data.get("initiator").get("role"),
                           f_initiator_party_id=data.get("party_id") if data.get("party_id") else data.get(
                               "initiator").get("party_id"),
                           f_request_ip=remote_addr,
                           f_model_id=data.get("model_id") if data.get("model_id") else data.get('job_parameters').get(
                               "model_id"),
                           f_model_version=data.get("model_version") if data.get("model_version") else data.get(
                               'job_parameters').get("model_version"))
        else:
            OperLog.create(f_operation_type=oper_type,
                           f_operation_status=oper_status,
                           f_initiator_role=data.get("role") if data.get("role") else data.get("initiator").get("role"),
                           f_initiator_party_id=data.get("party_id") if data.get("party_id") else data.get(
                               "initiator").get("party_id"),
                           f_request_ip=remote_addr,
                           f_model_id=data.get("model_id") if data.get("model_id") else data.get('job_parameters').get(
                               "model_id"),
                           f_model_version=data.get("model_version") if data.get("model_version") else data.get(
                               'job_parameters').get("model_version"))
    except Exception:
        stat_logger.error(traceback.format_exc())


def job_run_operate(project_id, role, party_id, v_sample_list, user,job_type=None):
    v_ids = []
    create_time = datetime_format(datetime.now())
    for v_sample in v_sample_list:
        p_id = get_uuid()
        v_sample["id"] = p_id
        v_sample["party_id"] = party_id
        v_sample["creator"] = user
        v_sample["create_time"] = create_time
        v_sample["role"] = role
        v_ids.append(p_id)
    if v_sample_list:
        VSampleInfoService.insert_many(v_sample_list)
    # todo project_sample
    project_sample_list = []
    for v_sample_id in v_ids:
        project_sample_list.append({
            "id": get_uuid(),
            "project_id": project_id,
            "sample_id": v_sample_id,
            "sample_type": SampleTypeEnum.FUSION.value,
            "creator": user,
            "create_time": create_time,
            "job_type":job_type
        })
    ProjectSampleService.insert_many(project_sample_list)
    return v_ids


def get_fusion_header(job_id, role, party_id):
    # todo 获取数据融合特征列(由于获取不到union的组件名称，可能要废弃)
    fusion_task = TaskService.get_fusion_task(job_id, role, party_id, only_latest=True)
    if not fusion_task:
        return False, 'can not find fusion data'
    else:
        request_data = {'function': 'component_output_data',
                        'job_id': job_id,
                        'party_id': party_id,
                        'role': role,
                        'component_name': fusion_task.f_component_name,
                        'local': {'party_id': party_id, 'role': role}
                        }
        import_component_output_depend(fusion_task.f_provider_info)
        try:
            output_tables_meta = get_component_output_tables_meta(task_data=request_data)
        except Exception as e:
            stat_logger.exception(e)
            return False, str(e)
        if not output_tables_meta:
            return False, 'no data'
        for output_name, output_table_meta in output_tables_meta.items():
            is_str = False
            extend_header = []
            with Session() as sess:
                output_table = sess.get_table(name=output_table_meta.get_name(),
                                              namespace=output_table_meta.get_namespace())
                if output_table:
                    for k, v in output_table.collect():
                        data_line, is_str, extend_header = feature_utils.get_component_output_data_line(src_key=k,
                                                                                                        src_value=v)
                        break
            if output_table.count():
                # get meta
                header = get_component_output_data_schema(output_table_meta=output_table_meta,
                                                          is_str=is_str,
                                                          extend_header=extend_header)
            else:
                header = []
            return True, header


def diy_job_command(job_id, endpoint, src_role, src_party_id, dest_party_ids, json_bodys=None, parallel=False):
    federated_response = {}
    threads = []
    for index, dest_party_id in enumerate(dest_party_ids):
        json_body = json_bodys[index]
        args = (job_id, src_role, src_party_id, dest_party_id, endpoint, json_body, federated_response)
        if parallel:
            t = threading.Thread(target=diy_federated_command, args=args)
            threads.append(t)
            t.start()
        else:
            diy_federated_command(*args)
    for thread in threads:
        thread.join()
    return diy_return_federated_response(federated_response=federated_response)


def diy_federated_command(job_id, src_role, src_party_id, dest_party_id, endpoint, body,
                          federated_response):
    st = base_utils.current_timestamp()
    log_msg = f"sending {endpoint} federated command"
    schedule_logger(job_id).info(start_log(msg=log_msg))
    try:
        response = federated_api(job_id=job_id,
                                 method='POST',
                                 endpoint=endpoint,
                                 src_role=src_role,
                                 src_party_id=src_party_id,
                                 dest_party_id=dest_party_id,
                                 json_body=body if body else {},
                                 federated_mode=ENGINES["federated_mode"])
    except Exception as e:
        schedule_logger(job_id=job_id).exception(e)
        response = {
            "retcode": RetCode.FEDERATED_ERROR,
            "retmsg": "Federated schedule error, {}".format(e)
        }
    if response["retcode"] != RetCode.SUCCESS:
        if response["retcode"] == RetCode.NOT_EFFECTIVE:
            schedule_logger(job_id).warning(
                warning_log(msg=log_msg, role="diy_federated_api_no_role", party_id=dest_party_id))
        else:
            schedule_logger(job_id).error(
                failed_log(msg=log_msg, role="diy_federated_api_no_role", party_id=dest_party_id,
                           detail=response["retmsg"]))
    federated_response[dest_party_id] = response
    et = base_utils.current_timestamp()
    schedule_logger(job_id).info(f"{log_msg} use {et - st} ms")


def diy_return_federated_response(federated_response):
    retcode_set = set()
    for party_id in federated_response.keys():
        retcode_set.add(federated_response[party_id]["retcode"])
    if len(retcode_set) == 1 and RetCode.SUCCESS in retcode_set:
        federated_scheduling_status_code = FederatedSchedulingStatusCode.SUCCESS
    elif RetCode.EXCEPTION_ERROR in retcode_set:
        federated_scheduling_status_code = FederatedSchedulingStatusCode.ERROR
    elif retcode_set == {RetCode.SUCCESS, RetCode.NOT_EFFECTIVE}:
        federated_scheduling_status_code = FederatedSchedulingStatusCode.NOT_EFFECTIVE
    elif RetCode.SUCCESS in retcode_set:
        federated_scheduling_status_code = FederatedSchedulingStatusCode.PARTIAL
    else:
        federated_scheduling_status_code = FederatedSchedulingStatusCode.FAILED
    return federated_scheduling_status_code, federated_response


def diy_start_task_worker(worker_name, task: Task, task_parameters: RunParameters = None,
                          executable: list = None, extra_env: dict = None, **kwargs):
    worker_id, config_dir, log_dir = WorkerManager.get_process_dirs(worker_name=worker_name,
                                                                    job_id=task.f_job_id,
                                                                    role=task.f_role,
                                                                    party_id=task.f_party_id,
                                                                    task=task)

    session_id = job_utils.generate_session_id(task.f_task_id, task.f_task_version, task.f_role, task.f_party_id)
    federation_session_id = job_utils.generate_task_version_id(task.f_task_id, task.f_task_version)

    info_kwargs = {}
    specific_cmd = []
    if worker_name is WorkerName.TASK_EXECUTOR:
        from fate_flow.worker.task_executor import TaskExecutor
        module_file_path = sys.modules[TaskExecutor.__module__].__file__
    else:
        raise Exception(f"not support {worker_name} worker")

    if task_parameters is None:
        task_parameters = RunParameters(**job_utils.get_job_parameters(task.f_job_id, task.f_role, task.f_party_id))

    config = task_parameters.to_dict()
    config["src_user"] = kwargs.get("src_user")
    config_path, result_path = WorkerManager.get_config(config_dir=config_dir, config=config, log_dir=log_dir)

    if executable:
        process_cmd = executable
    else:
        process_cmd = [sys.executable or "python3"]

    common_cmd = [
        module_file_path,
        "--job_id", task.f_job_id,
        "--component_name", task.f_component_name,
        "--task_id", task.f_task_id,
        "--task_version", task.f_task_version,
        "--role", task.f_role,
        "--party_id", task.f_party_id,
        "--config", config_path,
        '--result', result_path,
        "--log_dir", log_dir,
        "--parent_log_dir", os.path.dirname(log_dir),
        "--worker_id", worker_id,
        "--run_ip", RuntimeConfig.JOB_SERVER_HOST,
        "--job_server", f"{RuntimeConfig.JOB_SERVER_HOST}:{RuntimeConfig.HTTP_PORT}",
        "--session_id", session_id,
        "--federation_session_id", federation_session_id,
    ]
    process_cmd.extend(common_cmd)
    process_cmd.extend(specific_cmd)
    env = WorkerManager.get_env(task.f_job_id, task.f_provider_info)
    if extra_env:
        env.update(extra_env)
    schedule_logger(task.f_job_id).info(
        f"task {task.f_task_id} {task.f_task_version} on {task.f_role} {task.f_party_id} {worker_name} worker subprocess is ready")
    p = process_utils.run_subprocess(job_id=task.f_job_id, config_dir=config_dir, process_cmd=process_cmd,
                                     added_env=env, log_dir=log_dir, cwd_dir=config_dir, process_name=worker_name.value,
                                     process_id=worker_id)
    p.wait()
    returncode = p.returncode
    if returncode != 0:
        std_path = get_std_path(log_dir=log_dir, process_name=worker_name.value, process_id=p.pid)
        std = open(std_path, 'r')
        err_msg = std.read()
        return {"err_msg", "err_msg " + err_msg}
    return {"run_pid": p.pid, "worker_id": worker_id, "cmd": process_cmd}


def diy_start_task(job_id, component_name, task_id, task_version, role, party_id, **kwargs):
    job_dsl = job_utils.get_job_dsl(job_id, role, party_id)
    PrivilegeAuth.authentication_component(job_dsl, src_party_id=kwargs.get('src_party_id'),
                                           src_role=kwargs.get('src_role'),
                                           party_id=party_id, component_name=component_name)

    schedule_logger(job_id).info(
        f"try to start task {task_id} {task_version} on {role} {party_id} executor subprocess")
    task_executor_process_start_status = False
    task_info = {
        "job_id": job_id,
        "task_id": task_id,
        "task_version": task_version,
        "role": role,
        "party_id": party_id,
    }
    is_failed = False
    try:
        task = JobSaver.query_task(task_id=task_id, task_version=task_version, role=role, party_id=party_id)[0]
        run_parameters_dict = job_utils.get_job_parameters(job_id, role, party_id)
        run_parameters_dict["src_user"] = kwargs.get("src_user")
        run_parameters = RunParameters(**run_parameters_dict)

        config_dir = job_utils.get_task_directory(str(job_id), str(role), str(party_id), str(component_name),
                                                  str(task_id), str(task_version))
        os.makedirs(config_dir, exist_ok=True)

        run_parameters_path = os.path.join(config_dir, 'task_parameters.json')
        with open(run_parameters_path, 'w') as fw:
            fw.write(json_dumps(run_parameters_dict))

        schedule_logger(job_id).info(f"use computing engine {run_parameters.computing_engine}")
        task_info["engine_conf"] = {"computing_engine": run_parameters.computing_engine}
        run_info = diy_start_task_worker(worker_name=WorkerName.TASK_EXECUTOR, task=task,
                                         task_parameters=run_parameters)
        task_info.update(run_info)
        task_info["start_time"] = current_timestamp()
        task_executor_process_start_status = True
        if run_info.get("err_msg"):
            is_failed = True
            return run_info["err_msg"]
    except Exception as e:
        schedule_logger(job_id).exception(e)
        is_failed = True
        return {" "}
    finally:
        try:
            Task.update_task(task_info=task_info)
            task_info["party_status"] = TaskStatus.RUNNING
            Task.update_task_status(task_info=task_info)
            if is_failed:
                task_info["party_status"] = TaskStatus.FAILED
                Task.update_task_status(task_info=task_info)

        except Exception as e:
            schedule_logger(job_id).exception(e)
        schedule_logger(job_id).info(
            "task {} {} on {} {} executor subprocess start {}".format(task_id, task_version, role, party_id,
                                                                      "success" if task_executor_process_start_status else "failed"))


def diy_start_job(job_id):
    jobs = JobSaver.query_job(is_initiator=True, order_by="create_time", reverse=False, job_id=job_id)
    if len(jobs):
        RuntimeConfig.init_config(JOB_SERVER_HOST=HOST, HTTP_PORT=HTTP_PORT)
        job = jobs[0]
        apply_status_code, federated_response = FederatedScheduler.resource_for_job(job=job,
                                                                                    operation_type=ResourceOperation.APPLY)
        if apply_status_code == FederatedSchedulingStatusCode.SUCCESS:
            federated_scheduling_status_code, federated_response = FederatedScheduler.start_job(job=job)
            if federated_scheduling_status_code == FederatedSchedulingStatusCode.SUCCESS:
                tasks = JobSaver.query_task(job_id=job_id)
                if tasks:
                    task = tasks[0]
                    component_name, task_id, task_version, role, party_id = task.f_component_name, task.f_task_id, task.f_task_version, task.f_role, task.f_party_id
                    # 运行task
                    err_msg = diy_start_task(job_id, component_name, task_id, task_version, role, party_id)
                    if err_msg:
                        return {"error": err_msg}
            else:
                return {"error": federated_response}
        else:
            return {"error": federated_response}

        # 修改job end 状态
        jobs = JobSaver.query_job(is_initiator=True, status=JobStatus.RUNNING, order_by="create_time", reverse=False,
                                  job_id=job_id)
        if jobs:
            job = jobs[0]
            DAGScheduler.schedule_running_job(job=job)


    else:
        return {"error": "DAGScheduler.submit do not have job_id"}


def check_table_exist(table_name, engine_url):
    sql = "show tables like '{}'".format(table_name)
    con = create_engine(engine_url)
    try:
        df = pd.read_sql(sql, con)
        if df.empty:
            return False, "{} 表不存在".format(table_name)
        else:
            return True, None
    except Exception as e:
        return False, str(e)

def mysql_read_schema(engine_url,sql=None):
    if sql:
        try:
            con = create_engine(engine_url)
            df = pd.read_sql(sql, con)
            if df.empty:
                return None,None,None
            if len(list(set(df.columns[1:]))) !=len(df.columns[1:]):
                return None,None,None
            header = ",".join(df.columns[1:].tolist())
            sid= df.columns[0]
            return sid,header,df[:5]
        except:
            pass
    return None, None, None


def get_mysql_column_sid(db, table_name, engine_url, id_delimiter):
    e = create_engine(engine_url)
    future_column_sql = "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}'".format(
        db, table_name)
    sid_sql = "SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}'".format(
        db, table_name)
    future_column_df = pd.read_sql(future_column_sql, e)
    sid_df = pd.read_sql(sid_sql, e)
    all_columns = future_column_df["COLUMN_NAME"].astype(str).tolist()
    sid = sid_df["COLUMN_NAME"].astype(str).tolist()
    future_columns = id_delimiter.join(set(all_columns).difference(set(sid)))
    id_column = id_delimiter.join(sid)
    return future_columns, id_column
