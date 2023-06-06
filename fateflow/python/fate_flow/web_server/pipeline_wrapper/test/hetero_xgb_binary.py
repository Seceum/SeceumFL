import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
from fate_flow.web_server.pipeline_wrapper import wrapper

COMMON_PARAM = {
    "num_trees": 3,
    "task_type": 'classification',
    "objective_param": {"objective": "cross_entropy"},
    "tree_param": {
        "max_depth": 3
    },
    "validation_freqs": 1,
    "cv_param": {
        "n_splits": 4,
        "shuffle": True,
        "random_seed": 33,
        "need_cv": True
    }
}

SPLIT_PARAM = {
    "stratified":True,
    "test_size":0.2,
    "train_size":0.6,
    "validate_size":0.2,
    "split_points":[0.4,0.8]
}
EVAL_PARAM = {
    "eval_type":"binary",
    "pos_label":1
}
MODULE="HeteroXGBoost"

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,ml=True)

def split(jobid):
    global COMMON_PARAM,SPLIT_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=SPLIT_PARAM,cpn="scale_0")

def split_and_eval(jobid):
    global COMMON_PARAM,SPLIT_PARAM,EVAL_PARAM
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
    jobid="202211041621455153600"
    jobid = prepare.a_jobid()
    base(jobid)
    #split(jobid)
    #split_and_eval(jobid)
    #eval(jobid)
    #cv(jobid)
    #cv(jobid)