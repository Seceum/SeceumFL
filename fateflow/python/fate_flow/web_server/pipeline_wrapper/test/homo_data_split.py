import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper
import copy

MODULE="HomoDataSplit"
COMMON_PARAM = {
    "stratified":True, "test_size":0.3, "validate_size":0.2
}
BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}

def base(jobid):
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,ml=False)


if __name__ == "__main__":
    jobid="202210271608447756940"
    jobid = prepare.a_jobid()
    base(None)