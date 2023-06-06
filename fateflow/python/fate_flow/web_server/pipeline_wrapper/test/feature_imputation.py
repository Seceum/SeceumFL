import sys, copy
sys.path.append("./")
from fate_flow.web_server.pipeline_wrapper.test import prepare
from fate_flow.web_server.pipeline_wrapper import wrapper

MODULE = "FeatureImputation"
COMMON_PARAM = {
    "missing_fill_method":"designated",
    "default_value":42,
    "missing_impute":[0]
}

BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}

def feature_imputation(newjobid):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = newjobid
    base_param["cmp_nm"] = MODULE
    job = wrapper.WrapperBase(**base_param)
    job.setReader()
    guest_only_param = {"missing_fill_method":"min",
                        "col_missing_fill_method":{"x0":"min", "x1":"min", "x2":"min", "x3":"min", "x4":"min"},
                        "default_value":None,
                        "missing_impute":"-1, 0.222222"}
    host_only_param = None#guest_only_param
    newjobid2,_ = job.exe(guest_only_param=guest_only_param, host_only_param=host_only_param, asyn=False)
    print("feature imputation new jobid----",newjobid2)
    return newjobid2

def base_designated(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,ml=False)

COMMON_PARAM1 = {
    "missing_fill_method":"max",
    "missing_impute":[0]
}
def base_method(jobid):
    global COMMON_PARAM1
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM1,cpn="intersection_0",ml=False)

if __name__ == "__main__":
    #prepare.upload()
    #jid = prepare.a_jobid()
    feature_imputation("202212091233354301650")
    # base_method(jobid)