import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper

MODULE = "FederatedSample"
COMMON_PARAM = {
    "mode":"stratified", "method":"upsample","fractions":[[0, 1.5], [1, 2.0]]
}

BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}

def base(newjobid):
    wrapper.t_(newjobid,MODULE,common_param=COMMON_PARAM,cpn="outs",ml=False)


if __name__ == "__main__":
    jobid = "202210271728070569680"

    jobid = prepare.a_jobid()
    base(None)