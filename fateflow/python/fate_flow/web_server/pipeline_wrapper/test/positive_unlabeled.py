import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
from fate_flow.web_server.pipeline_wrapper import wrapper, WrapperFactory

COMMON_PARAM = {"max_iter": 2}

def base(jobid):
    global COMMON_PARAM
    lr_jid = "202303011525028053390"
    lr_jid,_ = wrapper.t_(jobid, "HeteroLR", common_param=COMMON_PARAM)
    pip = WrapperFactory("positiveunlabeled")(**prepare.BASE_PARAM)
    pip.setReader([lr_jid, jobid], mdl_nms=["LR", "Intersection"])
    pip.exe({"strategy": "proportion", "threshold": 0.1}, asyn=False)


if __name__=="__main__":
    jobid="202303011336449424770"
    jobid="202303011432284880960"
    #jobid = prepare.a_jobid()
    base(jobid)