import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper
import copy

MODULE = "SampleWeight"
guest_only_param = {"need_run":True,
                    "sample_weight_name":"x0"}
host_only_param = {"need_run":False}

BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}

def base(newjobid):
    wrapper.t_(newjobid,MODULE,guest_only_param=guest_only_param,host_only_param=host_only_param,cpn="outs",ml=False)


if __name__ == "__main__":
    jobid = "202211021615588714960"
    jobid = prepare.a_jobid()
    base(None)