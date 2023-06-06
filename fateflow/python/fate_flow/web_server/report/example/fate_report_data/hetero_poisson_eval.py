
job_id = "202204171100219807210"
component_name = "hetero_poisson_0"
guest_id = 9999

metrics = {}

metric_all = {}

output_model = {
    "data": {
        "bestIteration": -1,
        "header": [
            "hscore",
            "chcond1",
            "chcond2"
        ],
        "intercept": -0.17983558061155347,
        "isConverged": False,
        "iters": 10,
        "lossHistory": [],
        "weight": {
            "chcond1": -0.01388898737795123,
            "chcond2": -0.011969492527438636,
            "hscore": -0.014292688133836983
        }
    },
    "meta": {
        "meta_data": {
            "alpha": 100.0,
            "batchSize": "-1",
            "earlyStop": "weight_diff",
            "exposureColname": "exposure",
            "fitIntercept": True,
            "learningRate": 0.01,
            "maxIter": "10",
            "optimizer": "rmsprop",
            "penalty": "L2",
            "tol": 0.001
        },
        "module_name": "HeteroPoisson"
    },
    "retcode": 0,
    "retmsg": "success"
}
