
job_id = "202204112137352850520"
component_name = "hetero_lr_0"
guest_id = 9999

metrics = {}

metric_all = {}

output_model = {
    "data": {
        "bestIteration": -1,
        "encryptedWeight": {},
        "header": [
            "x0",
            "x1",
            "x2",
            "x3",
            "x4",
            "x5",
            "x6",
            "x7",
            "x8",
            "x9"
        ],
        "intercept": 0.5328324770911446,
        "isConverged": False,
        "iters": 30,
        "lossHistory": [],
        "needOneVsRest": False,
        "weight": {
            "x0": -0.06665431494101953,
            "x1": -0.03380440405113404,
            "x2": -0.05780699227549247,
            "x3": -0.026000367549279455,
            "x4": -0.10813401278922008,
            "x5": -0.06740120373007578,
            "x6": -0.057226481731558344,
            "x7": -0.11286573780563365,
            "x8": -0.5059447077729528,
            "x9": -0.32521626797963504
        }
    },
    "meta": {
        "meta_data": {
            "alpha": 0.01,
            "batchSize": "320",
            "earlyStop": "diff",
            "fitIntercept": True,
            "learningRate": 0.15,
            "maxIter": "30",
            "needOneVsRest": False,
            "optimizer": "rmsprop",
            "partyWeight": 0.0,
            "penalty": "L2",
            "reEncryptBatches": "0",
            "revealStrategy": "",
            "tol": 0.0001
        },
        "module_name": "HeteroLR"
    },
    "retcode": 0,
    "retmsg": "success"
}
