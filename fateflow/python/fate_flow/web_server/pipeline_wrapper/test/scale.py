import sys
from fate_flow.web_server.pipeline_wrapper.test import prepare
sys.path.append("./")
import wrapper

MODULE="FeatureScale"
COMMON_PARAM = {
    "method":"standard_scale",
    "mode":"normal",
    "scale_names":["x1","x4"]

}

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,pid=9999,cpn="intersection_0",ml=False)

if __name__ == "__main__":
    jobid = "202210181325484358530"
    jobid = prepare.a_jobid()
    base(jobid)