import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper
import copy

MODULE = "HeteroFeatureBinning"
BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}
COMMON_PARAM = {
    "optimal_binning_param": {
            "metric_method": "gini",
            "min_bin_pct": 0.05,
            "max_bin_pct": 0.8,
            "init_bucket_method": "quantile",
            "init_bin_nums": 100,
            "mixture": True
        },
        "compress_thres": 10000,
        "head_size": 10000,
        "error": 0.001,
        "bin_num": 10,
        "bin_indexes": -1,
        "bin_names": None,
        "category_indexes": [0, 1, 2],
        "category_names": None,
        "adjustment_factor": 0.5,
        "local_only": False,
        "transform_param": {
            "transform_cols": -1,
            "transform_names": None,
            "transform_type": "bin_num"
        }
}

def base_quantile(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM)


def base_bucket(jobid):
    pass

def base_chimq(jobid):
    pass


if __name__ == "__main__":
    # jobid = "202210211952452647390"
    jobid = None
    jobid = prepare.a_jobid()
    base_quantile(jobid)
    base_bucket(jobid)
    base_chimq(jobid)
