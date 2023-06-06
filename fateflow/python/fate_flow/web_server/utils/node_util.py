import copy
import os
import subprocess
from fate_arch.common.file_utils import load_json_conf_real_time, rewrite_json_file, get_project_base_directory
from fate_flow.entity.run_status import FederatedSchedulingStatusCode
from fate_flow.web_server.fl_config import eggroll_route_table_path, docker_model
from fate_flow.web_server.fl_scheduling_apps.fl_command import FL_Scheduler


def add_rollsite_node(party_id,rollsite_ip,rollsite_port,command_body=None,command=None):
    config = load_json_conf_real_time(conf_path=eggroll_route_table_path) or dict()
    pre_config = copy.deepcopy(config)
    config["route_table"][party_id]={"default":[{'port': int(rollsite_port), 'ip':rollsite_ip }]}
    rewrite_json_file(eggroll_route_table_path, config)
    if docker_model:
        subprocess.call("docker-compose restart rollsite",
                        shell=True,timeout=10)
    else:
        subprocess.call("sh %s all restart" % (os.path.join(get_project_base_directory(), "eggroll/bin/eggroll.sh")),
                        shell=True)
    if command=="restart":
        return None,None
    status_code, response = FL_Scheduler.node_command("verify_node_public_key", command_body,
                                                      specific_para=[("host", [party_id])])
    if status_code != FederatedSchedulingStatusCode.SUCCESS:
        rewrite_json_file(eggroll_route_table_path, pre_config)
        if docker_model:
            subprocess.call("docker-compose restart rollsite",
                            shell=True, timeout=10)
        else:
            subprocess.call(
                "sh %s all restart" % (os.path.join(get_project_base_directory(), "eggroll/bin/eggroll.sh")),
                shell=True)
        return False,str("合作方代理 or party_id 对应失败")
    elif response["host"][party_id]["data"] == False:
        rewrite_json_file(eggroll_route_table_path, pre_config)
        subprocess.call("sh %s all restart" % (os.path.join(get_project_base_directory(), "eggroll/bin/eggroll.sh")),
                        shell=True)
        return False, "public_key error"
    return True,None

# def update_rollsite_node(party_id,rollsite_ip,rollsite_port,fateflow_ip,fateflow_port):
#     config = load_json_conf_real_time(conf_path=eggroll_route_table_path) or dict()
#     # party_id="10002"
#     # rollsite_ip='192.168.1.153'
#     # rollsite_port=9370
#     # fateflow_ip='192.168.1.153'
#     # fateflow_port=9360
#     if config["route_table"].get(party_id):
#         config["route_table"][party_id]={"default":[{'port': rollsite_port, 'ip':rollsite_ip }],'fateflow': [{'port': fateflow_port, 'ip': fateflow_ip}]}
#         rewrite_json_file(eggroll_route_table_path, config)
#         subprocess.call("sh %s all restart"%(os.path.join(get_project_base_directory(), "eggroll/bin/eggroll.sh")),shell=True)
#     else:
#         print("已存在")

def delete_rollsite_node(party_id):
    config =load_json_conf_real_time(conf_path=eggroll_route_table_path) or dict()
    del config["route_table"][party_id]
    rewrite_json_file(eggroll_route_table_path, config)
    subprocess.call("sh %s all restart"%(os.path.join(get_project_base_directory(), "eggroll/bin/eggroll.sh")),shell=True)
