import sys, copy
sys.path.append("./")
from fate_flow.web_server.pipeline_wrapper.test import prepare
from fate_flow.web_server.pipeline_wrapper import wrapper

MODULE = "FeatureOutlier"
COMMON_PARAM_ALL_COLUMN = {
    "default_value":[42,50],
    "outlier_fill_method":"max",
    "missing_impute":None,
    "outlier_by_std":1.2,
    "outlier_by_quantile":0.45
}
COMMON_PARAM_PART_COLUMN = {
    "default_value":[42,50],
     "missing_impute":{"doctorco":[1,2],"hscore":[1],"chcond1":[1]},
     "outlier_by_std":None,
    "outlier_by_quantile":None
}
BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest",
    "asyn":True
}

def baseallcolumn(jobid):
    global COMMON_PARAM_ALL_COLUMN
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM_ALL_COLUMN,cpn="intersection_0",ml=False)

def designatedpartcolumn(jobid):
    global COMMON_PARAM_PART_COLUMN
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM_PART_COLUMN,cpn="intersection_0",ml=False)

COMMON_PARAM1 = {
    "default_value":[42,50],
    "missing_impute":None,
    "outlier_by_std":1.75,
    "outlier_by_quantile":None
}
GUEST_ONLY_PARAM = {
    "doctorco": "max",
    "hscore": "designated",
    "chcond1":"median"
}
def base_std(jobid):
    global COMMON_PARAM1,GUEST_ONLY_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM1,guest_only_param=GUEST_ONLY_PARAM,cpn="intersection_0",ml=False)

COMMON_PARAM2 = {
    "default_value":[42,50],
     "missing_impute":None,
    "outlier_by_std":None,
    "outlier_by_quantile":2.45
}
def base_quantile(jobid):
    global COMMON_PARAM2,GUEST_ONLY_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM2,guest_only_param=GUEST_ONLY_PARAM,cpn="intersection_0",ml=False)

COMMON_PARAM3 = {
    "default_value":[42,50],
    "missing_impute":None,
    "outlier_by_std":1.2,
    "outlier_by_quantile":0.45
}
def base_std_quantile(jobid):
    global COMMON_PARAM3,GUEST_ONLY_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM3,guest_only_param=GUEST_ONLY_PARAM,cpn="intersection_0",ml=False)

if __name__ == "__main__":
    jobid = "202211171114515043340"
    baseallcolumn(jobid)
    # jobid = "202211161436193678670"
    # designatedpartcolumn(jobid)
    # jobid = "202211161452561621470"
    # base_std(jobid)
    # jobid ="202211161501267965580"
    # base_quantile(jobid)
    # jobid = "202211161507168610240"
    # base_std_quantile(jobid)