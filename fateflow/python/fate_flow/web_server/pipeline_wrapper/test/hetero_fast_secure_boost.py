import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper

MODULE ="HeteroFastSecureBoost"
COMMON_PARAM = {}

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="")

if __name__ == "__main__":
    jobid = ""
    jobid = prepare.a_jobid()
    base(jobid)