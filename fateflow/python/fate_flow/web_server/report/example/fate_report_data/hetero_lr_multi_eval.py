
job_id = "202204112141001840000"
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
            "x8"
        ],
        "intercept": 0.0,
        "isConverged": False,
        "iters": 0,
        "lossHistory": [],
        "needOneVsRest": True,
        "oneVsRestResult": {
            "completedModels": [
                {
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
                        "x8"
                    ],
                    "intercept": -0.3958779237583844,
                    "isConverged": False,
                    "iters": 10,
                    "lossHistory": [],
                    "weight": {
                        "x0": 0.03474512869904987,
                        "x1": 0.07667414383629609,
                        "x2": 0.038042420060303575,
                        "x3": 0.21460706980372052,
                        "x4": 0.23719525212489495,
                        "x5": 0.29339239247197024,
                        "x6": 0.18393912608384666,
                        "x7": -0.023683480939347013,
                        "x8": 0.23662780624286156
                    }
                },
                {
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
                        "x8"
                    ],
                    "intercept": -0.38262901974658603,
                    "isConverged": False,
                    "iters": 10,
                    "lossHistory": [],
                    "weight": {
                        "x0": 0.1349241889669438,
                        "x1": 0.005720503431957243,
                        "x2": 0.038404971457761526,
                        "x3": 0.21788732284025905,
                        "x4": 0.23403367082969734,
                        "x5": 0.2820338315151138,
                        "x6": 0.15856053619263752,
                        "x7": -0.01081188745083718,
                        "x8": 0.2181485312692471
                    }
                },
                {
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
                        "x8"
                    ],
                    "intercept": -0.4191712485800189,
                    "isConverged": False,
                    "iters": 10,
                    "lossHistory": [],
                    "weight": {
                        "x0": -0.07133503095257857,
                        "x1": 0.011690684448698791,
                        "x2": -0.2530913435035573,
                        "x3": 0.13426987155972026,
                        "x4": 0.3147219478439074,
                        "x5": 0.24599329010145887,
                        "x6": 0.08508115873131439,
                        "x7": 0.05031533122209208,
                        "x8": 0.12903072587871856
                    }
                },
                {
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
                        "x8"
                    ],
                    "intercept": -0.5218171499035302,
                    "isConverged": False,
                    "iters": 10,
                    "lossHistory": [],
                    "weight": {
                        "x0": -0.05125641233753688,
                        "x1": -0.12096613049194282,
                        "x2": -0.28181148645522747,
                        "x3": 0.0599350363655886,
                        "x4": 0.33899196281445015,
                        "x5": 0.42762791953682383,
                        "x6": -0.1628718162874629,
                        "x7": 0.41321986872827327,
                        "x8": -0.06619528385671572
                    }
                }
            ],
            "oneVsRestClasses": [
                "0",
                "1",
                "2",
                "3"
            ]
        },
        "weight": {}
    },
    "meta": {
        "meta_data": {
            "alpha": 0.0001,
            "batchSize": "-1",
            "earlyStop": "diff",
            "fitIntercept": True,
            "learningRate": 0.15,
            "maxIter": "10",
            "needOneVsRest": True,
            "optimizer": "nesterov_momentum_sgd",
            "partyWeight": 0.0,
            "penalty": "L2",
            "reEncryptBatches": "0",
            "revealStrategy": "",
            "tol": 1e-05
        },
        "module_name": "HeteroLR"
    },
    "retcode": 0,
    "retmsg": "success"
}
