
import typing

from fate_flow.entity.run_status import TaskStatus
from fate_flow.web_server.db_service.sample_service import SampleFieldsService, VSampleInfoService


def get_error_message(traceback: str) -> str:
    """
    从Traceback信息中提取简要的报错信息

    This function is really foolish, don't ask why
    Just read the return message from job/submit in FATE
    """
    msg = ''
    lines = traceback.split('\\n')
    if not lines:
        return ''
    for line in reversed(lines):
        if line.startswith('ValueError') or \
           line.startswith('Error') or \
           line.startswith('Exception'):
            msg = line
            break
    return msg


def get_block_status(component_status: typing.List[str]) -> str:
    """
    根据内部Component的执行状态，判断Block的执行状态
    """
    if not component_status:
        return TaskStatus.PASS
    for status in component_status:
        if status != TaskStatus.SUCCESS and \
           status != TaskStatus.PASS:
            return status
    # 仅当内部组件全部为success或pass状态，才判定Block执行成功
    return TaskStatus.SUCCESS


def get_sample_label(sample_ids: typing.List[str]) -> dict:
    labels = {}
    for sample_id in sample_ids:
        # TODO: "Y" better defined somewhere
        label_objs = SampleFieldsService.query(sample_id=sample_id, data_type="Y")
        if label_objs:
            label_obj = label_objs[0]  # a sample only has one label field
            label_info = {
                "label_name": label_obj.field_name,
                "label_type": label_obj.field_type
            }
        else:
            label_info = {}
        labels[sample_id] = label_info
    return labels


def get_fusion_info(fusion_ids: typing.List[str]) -> (dict, list):
    fusion_info = {}
    party_infos = []
    for fusion_id in fusion_ids:
        sample_obj = VSampleInfoService.get(id=fusion_id)
        fusion_info[fusion_id] = {
            "job_id": sample_obj.job_id,
            "component_name": sample_obj.component_name,
        }
        party_infos.append(sample_obj.party_info)
    return fusion_info, party_infos
