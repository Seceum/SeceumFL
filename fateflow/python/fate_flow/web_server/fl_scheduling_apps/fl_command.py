import threading

from flask_login import current_user

from fate_flow.scheduler.federated_scheduler import FederatedScheduler
from fate_flow.settings import ENGINES
from fate_flow.web_server.db.db_models import StudioModelInfoExtend
from fate_flow.web_server.db_service.party_service import PartyInfoService
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.enums import StatusEnum, RoleTypeEnum


class FL_Scheduler(FederatedScheduler):
    @classmethod
    def sample_command(cls, sample_id,command, command_body=None, parallel=False,dest_only_initiator=False,specific_dest=False):
        federated_response = {}
        dest_partis= []
        if dest_only_initiator:
            api_type = "initiator"
        elif specific_dest:
            party_infos = PartyInfoService.query(status=StatusEnum.VALID.value,ping_status="正常").dicts()
            if party_infos:
                dest_partis.append((RoleTypeEnum.HOST.value,[party_info["id"] for party_info in party_infos]))
            api_type = "sample_schedule"
        else:
            party_infos = PartyInfoService.query(status=StatusEnum.VALID.value,ping_status="正常").dicts()
            if party_infos:
                dest_partis.append((RoleTypeEnum.HOST.value,[party_info["id"] for party_info in party_infos]))
            dest_partis.append((RoleTypeEnum.GUEST.value,[ config.local_party_id]))
            api_type = "sample_schedule"
        if not dest_partis:
            return 0,{}
        threads = []
        for dest_role, dest_party_ids in dest_partis:
            federated_response[dest_role] = {}
            for dest_party_id in dest_party_ids:
                username = current_user.username if dest_role==RoleTypeEnum.GUEST.value else "{}-{}".format("out_party_id",  config.local_party_id)
                endpoint = f"/{api_type}/{sample_id}/{dest_role}/{config.local_party_id}/{command}/%s"%( username)
                # endpoint = f"/{api_type}/{job.f_job_id}/{dest_role}/{dest_party_id}/{command}"
                # job.f_job_id, job.f_role, job.f_party_id = command,guest,config.local_party_id
                args = (command,RoleTypeEnum.GUEST.value,config.local_party_id,dest_role,dest_party_id, endpoint, command_body, ENGINES["federated_mode"], federated_response)
                if parallel:
                    t = threading.Thread(target=cls.federated_command, args=args)
                    threads.append(t)
                    t.start()
                else:
                    cls.federated_command(*args)
        for thread in threads:
            thread.join()
        return cls.return_federated_response(federated_response=federated_response)

    @classmethod
    def model_manage_command(cls, model: StudioModelInfoExtend,command, command_body=None, parallel=False,dest_only_initiator=False,specific_dest=False,dest_partis=[]):
        federated_response = {}
        api_type = "model_manage_schedule"
        if not dest_partis:
            if specific_dest:
                party_infos = PartyInfoService.query(status=StatusEnum.VALID.value,ping_status="正常").dicts()
                if party_infos:
                    dest_partis.append((RoleTypeEnum.HOST.value,[party_info["id"] for party_info in party_infos]))
            else:
                party_infos = PartyInfoService.query(status=StatusEnum.VALID.value,ping_status="正常").dicts()
                if party_infos:
                    dest_partis.append((RoleTypeEnum.HOST.value,[party_info["id"] for party_info in party_infos]))
                dest_partis.append((RoleTypeEnum.GUEST.value,[ config.local_party_id]))
            if not dest_partis:
                return 0,{}
        threads = []
        for dest_role, dest_party_ids in dest_partis:
            federated_response[dest_role] = {}
            for dest_party_id in dest_party_ids:
                username = current_user.username if dest_role==RoleTypeEnum.GUEST.value else "{}-{}".format("out_party_id",  config.local_party_id)
                endpoint = f"/{api_type}/{dest_role}/{config.local_party_id}/{command}/%s"%( username)
                # endpoint = f"/{api_type}/{job.f_job_id}/{dest_role}/{dest_party_id}/{command}"
                # job.f_job_id, job.f_role, job.f_party_id = command,guest,config.local_party_id
                args = (command,RoleTypeEnum.GUEST.value,config.local_party_id,dest_role,dest_party_id, endpoint, command_body, ENGINES["federated_mode"], federated_response)
                if parallel:
                    t = threading.Thread(target=cls.federated_command, args=args)
                    threads.append(t)
                    t.start()
                else:
                    cls.federated_command(*args)
        for thread in threads:
            thread.join()
        return cls.return_federated_response(federated_response=federated_response)

    @classmethod
    def node_command(cls, command, command_body=None, parallel=False,dest_only_initiator=False,specific_dest=False,specific_para=None):
        federated_response = {}
        dest_partis= []
        if specific_dest:
            party_infos = PartyInfoService.query(status=StatusEnum.VALID.value,ping_status="正常").dicts()
            if party_infos:
                dest_partis.append((RoleTypeEnum.HOST.value,[party_info["id"] for party_info in party_infos]))
            api_type = "node_schedule"
        elif specific_para:#指定给哪个host发送命令
            dest_partis=specific_para #[(RoleTypeEnum.HOST.value,party_ids)]
            api_type = "node_schedule"
        else:
            party_infos = PartyInfoService.query(status=StatusEnum.VALID.value,ping_status="正常").dicts()
            if party_infos:
                dest_partis.append((RoleTypeEnum.HOST.value,[party_info["id"] for party_info in party_infos]))
            dest_partis.append((RoleTypeEnum.GUEST.value,[ config.local_party_id]))
            api_type = "node_schedule"
        threads = []
        if not dest_partis:
            return 0,{}
        for dest_role, dest_party_ids in dest_partis:
            federated_response[dest_role] = {}
            for dest_party_id in dest_party_ids:
                username = current_user.username if dest_role==RoleTypeEnum.GUEST.value else "{}-{}".format("out_party_id",  config.local_party_id)
                endpoint = f"/{api_type}/{dest_role}/{config.local_party_id}/{command}/%s"%( username)
                # endpoint = f"/{api_type}/{job.f_job_id}/{dest_role}/{dest_party_id}/{command}"
                # job.f_job_id, job.f_role, job.f_party_id = command,guest,config.local_party_id
                args = (command,RoleTypeEnum.GUEST.value,config.local_party_id,dest_role,dest_party_id, endpoint, command_body, ENGINES["federated_mode"], federated_response)
                if parallel:
                    t = threading.Thread(target=cls.federated_command, args=args)
                    threads.append(t)
                    t.start()
                else:
                    cls.federated_command(*args)
        for thread in threads:
            thread.join()
        return cls.return_federated_response(federated_response=federated_response)

    @classmethod
    def project_command(cls, command, command_body=None, parallel=False,dest_only_initiator=False,specific_dest=False,specific_para=None):
        federated_response = {}
        dest_partis= []
        if specific_dest:
            party_infos = PartyInfoService.query(status=StatusEnum.VALID.value,ping_status="正常").dicts()
            if party_infos:
                dest_partis.append((RoleTypeEnum.HOST.value,[party_info["id"] for party_info in party_infos]))
            api_type = "project_schedule"
        elif specific_para:#指定给哪个host发送命令
            dest_partis=specific_para #[(RoleTypeEnum.HOST.value,party_ids)]
            api_type = "project_schedule"
        else:
            party_infos = PartyInfoService.query(status=StatusEnum.VALID.value,ping_status="正常").dicts()
            if party_infos:
                dest_partis.append((RoleTypeEnum.HOST.value,[party_info["id"] for party_info in party_infos]))
            dest_partis.append((RoleTypeEnum.GUEST.value,[ config.local_party_id]))
            api_type = "project_schedule"
        threads = []
        if not dest_partis:
            return 0,{}
        for dest_role, dest_party_ids in dest_partis:
            federated_response[dest_role] = {}
            for dest_party_id in dest_party_ids:
                username = current_user.username if dest_role==RoleTypeEnum.GUEST.value else "{}-{}".format("out_party_id",  config.local_party_id)
                endpoint = f"/{api_type}/{dest_role}/{config.local_party_id}/{command}/%s"%( username)
                # endpoint = f"/{api_type}/{job.f_job_id}/{dest_role}/{dest_party_id}/{command}"
                # job.f_job_id, job.f_role, job.f_party_id = command,guest,config.local_party_id
                args = (command,RoleTypeEnum.GUEST.value,config.local_party_id,dest_role,dest_party_id, endpoint, command_body, ENGINES["federated_mode"], federated_response)
                if parallel:
                    t = threading.Thread(target=cls.federated_command, args=args)
                    threads.append(t)
                    t.start()
                else:
                    cls.federated_command(*args)
        for thread in threads:
            thread.join()
        return cls.return_federated_response(federated_response=federated_response)