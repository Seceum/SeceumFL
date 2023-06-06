import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper

COMMON_PARAM  = {
    "penalty": "L2",
    "optimizer": "sgd",
    "tol": 0.001,
    "alpha": 0.01,
    "max_iter": 20,
    "early_stop": "weight_diff",
    "batch_size": -1,
    "learning_rate": 0.15,
    "decay": 0.0,
    "decay_sqrt": False,
    "init_param": {"init_method": "zeros"},
    "floating_point_precision": 23
}

EVA_PARAM = {
        "eval_type": "regression", 
        "pos_label": 1
}
SPLIT_PARAM = {
        "stratified":True,
        "test_size": 0.3,
        "validate_size": 0.2,
        "split_points": [0.0, 0.2]
}


def base(jid):
    global COMMON_PARAM, EVA_PARAM
    wrapper.t_(jid,  "HeteroLinR", common_param = COMMON_PARAM)

def eva(jid):
    global COMMON_PARAM, EVA_PARAM
    wrapper.t_(jid,  "HeteroLinR",
            common_param = COMMON_PARAM,
            eva_param = EVA_PARAM)

def cv(jid):
    global COMMON_PARAM, EVA_PARAM
    COMMON_PARAM["cv_param"]= {
            "n_splits": 3,
            "shuffle": False,
            "random_seed": 42,
            "need_cv": True
        }
    wrapper.t_(jid,  "HeteroLinR",
            common_param = COMMON_PARAM,
            eva_param = EVA_PARAM)

def split(jid):
    global COMMON_PARAM, SPLIT_PARAM
    wrapper.t_(jid,  "HeteroLinR",
            common_param = COMMON_PARAM, 
            split_param = SPLIT_PARAM)

def splitAndeva(jid):
    global COMMON_PARAM, EVA_PARAM, SPLIT_PARAM
    COMMON_PARAM["cv_param"]["need_cv"] = False
    wrapper.t_(jid,  "HeteroLinR",
            common_param = COMMON_PARAM, 
            split_param = SPLIT_PARAM,
            eva_param = EVA_PARAM)



if __name__  ==  "__main__":
    jid = prepare.a_jobid()
    jid = "202210081643480179740"
    base(jid)
    eva(jid)
    split(jid)
    cv(jid)
    splitAndeva(jid)
