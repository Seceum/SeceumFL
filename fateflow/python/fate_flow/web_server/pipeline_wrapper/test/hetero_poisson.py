import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper

MODULE="HeteroPoisson"
COMMON_PARAM={
    "early_stop":"weight_diff",
    "max_iter":10,
    "alpha":100.0,
    "batch_size":-1,
    "learning_rate":0.01,
    "optimizer":"rmsprop",
    "exposure_colname":"exposure",
    "decay_sqrt":False,
    "tol":0.001,
    "init_param":{"init_method": "zeros"},
    "penalty":"L2",
    "cv_param": {
        "n_splits": 5,
        "shuffle": False,
        "random_seed": 103,
        "need_cv": False
    }
}

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="intersection_0")

SPLIT_PARAM={
    "stratified":True,
    'test_size':0.2,
    "train_size":0.6,
    "validate_size":0.2,
    "split_points":[0.4,0.8]
}
def split(jobid):
    global COMMON_PARAM,SPLIT_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=SPLIT_PARAM,cpn="intersection_0")

EVAL_PARAM={
    "eval_type":"regression"
}
def eval(jobid):
    global COMMON_PARAM,EVAL_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,eva_param=EVAL_PARAM,cpn="intersection_0")

def split_and_eval(jobid):
    global COMMON_PARAM,SPLIT_PARAM,EVAL_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=SPLIT_PARAM,eva_param=EVAL_PARAM,cpn="intersection_0")

def cv(jobid):
    global COMMON_PARAM
    # COMMON_PARAM["cv_param"] = {"n_splits": 4,
    #     "shuffle": False,
    #     "random_seed": 103,
    #     "need_cv": True}
    COMMON_PARAM["cv_param"] = {
        "n_splits": 5,
        "shuffle": False,
        "random_seed": 103,
        "need_cv": True
    }
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="intersection_0")

if __name__ == "__main__":
    jid = prepare.a_jobid()
    jobid = "202210171513015139170"
    base(jobid)
    # split(jobid)
    # eval(jobid)
    # split_and_eval(jobid)
    # cv(jobid)