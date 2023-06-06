
job_id = "202204141531256350990"
component_name = "hetero_secure_boost_0"
guest_id = 9999

output_data = {}

metrics = {
    "data": {
        "train": [
            "loss.0",
            "fold_0.iteration_0",
            "fold_0.iteration_1",
            "fold_0.iteration_2",
            "train_fold_0",
            "loss.1",
            "fold_1.iteration_0",
            "fold_1.iteration_1",
            "fold_1.iteration_2",
            "train_fold_1",
            "loss.2",
            "fold_2.iteration_0",
            "fold_2.iteration_1",
            "fold_2.iteration_2",
            "train_fold_2",
            "loss.3",
            "fold_3.iteration_0",
            "fold_3.iteration_1",
            "fold_3.iteration_2",
            "train_fold_3",
            "loss.4",
            "fold_4.iteration_0",
            "fold_4.iteration_1",
            "fold_4.iteration_2",
            "train_fold_4"
        ],
        "validate": [
            "fold_0.iteration_0",
            "fold_0.iteration_1",
            "fold_0.iteration_2",
            "validate_fold_0",
            "fold_1.iteration_0",
            "fold_1.iteration_1",
            "fold_1.iteration_2",
            "validate_fold_1",
            "fold_2.iteration_0",
            "fold_2.iteration_1",
            "fold_2.iteration_2",
            "validate_fold_2",
            "fold_3.iteration_0",
            "fold_3.iteration_1",
            "fold_3.iteration_2",
            "validate_fold_3",
            "fold_4.iteration_0",
            "fold_4.iteration_1",
            "fold_4.iteration_2",
            "validate_fold_4"
        ]
    },
    "retcode": 0,
    "retmsg": "success"
}

metric_all = {
    "data": {
        "train": {
            # 仅保留iteration_0相关数据
            "fold_0.iteration_0": {
                "data": [
                    [
                        "mean_absolute_error",
                        2.929167
                    ],
                    [
                        "root_mean_squared_error",
                        3.876733
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "fold_0.iteration_0"
                }
            },
            "fold_0.iteration_1": {
                "data": [
                    [
                        "mean_absolute_error",
                        2.790979
                    ],
                    [
                        "root_mean_squared_error",
                        3.676591
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "fold_0.iteration_1"
                }
            },
            "fold_0.iteration_2": {
                "data": [
                    [
                        "mean_absolute_error",
                        2.71033
                    ],
                    [
                        "root_mean_squared_error",
                        3.561979
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "fold_0.iteration_2"
                }
            },
            "fold_1.iteration_0": {},
            "fold_1.iteration_1": {},
            "fold_1.iteration_2": {},
            "fold_2.iteration_0": {},
            "fold_2.iteration_1": {},
            "fold_2.iteration_2": {},
            "fold_3.iteration_0": {},
            "fold_3.iteration_1": {},
            "fold_3.iteration_2": {},
            "fold_4.iteration_0": {},
            "fold_4.iteration_1": {},
            "fold_4.iteration_2": {},
            "loss.0": {
                "data": [
                    [
                        0,
                        15.029056354521517
                    ],
                    [
                        1,
                        13.517323532559203
                    ],
                    [
                        2,
                        12.687693992770546
                    ]
                ],
                "meta": {
                    "Best": 12.687693992770546,
                    "curve_name": "0",
                    "metric_type": "LOSS",
                    "name": "train",
                    "unit_name": "iters"
                }
            },
            "loss.1": {
                "data": [
                    [
                        0,
                        18.89192771827273
                    ],
                    [
                        1,
                        16.78292944023195
                    ],
                    [
                        2,
                        15.590296773256847
                    ]
                ],
                "meta": {
                    "Best": 15.590296773256847,
                    "curve_name": "1",
                    "metric_type": "LOSS",
                    "name": "train",
                    "unit_name": "iters"
                }
            },
            "loss.2": {
                "data": [
                    [
                        0,
                        17.178719586215514
                    ],
                    [
                        1,
                        15.200507121771713
                    ],
                    [
                        2,
                        13.961852904897764
                    ]
                ],
                "meta": {
                    "Best": 13.961852904897764,
                    "curve_name": "2",
                    "metric_type": "LOSS",
                    "name": "train",
                    "unit_name": "iters"
                }
            },
            "loss.3": {
                "data": [
                    [
                        0,
                        17.665300118691757
                    ],
                    [
                        1,
                        15.727254522391831
                    ],
                    [
                        2,
                        14.606152077524568
                    ]
                ],
                "meta": {
                    "Best": 14.606152077524568,
                    "curve_name": "3",
                    "metric_type": "LOSS",
                    "name": "train",
                    "unit_name": "iters"
                }
            },
            "loss.4": {
                "data": [
                    [
                        0,
                        18.646847800492523
                    ],
                    [
                        1,
                        16.69567128409683
                    ],
                    [
                        2,
                        15.482428287754008
                    ]
                ],
                "meta": {
                    "Best": 15.482428287754008,
                    "curve_name": "4",
                    "metric_type": "LOSS",
                    "name": "train",
                    "unit_name": "iters"
                }
            },
            "train_fold_0": {
                "data": [
                    [
                        "mean_absolute_error",
                        2.71033
                    ],
                    [
                        "root_mean_squared_error",
                        3.561979
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "train_fold_0"
                }
            },
            "train_fold_1": {},
            "train_fold_2": {},
            "train_fold_3": {},
            "train_fold_4": {},
        },
        "validate": {
            "fold_0.iteration_0": {
                "data": [
                    [
                        "mean_absolute_error",
                        4.163358
                    ],
                    [
                        "root_mean_squared_error",
                        5.273497
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "fold_0.iteration_0"
                }
            },
            "fold_0.iteration_1": {
                "data": [
                    [
                        "mean_absolute_error",
                        3.973107
                    ],
                    [
                        "root_mean_squared_error",
                        4.999017
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "fold_0.iteration_1"
                }
            },
            "fold_0.iteration_2": {
                "data": [
                    [
                        "mean_absolute_error",
                        3.875196
                    ],
                    [
                        "root_mean_squared_error",
                        4.880445
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "fold_0.iteration_2"
                }
            },
            "fold_1.iteration_0": {},
            "fold_1.iteration_1": {},
            "fold_1.iteration_2": {},
            "fold_2.iteration_0": {},
            "fold_2.iteration_1": {},
            "fold_2.iteration_2": {},
            "fold_3.iteration_0": {},
            "fold_3.iteration_1": {},
            "fold_3.iteration_2": {},
            "fold_4.iteration_0": {},
            "fold_4.iteration_1": {},
            "fold_4.iteration_2": {},
            "validate_fold_0": {
                "data": [
                    [
                        "mean_absolute_error",
                        3.875196
                    ],
                    [
                        "root_mean_squared_error",
                        4.880445
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "validate_fold_0"
                }
            },
            "validate_fold_1": {},
            "validate_fold_2": {},
            "validate_fold_3": {},
            "validate_fold_4": {},
        }
    },
    "retcode": 0,
    "retmsg": "success"
}
