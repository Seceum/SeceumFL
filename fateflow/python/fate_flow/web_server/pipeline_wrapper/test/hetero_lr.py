import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper

COMMON_PARAM  = {
    "penalty": "L2",
    "optimizer": "rmsprop",
    "tol": 0.0001,
    "alpha": 0.01,
    "max_iter": 30,
    "early_stop": "diff",
    "batch_size": 320,
    "batch_strategy": "random",
    "learning_rate": 0.15,
    "early_stopping_rounds": None,
    "init_param": {
        "init_method": "zeros"
    },
    "sqn_param": {
        "update_interval_L": 3,
        "memory_M": 5,
        "sample_size": 5000,
        "random_seed": None
    },
    "cv_param": {
        "n_splits": 5,
        "shuffle": False,
        "random_seed": 103,
        "need_cv": False
    },
    "callback_param": {
        "callbacks": ["ModelCheckpoint"],
        "save_freq": 1
    }
}
EVA_PARAM = {
        "eval_type": "binary", 
        "pos_label": 1
}
SPLIT_PARAM = {
        "stratified":True,
        "test_size": 0.3,
        "validate_size": 0.2,
        "split_points": [0.0, 0.2]
}
SB_PARAM = {
    "method": "credit",
    "offset": 500,
    "factor": 20,
    "factor_base": 2,
    "upper_limit_ratio": 3,
    "lower_limit_value": 0
}

MODULE = "HeteroLR"

def base(jid):
    global COMMON_PARAM, EVA_PARAM
    print(f"Base ................................. {jid}")
    wrapper.t_(jid,  MODULE, common_param = COMMON_PARAM, ml=True)

def eva(jid):
    global COMMON_PARAM, EVA_PARAM
    print(f"eva ................................. {jid}")
    wrapper.t_(jid,  MODULE,
            common_param = COMMON_PARAM,
            eva_param = EVA_PARAM)

def cv(jid):
    global COMMON_PARAM, EVA_PARAM
    print(f"CV ................................. {jid}")
    COMMON_PARAM["cv_param"]= {
            "n_splits": 3,
            "shuffle": False,
            "random_seed": 42,
            "need_cv": True
        }
    wrapper.t_(jid,  MODULE,
            common_param = COMMON_PARAM,
            scr_param = SB_PARAM)

def split(jid):
    global COMMON_PARAM, SPLIT_PARAM
    print(f"split ................................. {jid}")
    wrapper.t_(jid,  MODULE,
            common_param = COMMON_PARAM, 
            split_param = SPLIT_PARAM,
            local_baseline=True)

def splitAndeva(jid):
    global COMMON_PARAM, EVA_PARAM, SPLIT_PARAM
    print(f"splitAndeva ................................. {jid}")
    COMMON_PARAM["cv_param"]["need_cv"] = False
    wrapper.t_(jid,  MODULE,
            common_param = COMMON_PARAM, 
            split_param = SPLIT_PARAM,
            eva_param = EVA_PARAM,
            local_baseline=True)


if __name__  ==  "__main__":
    #jid = prepare.a_jobid()
    jid = "202210261309334053120"
    base(jid)
    sys.exit()

    split(jid)
    splitAndeva(jid)
    eva(jid)
    cv(jid)

