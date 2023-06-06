import re
import traceback
import pandas as pd
from ruamel import yaml

from fate_flow.settings import stat_logger
from fate_flow.utils.log_sharing_utils import LogCollector
from fate_flow.web_server.db_service.project_service import TaskService
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError
from fate_flow.db.runtime_config import RuntimeConfig
from fate_flow.web_server.fl_config import config


def get_run_ips(job_id, role, party_id):
    run_ip_df = pd.DataFrame(list(TaskService.get_run_ip(job_id, role, party_id).dicts()))
    run_ip_df.drop_duplicates(subset=["f_run_ip"],inplace=True)
    run_ips = []
    if run_ip_df.empty:
        return run_ips
    run_ip_list = run_ip_df.f_run_ip.tolist()
    for run_ip in run_ip_list:
        if run_ip not in run_ips:
            run_ips.append(run_ip)
    return run_ips


class SshClient:
    _instance = None
    ssh_info = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            with open(config.ssh_path, encoding='utf8') as f:
                cls.ssh_info = yaml.safe_load(f)
            return cls._instance
        else:
            return cls._instance

    def __init__(self, host):
        self.ssh_client = SSHClient()
        self.host = host
        try:
            self.port = self.ssh_info[host]["port"]
            self.username = self.ssh_info[host]["username"]
            self.password = self.ssh_info[host]["password"]
        except Exception as e:
            stat_logger.exception(traceback.format_exc())
            print("异常ssh配置有误")
            raise KeyError("没有ssh 配置信息")

    def ssh_login(self):
        try:
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            self.ssh_client.connect(self.host, port=self.port, username=self.username, password=self.password)
            return True
        except AuthenticationException:
            stat_logger.exception("ssh {} username or password error".format(self.host))
            return False
        except NoValidConnectionsError:
            stat_logger.exception("ssh {} connect time out".format(self.host))
            return False
        except Exception as e:
            stat_logger.exception(traceback.format_exc())
            return False

    def execute(self, command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.read().decode()

    def close(self):
        self.ssh_client.close()


class GetLogInfo:
    def __init__(self, run_ips, job_id, role, party_id):
        self.run_ips = run_ips
        self.job_id = job_id
        self.role = role
        self.party_id = party_id

    @staticmethod
    def cat_log(log_server, log_file_path, begin, end):
        line_list = []
        if begin and end:
            cmd = f"cat {log_file_path} | tail -n +{begin}| head -n {end-begin+1}"
        else:
            cmd = f"cat {log_file_path}"
        lines = log_server.execute(cmd)
        if lines:
            line_list = []
            line_num = begin if begin else 1
            for line in lines.strip().split("\n"):
                match_ip = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line)
                if match_ip:
                    for ip in match_ip:
                        line = re.sub(ip, "xxx.xxx.xxx.xxx", line)
                line_list.append({"line_num": line_num, "content": line})
                line_num += 1
        return line_list

    def get_log_size(self):
        res_data = {"partyInfo": 0, "partyWarning": 0, "partyError": 0, "partyDebug": 0}
        command = "cat {} |wc -l"
        request_data = {
            "role": self.role,
            "party_id": self.party_id,
            "job_id": self.job_id,
            "log_type": None
        }
        for run_ip in self.run_ips:
            log_collector = LogCollector(**request_data)
            if run_ip == RuntimeConfig.JOB_SERVER_HOST:
                log_server = log_collector
            else:
                log_server = SshClient(run_ip)
                if not log_server.ssh_login():
                    continue
            for log_type in res_data.keys():
                log_collector.log_type = log_type
                log_server.log_type = log_type
                res_data[log_type] += int(log_server.execute(command.format(log_collector.get_log_file_path())))
            if run_ip != RuntimeConfig.JOB_SERVER_HOST:
                log_server.close()
        return res_data

    def get_log_lines(self, log_type, begin=None, end=None):
        request_data = {
            "role": self.role,
            "party_id": config.local_party_id,
            "job_id": self.job_id,
            "log_type": log_type
        }
        line_list = []
        line_num = int(begin) if begin else 1
        for run_ip in self.run_ips:
            log_collector = LogCollector(**request_data)
            if run_ip == RuntimeConfig.JOB_SERVER_HOST:
                log_server = log_collector
            else:
                log_server = SshClient(run_ip)
                if not log_server.ssh_login():
                    continue
            log_file_path = log_collector.get_log_file_path()
            if begin and end:
                end=int(end)
                begin=int(begin)
                cmd = f"cat {log_file_path} | tail -n +{begin}| head -n {end-begin+1}"
            else:
                cmd = f"cat {log_file_path}"
            lines = log_server.execute(cmd)
            if lines:
                for line in lines.strip().split("\n"):
                    match_ip = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line)
                    if match_ip:
                        for ip in match_ip:
                            line = re.sub(ip, "xxx.xxx.xxx.xxx", line)
                    line_list.append({"line_num": line_num, "content": line})
                    line_num += 1
            if run_ip != RuntimeConfig.JOB_SERVER_HOST:
                log_server.close()
        return line_list
