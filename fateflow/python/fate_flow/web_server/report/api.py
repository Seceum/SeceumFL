
import typing

import peewee

from fate_flow.web_server.fl_config import config
from fate_flow.utils.api_utils import get_json_result
from fate_flow.web_server.db_service.job_service import JobContentService
from fate_flow.web_server.blocks import BlockGroup, BlockParser
from fate_flow.web_server.report.component import get_component_content, get_ml_content
from fate_flow.web_server.report.dataset_info import SampleInfoContent, SampleInfoDetail
from fate_flow.web_server.report.report import ReportClient


def _get_job_content(job_id: str):
    try:
        content_obj = JobContentService.get(job_id=job_id)
    except peewee.DoesNotExist:
        content_obj = None
    return content_obj


def report_content(job_id: str, component_name: str):
    """
    查询组件的报告内容项
    # TODO: job_id -> job_content_id?
    """
    # 样本信息报告内容项（执行任务前查看）
    if not job_id:
        return get_json_result(data={'content': SampleInfoContent})
    # 1. 加载作业信息
    content_obj = _get_job_content(job_id)
    if not content_obj:
        return get_json_result(data=False, retcode=100, retmsg=f'job_id {job_id} 不存在')
    parser = BlockParser()
    # 2. 获取组件
    parser.load(content_obj.run_param)
    block = parser.blocks.get(component_name)
    if not block:
        return get_json_result(data=False, retcode=100, retmsg=f'组件 {component_name} 不存在')
    # 2. 生成报告内容项
    if BlockGroup.is_algorithm_block(block.module) or BlockGroup.is_evaluation_block(block.module):
        task_type = block.get_param('task_type')
        need_cv = block.get_param('need_cv')
        content = get_ml_content(block.module, task_type, need_cv)
    else:
        content = get_component_content(block.module)
    return get_json_result(data={'content': content})


def report_detail(job_id: str, component_name: str, contents: typing.List[str]):
    """
    获取组件的报告数据
    """
    # 样本信息报告数据（执行任务前查看）
    if not job_id:
        return get_json_result(data=SampleInfoDetail)
    # 1. 加载作业信息
    content_obj = _get_job_content(job_id)
    if not content_obj:
        return get_json_result(data=False, retcode=100, retmsg=f'job_id {job_id} 不存在')
    parser = BlockParser()
    parser.load(content_obj.run_param)
    # 2. 获取组件
    block = parser.blocks.get(component_name)
    if not block:
        return get_json_result(data=False, retcode=100, retmsg=f'组件 {component_name} 不存在')
    # TODO: above code is duplicated
    # 3. 获取参与方信息 TODO: it's a bad idea to get role and party_id by doing so
    # role = config.local_party_name
    role = 'guest'
    party_id = config.local_party_id
    # 4. 初始化报告类
    fate_cpt_name = block.output_component
    client = ReportClient(job_id, role, party_id, fate_cpt_name)
    # 5. 设置Block信息
    # TODO: add cv info to Reporter
    if BlockGroup.is_algorithm_block(block.module):
        task_type = block.get_param('task_type')
        need_cv = block.get_param('need_cv')
        n_split = 5 if need_cv else 0  # TODO: change 5 to constant
        client.set_block_info(module=block.module, is_algorithm=True,
                                task_type=task_type, need_cv=need_cv, n_split=n_split)
    elif BlockGroup.is_evaluation_block(block.module):
        task_type = block.get_param('task_type')
        client.set_block_info(module=block.module, is_evaluation=True,
                                task_type=task_type, need_cv=False)
    else:
        client.set_block_info(module=block.module)
    return get_json_result(data=client.get_report_data(contents))
