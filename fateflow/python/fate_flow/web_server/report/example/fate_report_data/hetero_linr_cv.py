
job_id = "202204171043543339210"
component_name = "hetero_linr_0"
guest_id = 9999

metrics = {
    "data": {
        "train": [
            "train_fold_0",
            "train_fold_1",
            "train_fold_2",
            "train_fold_3",
            "train_fold_4"
        ],
        "validate": [
            "validate_fold_0",
            "validate_fold_1",
            "validate_fold_2",
            "validate_fold_3",
            "validate_fold_4"
        ]
    },
    "retcode": 0,
    "retmsg": "success"
}

metric_all = {
    "data": {
        "train": {
            "train_fold_0": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.238908
                    ],
                    [
                        "root_mean_squared_error",
                        0.318764
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "train_fold_0"
                }
            },
            "train_fold_1": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.236648
                    ],
                    [
                        "root_mean_squared_error",
                        0.318992
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "train_fold_1"
                }
            },
            "train_fold_2": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.235376
                    ],
                    [
                        "root_mean_squared_error",
                        0.315606
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "train_fold_2"
                }
            },
            "train_fold_3": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.24088
                    ],
                    [
                        "root_mean_squared_error",
                        0.317329
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "train_fold_3"
                }
            },
            "train_fold_4": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.243664
                    ],
                    [
                        "root_mean_squared_error",
                        0.324274
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "train_fold_4"
                }
            }
        },
        "validate": {
            "validate_fold_0": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.253033
                    ],
                    [
                        "root_mean_squared_error",
                        0.33158
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "validate_fold_0"
                }
            },
            "validate_fold_1": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.25903
                    ],
                    [
                        "root_mean_squared_error",
                        0.332531
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "validate_fold_1"
                }
            },
            "validate_fold_2": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.247411
                    ],
                    [
                        "root_mean_squared_error",
                        0.333407
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "validate_fold_2"
                }
            },
            "validate_fold_3": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.233392
                    ],
                    [
                        "root_mean_squared_error",
                        0.325237
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "validate_fold_3"
                }
            },
            "validate_fold_4": {
                "data": [
                    [
                        "mean_absolute_error",
                        0.216348
                    ],
                    [
                        "root_mean_squared_error",
                        0.291747
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "validate_fold_4"
                }
            }
        }
    },
    "retcode": 0,
    "retmsg": "success"
}

output_model = {
    "data": {
        "bestIteration": -1,
        "header": [],
        "intercept": 0.0,
        "isConverged": False,
        "iters": 0,
        "lossHistory": [],
        "weight": {}
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
            "penalty": "NONE",
            "tol": 0.001
        },
        "module_name": "HeteroLinR"
    },
    "retcode": 0,
    "retmsg": "success"
}
