
job_id = "202204112157147688640"
component_name = "hetero_linr_0"
guest_id = 9999

metrics = {}

metric_all = {}

output_model = {
    "data": {
        "bestIteration": -1,
        "header": [
            "pm",
            "stator_yoke",
            "stator_tooth",
            "stator_winding"
        ],
        "intercept": 0.012795519335644018,
        "isConverged": False,
        "iters": 20,
        "lossHistory": [],
        "weight": {
            "pm": 0.11813467875257995,
            "stator_tooth": 0.01925550354502433,
            "stator_winding": 0.024290567441345366,
            "stator_yoke": -0.04423512434450521
        }
    },
    "meta": {
        "meta_data": {
            "alpha": 0.01,
            "batchSize": "-1",
            "earlyStop": "weight_diff",
            "fitIntercept": True,
            "learningRate": 0.15,
            "maxIter": "20",
            "optimizer": "sgd",
            "penalty": "L2",
            "tol": 0.001
        },
        "module_name": "HeteroLinR"
    },
    "retcode": 0,
    "retmsg": "success"
}
