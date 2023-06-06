import copy, os
from pipeline.backend.pipeline import PipeLine
from fate_flow.web_server.pipeline_wrapper import wrapper

BASE_PARAM = {
    "pid": 9999,
    "guest": 9999,
    "hosts": [10000],
    "arbiter":10000,
    "role": "guest"
}

GUEST_ONLY_PARAM = {
    "with_label": True,
    "output_format": "dense",
    "label_name": "y"
}

HOST_ONLY_PARAM = {
    "with_label": False,
}

HOST_TABLES = {
    "name": "vehicle_scale_hetero_host",
    "namespace": "experiment"
}

GUEST_TABLE = {
    "name": "vehicle_scale_hetero_guest",
    "namespace": "experiment"
}

GUEST_TABLE = {
    "name": "breast_hetero_guest",
    "namespace": "experiment"
}
HOST_TABLES = {
    "name": "breast_hetero_host",
    "namespace": "experiment"
}

HOMO_HOST_TABLES = {
    "name":"breast_homo_host",
    "namespace": "experiment"
}

HOMO_GUEST_TABLES = {
    "name":"breast_homo_guest",
    "namespace":"experiment"
}

def upload(guest=GUEST_TABLE, host=HOST_TABLES):

    pipeline_upload = PipeLine().set_initiator(role="guest", party_id=9999).set_roles(guest=9999)
    data_base = "/data/projects/AutoFL/"

    # add upload data info
    # path to csv file(s) to be uploaded
    pipeline_upload.add_upload_data(file=os.path.join(data_base,
                                                      f"examples/data/{guest['name']}.csv"),
                                    table_name=guest["name"],  # table name
                                    namespace=guest["namespace"],  # namespace
                                    head=1, partition=4,  # data info
                                    # extend_sid = True,
                                    id_delimiter=",", )

    pipeline_upload.add_upload_data(file=os.path.join(data_base,
                                                      f"examples/data/{host['name']}.csv"),
                                    table_name=host["name"],
                                    namespace=host["namespace"],
                                    head=1, partition=4,
                                    # extend_sid = True,
                                    id_delimiter=",")
    pipeline_upload.upload(drop=1)

def read(gst_tab=GUEST_TABLE, host_tb=HOST_TABLES):
    param = copy.deepcopy(BASE_PARAM)
    param['cmp_nm'] = "Reader"
    job = wrapper.WrapperBase(**param)
    job.setReader(gst_tab = gst_tab,
        host_tb = {"10000": host_tb })
    jobid,_ = job.exe(asyn=False)
    print(jobid)
    return jobid


def data_transform(jobid, guest_only_param=GUEST_ONLY_PARAM, host_only_param=HOST_ONLY_PARAM):

    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'reader'
    base_param['cmp_nm'] = 'DataTransform'
    job = wrapper.WrapperBase(**base_param)
    job.setReader()
    new_job_id,_ = job.exe(guest_only_param=guest_only_param,host_only_param={h:host_only_param for h in base_param["hosts"]}, asyn=False)

    return new_job_id


def intersection(jobid):
    new_job_id, _ = wrapper.t_(jobid, cmp_nm="Intersection", cpn="outs",
                               common_param={
                                   "intersect_method": "dh",
                                   # "sync_intersect_ids": True,
                                   "only_output_key": False,
                                   "dh_params": {
                                       "hash_method": "sha256",
                                       "salt": "12345",
                                       "key_length": 1024
                                   },
                               }, ml=False,
                               )
    return new_job_id

def a_jobid(gst_tab=GUEST_TABLE, host_tb=HOST_TABLES,
            guest_only_param=GUEST_ONLY_PARAM, host_only_param=HOST_ONLY_PARAM,
            do_intersect=True):
    jobid = read(gst_tab,host_tb)
    jobid = data_transform(jobid, guest_only_param, host_only_param)
    if do_intersect: return intersection(jobid)
    return jobid

if __name__ == "__main__":
    upload(HOMO_GUEST_TABLES, HOMO_HOST_TABLES)