
job_id = "202204171100535494040"
component_name = "hetero_poisson_0"
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
                        0.776813
                    ],
                    [
                        "root_mean_squared_error",
                        0.95938
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
                        0.770592
                    ],
                    [
                        "root_mean_squared_error",
                        0.955502
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
                        0.766464
                    ],
                    [
                        "root_mean_squared_error",
                        0.947786
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
                        0.763848
                    ],
                    [
                        "root_mean_squared_error",
                        0.943731
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
                        0.757645
                    ],
                    [
                        "root_mean_squared_error",
                        0.826505
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
                        0.736031
                    ],
                    [
                        "root_mean_squared_error",
                        0.793204
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
                        0.762002
                    ],
                    [
                        "root_mean_squared_error",
                        0.812376
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
                        0.778254
                    ],
                    [
                        "root_mean_squared_error",
                        0.848564
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
                        0.789232
                    ],
                    [
                        "root_mean_squared_error",
                        0.867841
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
                        0.814971
                    ],
                    [
                        "root_mean_squared_error",
                        1.294697
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