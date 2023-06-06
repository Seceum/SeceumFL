
job_id = "202204131006392385640"
component_name = "hetero_lr_0"
guest_id = 9999

metrics = {
    "data": {
        "train": [
            "train_fold_0",
            "train_fold_0_precision",
            "train_fold_0_recall",
            "train_fold_1",
            "train_fold_1_precision",
            "train_fold_1_recall",
            "train_fold_2",
            "train_fold_2_precision",
            "train_fold_2_recall"
        ],
        "validate": [
            "validate_fold_0",
            "validate_fold_0_precision",
            "validate_fold_0_recall",
            "validate_fold_1",
            "validate_fold_1_precision",
            "validate_fold_1_recall",
            "validate_fold_2",
            "validate_fold_2_precision",
            "validate_fold_2_recall"
        ]
    },
    "retcode": 0,
    "retmsg": "success"
}

# 仅保留fold_0相关数据
metric_all = {
    "data": {
        "train": {
            "train_fold_0": {
                "data": [
                    [
                        "accuracy",
                        0.439716
                    ],
                    [
                        "precision",
                        0.451859
                    ],
                    [
                        "recall",
                        0.450959
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "train_fold_0"
                }
            },
            "train_fold_0_precision": {
                "data": [
                    [
                        0,
                        0.474227
                    ],
                    [
                        1,
                        0.524823
                    ],
                    [
                        2,
                        0.416667
                    ],
                    [
                        3,
                        0.39172
                    ]
                ],
                "meta": {
                    "curve_name": "train_fold_0",
                    "metric_type": "PRECISION_MULTI_EVALUATION",
                    "name": "train_fold_0_precision",
                    "ordinate_name": "Precision",
                    "pair_type": "train_fold_0"
                }
            },
            "train_fold_0_recall": {
                "data": [
                    [
                        0,
                        0.306667
                    ],
                    [
                        1,
                        0.5
                    ],
                    [
                        2,
                        0.036232
                    ],
                    [
                        3,
                        0.960938
                    ]
                ],
                "meta": {
                    "curve_name": "train_fold_0",
                    "metric_type": "RECALL_MULTI_EVALUATION",
                    "name": "train_fold_0_recall",
                    "ordinate_name": "Recall",
                    "pair_type": "train_fold_0"
                }
            },
            "train_fold_1": {},
            "train_fold_1_precision": {},
            "train_fold_1_recall": {},
            "train_fold_2": {},
            "train_fold_2_precision": {},
            "train_fold_2_recall": {}
        },
        "validate": {
            "validate_fold_0": {
                "data": [
                    [
                        "accuracy",
                        0.421986
                    ],
                    [
                        "precision",
                        0.557218
                    ],
                    [
                        "recall",
                        0.42766
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "validate_fold_0"
                }
            },
            "validate_fold_0_precision": {
                "data": [
                    [
                        0,
                        0.348837
                    ],
                    [
                        1,
                        0.47541
                    ],
                    [
                        2,
                        1.0
                    ],
                    [
                        3,
                        0.404624
                    ]
                ],
                "meta": {
                    "curve_name": "validate_fold_0",
                    "metric_type": "PRECISION_MULTI_EVALUATION",
                    "name": "validate_fold_0_precision",
                    "ordinate_name": "Precision",
                    "pair_type": "validate_fold_0"
                }
            },
            "validate_fold_0_recall": {
                "data": [
                    [
                        0,
                        0.241935
                    ],
                    [
                        1,
                        0.42029
                    ],
                    [
                        2,
                        0.0625
                    ],
                    [
                        3,
                        0.985915
                    ]
                ],
                "meta": {
                    "curve_name": "validate_fold_0",
                    "metric_type": "RECALL_MULTI_EVALUATION",
                    "name": "validate_fold_0_recall",
                    "ordinate_name": "Recall",
                    "pair_type": "validate_fold_0"
                }
            },
            "validate_fold_1": {},
            "validate_fold_1_precision": {},
            "validate_fold_1_recall": {},
            "validate_fold_2": {},
            "validate_fold_2_precision": {},
            "validate_fold_2_recall": {}
        }
    },
    "retcode": 0,
    "retmsg": "success"
}

output_model = {
    "data": {
        "bestIteration": 0,
        "encryptedWeight": {},
        "header": [],
        "intercept": 0.0,
        "isConverged": False,
        "iters": 0,
        "lossHistory": [],
        "needOneVsRest": False,
        "weight": {}
    },
    "meta": {
        "meta_data": {
            "alpha": 0.01,
            "batchSize": "-1",
            "earlyStop": "diff",
            "fitIntercept": True,
            "learningRate": 0.15,
            "maxIter": "10",
            "needOneVsRest": False,
            "optimizer": "nesterov_momentum_sgd",
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
