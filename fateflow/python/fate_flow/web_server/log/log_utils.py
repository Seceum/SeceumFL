import os
import re

from fate_flow.utils.base_utils import get_fate_flow_directory


class Log_seceum_audit():
    def __init__(self,  job_id):
        self.job_id = job_id


    def get_log_file_path(self):
        audit_path= os.path.join(get_fate_flow_directory('logs'), self.job_id , "fate_flow_audit.log")
        if os.path.exists(audit_path):
            return audit_path


    def cat_log(self):
        line_list = []

        cmd = f"cat {self.get_log_file_path()}"
        lines = self.execute(cmd)
        if lines:
            line_list = []
            line_num = 1
            for line in lines.strip().split("\n"):
                match_ip = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', line)
                if match_ip:
                    for ip in match_ip:
                        line = re.sub(ip, "xxx.xxx.xxx.xxx", line)
                line_list.append({"line_num": line_num, "content": line})
                line_num += 1
        return line_list


    @staticmethod
    def execute(cmd):
        res = os.popen(cmd)
        data = res.read()
        res.close()
        return data