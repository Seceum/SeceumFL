import sys, os
sys.path.append("./")
from pipeline.backend.pipeline import PipeLine
import wrapper

GUEST_TABLE = {
    "name": "default_credit_hetero_guest",
    "namespace": "experiment"
}

HOST_TABLES = {
    "name": "default_credit_hetero_host",
    "namespace": "experiment"
}

ROLE = "guest"
PID = 9999

def upload():
    guest = {"name": "default_credit_hetero_guest", "namespace": "experiment"}
    host = {"name": "default_credit_hetero_host", "namespace": f"experiment"}

    pipeline_upload = PipeLine().set_initiator(role="guest", party_id=9999).set_roles(guest=9999)
    data_base = "/data/projects/AutoFL/"

    # add upload data info
    # path to csv file(s) to be uploaded
    pipeline_upload.add_upload_data(file=os.path.join(data_base,
        "examples/data/default_credit_hetero_guest.csv"),
                                    table_name=guest["name"],             # table name
                                    namespace=guest["namespace"],         # namespace
                                    head=1, partition=4,               # data info
                                    #extend_sid = True,
                                    id_delimiter=",",)

    pipeline_upload.add_upload_data(file=os.path.join(data_base,
        "examples/data/default_credit_hetero_host.csv"),
                                    table_name=host["name"],
                                    namespace=host["namespace"],
                                    head=1, partition=4,
                                    #extend_sid = True,
                                    id_delimiter=",")
    pipeline_upload.upload(drop=1)

def guest_union():
    j = wrapper.UnionWrapper(pid=PID, guest=9999, role=ROLE, asyn = False)
    j.exe([GUEST_TABLE, GUEST_TABLE] )

def host_union():
    ROLE = "host"
    PID = 10000
    j = wrapper.UnionWrapper(pid=PID, hosts=[10000], role=ROLE, asyn = False)
    j.exe([HOST_TABLES, HOST_TABLES])

if __name__  ==  "__main__":
    #upload()
    guest_union()
    #host_union()

