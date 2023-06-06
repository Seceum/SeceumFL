import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper

MODULE = "DataStatistics"
COMMON_PARAM = {
        "statistics": ["95%", "coefficient_of_variance", "stddev"],
        "column_indexes": -1,
        "column_names": []
}
BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,ml=False)

if __name__ == "__main__":
    jobid = "202210201404092750800"
    jobid = prepare.a_jobid()
    base(jobid)