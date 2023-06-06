import os
from fate_arch.common import file_utils
from fate_arch.common.file_utils import get_project_base_directory
from fate_flow.utils.log_utils import getLogger



class Properties:
    def __init__(self, file_name):
        self.file_name = file_name
        self.properties = {}
        try:
            fopen = open(self.file_name, 'r')
            for line in fopen:
                line = line.strip()
                if line.find('=') > 0 and not line.startswith('#'):
                    strs = line.split('=')
                    self.properties[strs[0].strip()] = strs[1].strip()
        except Exception as e:
            # raise e
            print(str(e))
        else:
            fopen.close()
    @classmethod
    def has_key(self, key):
        return key in self.properties

    def get(self, key, default_value=''):
        if key in self.properties:
            return self.properties[key]
        return default_value

    def put(self, key, value):
        self.properties[key] = value


def get_cf():
    config_path = os.path.join("conf", "fl_config.yaml")
    cont = file_utils.load_yaml_conf(config_path)
    party_id =Properties(str(os.path.join(get_project_base_directory(), "eggroll/conf/eggroll.properties"))).get("eggroll.rollsite.party.id")
    if not party_id:
        raise("eggroll.properties 没有party_id")
    cont["local_party_id"] = party_id
    cont["local_party_name"] = "party_name_%s"%party_id
    return cont


class Config:
    cf = get_cf()
    namespace = cf["namespace"]
    docker_model = cf.get("docker_model")
    is_chain = cf.get("is_chain")
    login_rsa = cf.get("login_rsa")
    local_party_id = str(cf["local_party_id"])
    local_party_name = "本地节点"
    partition = cf["partition"]
    token_expires_in = 3600 * 48
    ssh_path = os.path.join(get_project_base_directory(), "conf", "ssh.yaml")
    secret_key = '%@mzit!i8b*$zc&6oev96=6B10B159CF'
    LICENSE_PATH = cf["license_path"]


license_logger = getLogger("license_log")
config = Config
eggroll_route_table_path = os.path.join(get_project_base_directory(), "eggroll/conf/route_table.json")
PARTY_ID =config.local_party_id
docker_model = config.docker_model
url_code_dict={
        '/v1/user/login':"1010",
        '/v1/user/logout':"1020",
        '/v1/user/setting':"1030",
        '/v1/user/add':"2010",
        '/v1/user/delete':"2020",
        '/v1/user/edit/*':"2030",
        '/v1/node/add':"2040",
        '/v1/node/delete/*':"2050",
        '/v1/node/edit/*':"2060",
        '/v1/role/add':"2070",
        '/v1/role/delete':"2080",
        '/v1/role/edit': "2090",
        '/v1/own/add': "3010",
        '/v1/own/on_off_line':"3020", #"1"上线 “2”下线
        '/v1/own/edit_fields/*':"3040",
        '/v1/approve/status':"3050", #1授权同意，2授权拒绝，3取消授权
        '/v1/project/add':"4010",
        '/v1/project/edit/*':"4020",
        '/v1/project/delete/*':"4030",
        '/v1/project/canvas_add':"5010",#新建任务
        '/v1/canvas/save':"5020",#编辑任务
        '/v1/project/detail/delete':"5030",#删除任务
        '/v1/canvas/model_store':"6010",
        '/v1/model_manage/delete':"6020",#删除模型
        '/v1/model_manage/export/*':"6030",#模型导出
        '/v1/model_manage/release': "6040",  # 模型发布
        '/v1/model_manage/approval':"6050",#模型授权
    }