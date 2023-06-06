import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper
import copy

MODULE="HomoFeatureBinning"
COMMON_PARAM = {
    "sample_bins":1000
}
BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}

def base(newjobid):
    wrapper.t_(newjobid,MODULE,common_param=COMMON_PARAM,ml=False,cpn="outs")


if __name__ == "__main__":
    jobid = "202210271703369346090"
    jobid = prepare.a_jobid()
    base(None)