import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper

MODULE="HomoXGBoost"

COMMON_PARAM={
"num_trees": 5,
        "max_depth": 3,
        "learning_rate": 0.3,
        "random_seed": 0,
        "threshold": 0.5,
        "n_iter_no_change": True,
        "tol": 1e-4,
        "subsample_feature_rate": 1.0,
        "bin_num": 32,
        "l1_coefficient": 0.1,
        "l2_coefficient": 0.0,
        "min_sample_split": 2,
        "min_impurity_split": 1e-3,
        "min_leaf_node": 1,
        "max_split_nodes": 65535,
        "fast_mode": False,
        "run_goss": False,
        "top_rate": 0.2,
        "other_rate": 0.1,
        "cv_param": {
            "n_splits": 4,
            "shuffle": True,
            "random_seed": 33,
            "need_cv": False
        }
}

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="scale_0")

SPLIT_PARAM = {
    "stratified":True,
    "test_size":0.2,
    "train_size":0.6,
    "validate_size":0.2,
    "split_points":[0.4,0.8]
}

def split(jobid):
    global COMMON_PARAM,SPLIT_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=SPLIT_PARAM,cpn="scale_0")

EVAL_PARAM={
    "eval_type":"multi"
}
def split_and_eval(jobid):
    global COMMON_PARAM,EVAL_PARAM,SPLIT_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=SPLIT_PARAM,eva_param=EVAL_PARAM,cpn="scale_0")

def eval(jobid):
    global COMMON_PARAM,EVAL_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,eva_param=EVAL_PARAM,cpn="scale_0")

def cv(jobid):
    global COMMON_PARAM
    COMMON_PARAM["cv_param"]={
            "n_splits": 4,
            "shuffle": True,
            "random_seed": 33,
            "need_cv": True
        }
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="scale_0")

if __name__=="__main__":
    jobid = "202210141622337306860"
    jobid = prepare.a_jobid()
    base(jobid)
    split(jobid)
    split_and_eval(jobid)
    eval(jobid)
    cv(jobid)