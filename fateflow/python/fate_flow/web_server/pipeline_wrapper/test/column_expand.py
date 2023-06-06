import sys
from fate_flow.web_server.pipeline_wrapper.test import prepare
sys.path.append("./")
import wrapper
import copy

MODULE = "ColumnExpand"

COMMON_PARAM = {
    "need_run":True,
    "method":"manual",
    "append_header":["x_0", "x_1", "x_2", "x_3"],
    "fill_value":[0, 0.2, 0.5, 1]
}
BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}

def base(newjobid):
    wrapper.t_(newjobid,MODULE,guest_only_param=COMMON_PARAM,host_only_param={"need_run":False},common_param={},cpn="reader",ml=False)


if __name__ == "__main__":
    jobid = "202210271753574659610"
    jobid = prepare.a_jobid()
    base(None)