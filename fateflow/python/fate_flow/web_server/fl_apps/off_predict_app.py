import os
import peewee
from flask import request, send_file, after_this_request
from flask_login import login_required
from fate_arch.session import Session
from fate_arch.common.base_utils import fate_uuid
from fate_flow.component_env_utils import feature_utils
from fate_flow.component_env_utils.env_utils import import_component_output_depend
from fate_flow.manager.data_manager import get_component_output_data_schema
from fate_flow.operation.job_saver import JobSaver
from fate_flow.web_server.blocks import BlockParser
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.db_service.job_service import JobContentService
from fate_flow.web_server.utils.enums import RoleTypeEnum
from fate_flow.web_server.utils.off_predict_util import get_component_output_tables_meta
from fate_flow.web_server.utils.reponse_util import get_json_result
from fate_flow.utils.detect_utils import validate_request


@manager.route('/data_download', methods=['POST'])
@login_required
@validate_request("job_id", "component_name")
def data_download():
    """数据下载"""
    request_data = request.json
    request_data["role"] = RoleTypeEnum.GUEST.value
    request_data["party_id"] = config.local_party_id
    job_id = request_data['job_id']
    component_name = request_data['component_name']
    try:
        content_obj = JobContentService.get(job_id=job_id)
    except peewee.DoesNotExist:
        return get_json_result(data=False, retmsg=f"job_id {job_id} not found", retcode=100)
    parser = BlockParser()
    parser.load(content_obj.run_param)
    block = parser.blocks.get(component_name)
    if not block:
        return get_json_result(data=False, retcode=100, retmsg=f'组件 {component_name} 不存在')
    fate_cpt_name = block.output_component
    tasks = JobSaver.query_task(only_latest=True, job_id=request_data['job_id'], component_name=fate_cpt_name,
                                role=request_data['role'], party_id=request_data['party_id'])
    request_data['component_name'] = fate_cpt_name
    if not tasks:
        return get_json_result(data=False, retmsg="no found task, please check if the parameters are correct",
                               retcode=100)
    import_component_output_depend(tasks[0].f_provider_info)
    try:
        output_tables_meta = get_component_output_tables_meta(task_data=request_data)
    except Exception as e:
        return get_json_result(data=False, retmsg=str(e), retcode=100)
    if not output_tables_meta:
        return get_json_result(data=False, retmsg='no data', retcode=100)
    for output_name, output_table_meta in output_tables_meta.items():
        output_data_count = 0
        is_str = False
        output_data_file_path = "{}/{}.csv".format(os.getcwd(), fate_uuid())
        os.makedirs(os.path.dirname(output_data_file_path), exist_ok=True)
        with open(output_data_file_path, 'w') as fw:
            with Session() as sess:
                output_table = sess.get_table(name=output_table_meta.get_name(),
                                              namespace=output_table_meta.get_namespace())
                if output_table:
                    for k, v in output_table.collect():
                        data_line, is_str, extend_header = feature_utils.get_component_output_data_line(src_key=k,
                                                                                                        src_value=v)
                        # fw.write('{}\n'.format(','.join(map(lambda x: str(x).replace(",",""), data_line))))
                        fw.write('{}\n'.format(
                            ','.join(map(lambda x: "\"" + str(x) + "\"" if "," in str(x) else str(x), data_line))))
                        output_data_count += 1
        if output_data_count:
            header = get_component_output_data_schema(output_table_meta=output_table_meta,
                                                      is_str=is_str,
                                                      extend_header=extend_header)
            if header:
                with open(output_data_file_path, 'r+') as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write('{}\n'.format(','.join(header)) + content)
        @after_this_request
        def remove_file(response):
            try:
                os.remove(output_data_file_path)
            except Exception:
                pass
            return response

        return send_file(output_data_file_path, mimetype="text/csv", attachment_filename="data.csv", as_attachment=True)
