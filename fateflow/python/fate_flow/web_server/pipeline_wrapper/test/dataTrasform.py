import sys, os
sys.path.append("./")
from pipeline.backend.pipeline import PipeLine
import wrapper

HOST_TABLES = {
    "name": "default_credit_hetero_host",
    "namespace": "experiment"
}

GUEST_TABLE = {
    "name": "default_credit_hetero_guest",
    "namespace": "experiment"
}

ROLE = "guest"
PID = 9999

def fromRaw():
    j = wrapper.DataTransformJob(pid=PID, guest=9999, role=ROLE, hosts=[10000])
    j.setReader(guest_table=GUEST_TABLE,
        host_tables={"10000":HOST_TABLES }
    )
    j.exe(guest_only_param = {
        "label_name": "y",
        "missing_fill": True,
        "missing_fill_method": "mean",
        "outlier_replace": True,
        "with_label":True
        },
        host_only_param={
        "with_label": False,
        "missing_fill": True,
        "missing_fill_method": "mean",
        "outlier_replace": True
        },
        asyn=False
    )

def afterUnion(jid):
    j = wrapper.DataTransformJob(pid=PID, guest=9999, role=ROLE, hosts=[10000])
    j.setReader(guest_table = {
        "job_id": jid,
        "component_name": "outs",
        "data_name":"data"
        },
        host_tables = {"10000":HOST_TABLES }
    )
    j.exe(guest_only_param = {
        "label_name": "y",
        "missing_fill": True,
        "missing_fill_method": "mean",
        "outlier_replace": True,
        "with_label":True
        },
        host_only_param={
        "with_label": False,
        "missing_fill": True,
        "missing_fill_method": "mean",
        "outlier_replace": True
        }, asyn = False
    )


if __name__  ==  "__main__":
    fromRaw()
    #afterUnion(jid = "202210081537167661060")
