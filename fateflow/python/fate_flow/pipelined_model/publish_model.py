#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import time
import grpc
import os

from fate_flow.controller.job_controller import JobController
from fate_flow.settings import HOST, HTTP_PORT, FATE_FLOW_MODEL_TRANSFER_ENDPOINT, \
    USE_REGISTRY, FATE_SERVERING_ENDPOINT
from fate_arch.common.base_utils import json_loads
from fate_arch.protobuf.python import model_service_pb2, model_service_pb2_grpc

from fate_flow.model.sync_model import SyncModel
from fate_flow.pipelined_model import pipelined_model
from fate_flow.pipelined_model.homo_model_deployer.model_deploy import model_deploy
from fate_flow.settings import (
    ENABLE_MODEL_STORE, FATE_FLOW_MODEL_TRANSFER_ENDPOINT,
    GRPC_OPTIONS, HOST, HTTP_PORT, USE_REGISTRY, stat_logger,
)
from fate_flow.utils import model_utils


def generate_publish_model_info(config_data):
    model_id = config_data['job_parameters']['model_id']
    model_version = config_data['job_parameters']['model_version']
    config_data['model'] = {}
    for role, role_party in config_data.get("role").items():
        config_data['model'][role] = {}
        for party_id in role_party:
            config_data['model'][role][party_id] = {
                'model_id': model_utils.gen_party_model_id(model_id, role, party_id),
                'model_version': model_version
            }

'''
def load_model(config_data):
    stat_logger.info("load_model {}".format(config_data))
    if not config_data.get('servings'):
        return 100, 'Please configure servings address'

    for serving in config_data['servings']:

        local_role = config_data.get('local', {}).get('role', '')

        add_model_req = {
            "serviceId": "",
            "modelUrl": f"http://{HOST}:{HTTP_PORT}{FATE_FLOW_MODEL_TRANSFER_ENDPOINT}",
            "role": local_role
        }

        for role_name, role_model_config in config_data.get("model", {}).items():

            if role_name != local_role:
                continue
            for _party_id, role_party_model_config in role_model_config.items():
                add_model_req["table_name"] = role_party_model_config['model_version']
                add_model_req["namespace"] = role_party_model_config["model_id"]
                add_model_req["serviceId"] = config_data['service_id']  # role_party_model_config["model_version"]
            add_model_req["role"] = role_name
            stat_logger.info("Load_model add_model_req {}".format(add_model_req))
            servering_url = "http://{}{}/add".format(serving, FATE_SERVERING_ENDPOINT)
            stat_logger.info("Load_model servering_url {}".format(servering_url))
            response = requests.post(servering_url, data=json.dumps(add_model_req))
            stat_logger.info("load_model send req to {} {}".format(servering_url, add_model_req))

    return 0, 'success'


'''
def load_model(config_data):
    stat_logger.info(config_data)
    if not config_data.get('servings'):
        return 100, 'Please configure servings address'

    for serving in config_data['servings']:
        with grpc.insecure_channel(serving, GRPC_OPTIONS) as channel:
            stub = model_service_pb2_grpc.ModelServiceStub(channel)
            load_model_request = model_service_pb2.PublishRequest()
            for role_name, role_partys in config_data.get("role", {}).items():
                for _party_id in role_partys:
                    load_model_request.role[role_name].partyId.append(str(_party_id))
            for role_name, role_model_config in config_data.get("model", {}).items():
                for _party_id, role_party_model_config in role_model_config.items():
                    load_model_request.model[role_name].roleModelInfo[str(_party_id)].tableName = \
                        role_party_model_config['model_version']
                    load_model_request.model[role_name].roleModelInfo[str(_party_id)].namespace = \
                        role_party_model_config['model_id']

            stat_logger.info('request serving: {} load model'.format(serving))
            load_model_request.local.role = config_data.get('local', {}).get('role', '')
            load_model_request.local.partyId = str(config_data.get('local', {}).get('party_id', ''))
            load_model_request.loadType = config_data['job_parameters'].get("load_type", "FATEFLOW")
            # make use of 'model.transfer.url' in serving server
            use_serving_url = config_data['job_parameters'].get('use_transfer_url_on_serving', False)
            if not USE_REGISTRY and not use_serving_url:
                load_model_request.filePath = f"http://{HOST}:{HTTP_PORT}{FATE_FLOW_MODEL_TRANSFER_ENDPOINT}"
            else:
                load_model_request.filePath = config_data['job_parameters'].get("file_path", "")
            stat_logger.info(load_model_request)
            response = stub.publishLoad(load_model_request)
            stat_logger.info(
                '{} {} load model status: {}'.format(load_model_request.local.role, load_model_request.local.partyId,
                                                     response.statusCode))
            if response.statusCode != 0:
                return response.statusCode, '{} {}'.format(response.message, response.error)
    return 0, 'success'



def bind_model_service(config_data):
    if not config_data.get('servings'):
        return 100, 'Please configure servings address'

    service_id = str(config_data.get('service_id', ''))
    initiator_role = config_data['initiator']['role']
    initiator_party_id = str(config_data['initiator']['party_id'])
    model_id = config_data['job_parameters']['model_id']
    model_version = config_data['job_parameters']['model_version']

    for serving in config_data['servings']:
        with grpc.insecure_channel(serving, GRPC_OPTIONS) as channel:
            stub = model_service_pb2_grpc.ModelServiceStub(channel)
            publish_model_request = model_service_pb2.PublishRequest()
            publish_model_request.serviceId = service_id

            # {"role": {"guest": ["9999"], "host": ["10000"], "arbiter": ["9999"]}}
            for role_name, role_party in config_data.get("role").items():
                publish_model_request.role[role_name].partyId.extend([str(party_id) for party_id in role_party])

            party_model_id = model_utils.gen_party_model_id(model_id, initiator_role, initiator_party_id)
            publish_model_request.model[initiator_role].roleModelInfo[initiator_party_id].tableName = model_version
            publish_model_request.model[initiator_role].roleModelInfo[initiator_party_id].namespace = party_model_id

            publish_model_request.local.role = initiator_role
            publish_model_request.local.partyId = initiator_party_id

            stat_logger.info(publish_model_request)
            response = stub.publishBind(publish_model_request)
            stat_logger.info(response)
            if response.statusCode != 0:
                return response.statusCode, response.message

    return 0, None


def download_model(party_model_id, model_version):
    if ENABLE_MODEL_STORE:
        sync_model = SyncModel(
            party_model_id=party_model_id,
            model_version=model_version,
        )
        if sync_model.remote_exists():
            sync_model.download(True)

    model = pipelined_model.PipelinedModel(party_model_id, model_version)
    if not model.exists():
        return {}
    return model.collect_models(in_bytes=True)


def convert_homo_model(request_data):
    party_model_id = model_utils.gen_party_model_id(model_id=request_data["model_id"],
                                                    role=request_data["role"],
                                                    party_id=request_data["party_id"])
    model_version = request_data.get("model_version")
    model = pipelined_model.PipelinedModel(model_id=party_model_id, model_version=model_version)
    if not model.exists():
        return 100, 'Model {} {} does not exist'.format(party_model_id, model_version), None

    define_meta = model.pipelined_component.get_define_meta()

    framework_name = request_data.get("framework_name")
    detail = []
    # todo: use subprocess?
    convert_tool = model.get_homo_model_convert_tool()
    for key, value in define_meta.get("model_proto", {}).items():
        if key == 'pipeline':
            continue
        for model_alias in value.keys():
            buffer_obj = model.read_component_model(key, model_alias)
            module_name = define_meta.get("component_define", {}).get(key, {}).get('module_name')
            converted_framework, converted_model = convert_tool.model_convert(model_contents=buffer_obj,
                                                                              module_name=module_name,
                                                                              framework_name=framework_name)
            if converted_model:
                converted_model_dir = os.path.join(model.pipelined_component.variables_data_path, key, model_alias,
                                                   "converted_model")
                os.makedirs(converted_model_dir, exist_ok=True)

                saved_path = convert_tool.save_converted_model(converted_model,
                                                               converted_framework,
                                                               converted_model_dir)
                detail.append({
                    "component_name": key,
                    "model_alias": model_alias,
                    "converted_model_path": saved_path
                })
    if len(detail) > 0:
        return (0,
                f"Conversion of homogeneous federated learning component(s) in model "
                f"{party_model_id}:{model_version} completed. Use export or homo/deploy "
                f"to download or deploy the converted model.",
                detail)
    else:
        return 100, f"No component in model {party_model_id}:{model_version} can be converted.", None


def deploy_homo_model(request_data):
    party_model_id = model_utils.gen_party_model_id(model_id=request_data["model_id"],
                                                    role=request_data["role"],
                                                    party_id=request_data["party_id"])
    model_version = request_data["model_version"]
    component_name = request_data['component_name']
    service_id = request_data['service_id']
    framework_name = request_data.get('framework_name')
    model = pipelined_model.PipelinedModel(model_id=party_model_id, model_version=model_version)
    if not model.exists():
        return 100, 'Model {} {} does not exist'.format(party_model_id, model_version), None

    # get the model alias from the dsl saved with the pipeline
    pipeline = model.read_pipeline_model()
    train_dsl = json_loads(pipeline.train_dsl)
    if component_name not in train_dsl.get('components', {}):
        return 100, 'Model {} {} does not contain component {}'. \
            format(party_model_id, model_version, component_name), None

    model_alias_list = train_dsl['components'][component_name].get('output', {}).get('model')
    if not model_alias_list:
        return 100, 'Component {} in Model {} {} does not have output model'. \
            format(component_name, party_model_id, model_version), None

    # currently there is only one model output
    model_alias = model_alias_list[0]
    converted_model_dir = os.path.join(model.pipelined_component.variables_data_path, component_name, model_alias,
                                       "converted_model")
    if not os.path.isdir(converted_model_dir):
        return 100, '''Component {} in Model {} {} isn't converted'''. \
            format(component_name, party_model_id, model_version), None

    # todo: use subprocess?
    convert_tool = model.get_homo_model_convert_tool()
    if not framework_name:
        module_name = train_dsl['components'][component_name].get('module')
        buffer_obj = model.read_component_model(component_name, model_alias)
        framework_name = convert_tool.get_default_target_framework(model_contents=buffer_obj, module_name=module_name)

    model_object = convert_tool.load_converted_model(base_dir=converted_model_dir,
                                                     framework_name=framework_name)
    deployed_service = model_deploy(party_model_id,
                                    model_version,
                                    model_object,
                                    framework_name,
                                    service_id,
                                    request_data['deployment_type'],
                                    request_data['deployment_parameters'])
    return (0,
            f"An online serving service is started in the {request_data['deployment_type']} system.",
            deployed_service)

def fakePredict(mdl_param, local_party_id):
    from fate_flow.web_server.pipeline_wrapper import WrapperFactory
    from fate_flow.web_server.utils.common_util import model_id_get_hosts
    # 多个job 包含多个组件
    # mdl_param: {
    #     "model_id": "guest-9999#host-10000#model",
    #     "model_versions": [
    #         ("202210201120144748370",["data_transform_0"]),
    #         # 多个feature selection 组件，model version和组件需要一一对应起来
    #         ("202210201120144748371",["hetero_feature_selection_0"])
    #     ]
    # }
    cpn_init = {
        "jid4reader": mdl_param["model_versions"][-1][0],
        "cpn4reader": "outs",
        "pid": local_party_id,
        "guest": local_party_id,
        "hosts": model_id_get_hosts(mdl_param["model_id"])
    }

    pip = WrapperFactory("Prediction")(**cpn_init)
    pip.setReader()
    jid, mdl_info = pip.exe(mdl_param)
    try:
        pip.pip.continuously_fit()
    except Exception as e:
        pass
    JobController.save_pipelined_model(jid, role="guest", party_id=local_party_id)
    return mdl_info, pip.pip.get_component_list()

def composeDAG(mdl_param, role, fake_mdinfo, party_id, cpn_nm_lst):
    from fate_flow.pipelined_model.pipelined_component import PipelinedComponent
    from fate_flow.db.db_models import PipelineComponentMeta
    new_cpn = PipelinedComponent(role=role, party_id=party_id, model_id=fake_mdinfo["model_id"], model_version=fake_mdinfo["model_version"])
    for ii,(vid, mdnm) in enumerate(mdl_param["model_versions"]):
        mdnm = mdnm[0]
        mdnm = mdnm.split(":")[0]
        if ii + 1 == len(mdl_param["model_versions"]): mdnm = "outs"
        for nm in cpn_nm_lst:
            if nm.find(mdnm) >=0:
                mdnm = nm
                break
        else: continue
        cpn = PipelinedComponent(role=role, party_id=party_id, model_id=mdl_param["model_id"], model_version=vid)
        cmd = "mkdir -p {};".format(new_cpn.run_parameters_path)
        cmd += "cp -arp {} {}".format(cpn.run_parameters_path / "outs", new_cpn.run_parameters_path / mdnm)
        stat_logger.info(cmd)
        os.system(cmd)
        cmd = "mkdir -p {};".format(new_cpn.variables_data_path)
        cmd += "cp -arp {} {}".format(cpn.variables_data_path / "outs", new_cpn.variables_data_path / mdnm)
        stat_logger.info(cmd)
        os.system(cmd)
        cpn.replicate_define_meta({"f_model_version": fake_mdinfo["model_version"], "f_component_name": mdnm,
                                       "f_model_id": fake_mdinfo["model_id"]},
                                      (PipelineComponentMeta.f_component_name == "outs",
                                       PipelineComponentMeta.f_model_version == vid,
                                       PipelineComponentMeta.f_party_id == party_id),
                                      replace_on_conflict=True)

    new_cpn.save_define_meta_from_db_to_file()

