import sys
sys.path.append("./")
from fate_flow.web_server.pipeline_wrapper import wrapper
from fate_flow.web_server.pipeline_wrapper.test import prepare


MODULE = "HeteroKmeans"
COMMON_PARAM = {
        "k": 2,
        "max_iter": 10,
    "random_stat": 1000
}

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM)

if __name__ == "__main__":
    jid = prepare.a_jobid()
    #jid = "202210171725197522750"
    base(jid)