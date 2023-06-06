from fate_flow.web_server.pipeline_wrapper import HeteroNNWrapper
import copy

from fate_flow.web_server.pipeline_wrapper.test import prepare

BASE_PARAM = {
    "pid": 9999,
    "guest": 9999,
    "hosts": [10000],
    "arbiter": 10000,
    "role": "guest"
}

HOST_TABLES = {
    "name": "breast_hetero_host",
    "namespace": "experiment"
}

GUEST_TABLE = {
    "name": "breast_hetero_guest",
    "namespace": "experiment"
}

GUEST_ONLY_PARAM = {
    "with_label": True,
    "output_format": "dense",
}

HOST_ONLY_PARAM = {
    "with_label": False,
}

BOTTOM_MODEL_PARAM = [
    [
        "Linear",
        {
            "out_features": 32,
            "in_features": 9
        }
    ],[
        "Activation",
        {
            "activation": "ReLU"
        }
    ]
]

TOP_MODEL_PARAM = [
    [
        "Linear",
        {
            "out_features": 1,
            "in_features": 16,
        }
    ],[
        "Activation",
        {
            "activation": "Sigmoid"
        }
    ]
]

INTERACTIVE_MODEL_PARAM = {
    "out_dim": 16,
    "guest_dim":32,
    "host_dim":32,
}


HETERO_NN_PARAM = {
    "task_type": "classification",
    "guest_bottom_nn": BOTTOM_MODEL_PARAM,
    "top_nn": TOP_MODEL_PARAM,
    "interactive_layer_param": INTERACTIVE_MODEL_PARAM,
    "interactive_layer_lr": 0.9,
    "optimizer_learning_rate": 0.01,
    "optimizer": "sgd",
    "epochs": 100,
    "batch_size": -1,
    "early_stop": "diff",
    "loss":"CrossEntropy",
}


def hetero_nn(base_param, hetero_nn_param=HETERO_NN_PARAM):

    job = HeteroNNWrapper(**base_param)
    job.setReader()
    return job.exe(hetero_nn_param, host_only_param={"10000": BOTTOM_MODEL_PARAM}, asyn=False)


def test_hetero_nn():
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = "202303011432284880960"#prepare.a_jobid()
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroNN'
    hetero_nn(base_param)


if __name__ == "__main__":
    test_hetero_nn()
