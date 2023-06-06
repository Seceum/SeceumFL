import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper

MODULE = "HomoLR"
COMMON_PARAM={
"penalty": "L2",
        "optimizer": "sgd",
        "tol": 1e-05,
        "alpha": 0.01,
        "max_iter": 30,
        "early_stop": "diff",
        "batch_size": -1,
        "learning_rate": 0.15,
        "decay": 1,
        "decay_sqrt": True,
        "init_param": {
            "init_method": "zeros"
        },
        "encrypt_param": {
            "method": None
        },
        "cv_param": {
            "n_splits": 4,
            "shuffle": True,
            "random_seed": 33,
            "need_cv": False
        }
}
SPLIT_PARAM = {
    "stratified":True,
    "test_size":0.2,
    "train_size":0.7,
    "validate_size":0.1,
    "split_points":[0,0.4]
}
EVAL_PARAM = {
    "eval_type":"binary",
    "pos_label":1
}
def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="scale_0")


def split(jobid):
    global COMMON_PARAM,SPLIT_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=SPLIT_PARAM,cpn="scale_0")

def split_and_eva(jobid):
    global COMMON_PARAM,SPLIT_PARAM,EVAL_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=SPLIT_PARAM,cpn="scale_0")

def eval(jobid):
    global COMMON_PARAM,EVAL_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,eva_param=EVAL_PARAM,cpn="scale_0")

def cv(jobid):
    global COMMON_PARAM
    COMMON_PARAM["cv_param"]={ "n_splits": 4,
            "shuffle": True,
            "random_seed": 33,
            "need_cv": True}
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="scale_0")

if __name__== "__main__":
    jobid = "202210141622337306860"
    jobid = prepare.a_jobid()
    base(jobid)
    split(jobid)
    split_and_eva(jobid)
    eval(jobid)
    cv(jobid)