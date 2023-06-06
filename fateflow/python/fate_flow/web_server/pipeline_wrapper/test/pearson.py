import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
from fate_flow.web_server.pipeline_wrapper import wrapper

COMMON_PARAM = {'column_indexes':-1}

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid, "HeteroPearson", cpn="intersection_0", common_param=COMMON_PARAM)

if __name__=="__main__":
    jobid="202210141609112785010"
    jobid = prepare.a_jobid()
    base(jobid)