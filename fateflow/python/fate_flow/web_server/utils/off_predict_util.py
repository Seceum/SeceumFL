from fate_flow.db.db_models import DB, Job
from fate_flow.operation.job_tracker import Tracker


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
def get_component_output_tables_meta(task_data):
    check_request_parameters(task_data)
    tracker = Tracker(job_id=task_data['job_id'], component_name=task_data['component_name'],
                      role=task_data['role'], party_id=task_data['party_id'])
    output_data_table_infos = tracker.get_output_data_info()
    output_tables_meta = tracker.get_output_data_table(output_data_infos=output_data_table_infos)
    return output_tables_meta