from fate_flow.web_server.pipeline_wrapper import  HomoNNWrapper
import copy

from fate_flow.web_server.pipeline_wrapper.test import prepare

BASE_PARAM = {
    "pid": 9999,
    "guest": 9999,
    "hosts": [10000],
    "arbiter":10000,
    "rol": "guest",
    "asyn": False,
}

HOST_TABLES = {
    "name": "breast_homo_host",
    "namespace": "experiment"
}

GUEST_TABLE = {
    "name": "breast_homo_guest",
    "namespace": "experiment"
}

GUEST_ONLY_PARAM = {
    "with_label": True,
    "output_format": "dense",
}

HOST_ONLY_PARAM = {
    "with_label": False,
}

NETWORK_PARAM = [
    [
        "Linear",
        {
            "out_features": 3,
            "in_features": 30
        }
    ],
    [
        "Linear",
        {
            "out_features": 1,
            "in_features": 3
        }
    ], [
        "Activation",
        {
            "activation": "ReLU"
        }
    ]
]


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

CV_PARAM = {
    "n_splits": 5,
    "shuffle": False,
    "random_seed": 103,
    "need_cv": False
}

CALLBACK_PARAM = {
    "callbacks": ["ModelCheckpoint"],
    "save_freq": "epoch"
}

HOMO_NN_PARAM = {
    "loss": "crossentropy",
    "epoch": 10,
    "batch_size": -1,
    "early_stop": "diff",
    "optimizer": "sgd",
    "optimizer_learning_rate": 0.001,
    "model": NETWORK_PARAM,
    "cv_param": CV_PARAM,
    "eval_param": EVA_PARAM,
    "split_param": SPLIT_PARAM,
    "callback_param": CALLBACK_PARAM,
}


def homo_nn(base_param, homo_nn_param=HOMO_NN_PARAM):
    job = HomoNNWrapper(**base_param)
    job.setReader()
    job.exe(homo_nn_param, asyn = False)


def test_homo_nn():
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = "202303021621559238000"#prepare.a_jobid(prepare.HOMO_GUEST_TABLES, prepare.HOMO_HOST_TABLES,host_only_param=prepare.GUEST_ONLY_PARAM, do_intersect=False)
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HomoNN'
    homo_nn(base_param)


if __name__ == "__main__":
    test_homo_nn()

