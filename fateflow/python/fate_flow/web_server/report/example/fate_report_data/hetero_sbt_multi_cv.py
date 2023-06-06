
job_id = "202204141522390544270"
component_name = "hetero_secure_boost_0"
guest_id = 9999

output_model = {}

metrics = {
    "data": {
        "train": [
            "loss.0",
            "fold_0.iteration_0",
            "fold_0.iteration_0_precision",
            "fold_0.iteration_0_recall",
            "fold_0.iteration_1",
            "fold_0.iteration_1_precision",
            "fold_0.iteration_1_recall",
            "fold_0.iteration_2",
            "fold_0.iteration_2_precision",
            "fold_0.iteration_2_recall",
            "train_fold_0",
            "train_fold_0_precision",
            "train_fold_0_recall",
            "loss.1",
            "fold_1.iteration_0",
            "fold_1.iteration_0_precision",
            "fold_1.iteration_0_recall",
            "fold_1.iteration_1",
            "fold_1.iteration_1_precision",
            "fold_1.iteration_1_recall",
            "fold_1.iteration_2",
            "fold_1.iteration_2_precision",
            "fold_1.iteration_2_recall",
            "train_fold_1",
            "train_fold_1_precision",
            "train_fold_1_recall",
            "loss.2",
            "fold_2.iteration_0",
            "fold_2.iteration_0_precision",
            "fold_2.iteration_0_recall",
            "fold_2.iteration_1",
            "fold_2.iteration_1_precision",
            "fold_2.iteration_1_recall",
            "fold_2.iteration_2",
            "fold_2.iteration_2_precision",
            "fold_2.iteration_2_recall",
            "train_fold_2",
            "train_fold_2_precision",
            "train_fold_2_recall",
            "loss.3",
            "fold_3.iteration_0",
            "fold_3.iteration_0_precision",
            "fold_3.iteration_0_recall",
            "fold_3.iteration_1",
            "fold_3.iteration_1_precision",
            "fold_3.iteration_1_recall",
            "fold_3.iteration_2",
            "fold_3.iteration_2_precision",
            "fold_3.iteration_2_recall",
            "train_fold_3",
            "train_fold_3_precision",
            "train_fold_3_recall",
            "loss.4",
            "fold_4.iteration_0",
            "fold_4.iteration_0_precision",
            "fold_4.iteration_0_recall",
            "fold_4.iteration_1",
            "fold_4.iteration_1_precision",
            "fold_4.iteration_1_recall",
            "fold_4.iteration_2",
            "fold_4.iteration_2_precision",
            "fold_4.iteration_2_recall",
            "train_fold_4",
            "train_fold_4_precision",
            "train_fold_4_recall"
        ],
        "validate": [
            "fold_0.iteration_0",
            "fold_0.iteration_0_precision",
            "fold_0.iteration_0_recall",
            "fold_0.iteration_1",
            "fold_0.iteration_1_precision",
            "fold_0.iteration_1_recall",
            "fold_0.iteration_2",
            "fold_0.iteration_2_precision",
            "fold_0.iteration_2_recall",
            "validate_fold_0",
            "validate_fold_0_precision",
            "validate_fold_0_recall",
            "fold_1.iteration_0",
            "fold_1.iteration_0_precision",
            "fold_1.iteration_0_recall",
            "fold_1.iteration_1",
            "fold_1.iteration_1_precision",
            "fold_1.iteration_1_recall",
            "fold_1.iteration_2",
            "fold_1.iteration_2_precision",
            "fold_1.iteration_2_recall",
            "validate_fold_1",
            "validate_fold_1_precision",
            "validate_fold_1_recall",
            "fold_2.iteration_0",
            "fold_2.iteration_0_precision",
            "fold_2.iteration_0_recall",
            "fold_2.iteration_1",
            "fold_2.iteration_1_precision",
            "fold_2.iteration_1_recall",
            "fold_2.iteration_2",
            "fold_2.iteration_2_precision",
            "fold_2.iteration_2_recall",
            "validate_fold_2",
            "validate_fold_2_precision",
            "validate_fold_2_recall",
            "fold_3.iteration_0",
            "fold_3.iteration_0_precision",
            "fold_3.iteration_0_recall",
            "fold_3.iteration_1",
            "fold_3.iteration_1_precision",
            "fold_3.iteration_1_recall",
            "fold_3.iteration_2",
            "fold_3.iteration_2_precision",
            "fold_3.iteration_2_recall",
            "validate_fold_3",
            "validate_fold_3_precision",
            "validate_fold_3_recall",
            "fold_4.iteration_0",
            "fold_4.iteration_0_precision",
            "fold_4.iteration_0_recall",
            "fold_4.iteration_1",
            "fold_4.iteration_1_precision",
            "fold_4.iteration_1_recall",
            "fold_4.iteration_2",
            "fold_4.iteration_2_precision",
            "fold_4.iteration_2_recall",
            "validate_fold_4",
            "validate_fold_4_precision",
            "validate_fold_4_recall"
        ]
    },
    "retcode": 0,
    "retmsg": "success"
}

metric_all = {
    "data": {
        "train": {
            # 仅保留fold_0与iteration_0相关数据
            "fold_0.iteration_0": {
                "data": [
                    [
                        "accuracy",
                        0.710059
                    ],
                    [
                        "precision",
                        0.723524
                    ],
                    [
                        "recall",
                        0.719316
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "fold_0.iteration_0"
                }
            },
            "fold_0.iteration_0_precision": {
                "data": [
                    [
                        0,
                        0.76
                    ],
                    [
                        1,
                        0.568889
                    ],
                    [
                        2,
                        0.817734
                    ],
                    [
                        3,
                        0.747475
                    ]
                ],
                "meta": {
                    "curve_name": "fold_0.iteration_0",
                    "metric_type": "PRECISION_MULTI_EVALUATION",
                    "name": "fold_0.iteration_0_precision",
                    "ordinate_name": "Precision",
                    "pair_type": "fold_0.iteration_0"
                }
            },
            "fold_0.iteration_0_recall": {
                "data": [
                    [
                        0,
                        0.218391
                    ],
                    [
                        1,
                        0.715084
                    ],
                    [
                        2,
                        0.976471
                    ],
                    [
                        3,
                        0.96732
                    ]
                ],
                "meta": {
                    "curve_name": "fold_0.iteration_0",
                    "metric_type": "RECALL_MULTI_EVALUATION",
                    "name": "fold_0.iteration_0_recall",
                    "ordinate_name": "Recall",
                    "pair_type": "fold_0.iteration_0"
                }
            },
            "fold_0.iteration_1": {},
            "fold_0.iteration_1_precision": {},
            "fold_0.iteration_1_recall": {},
            "fold_0.iteration_2": {},
            "fold_0.iteration_2_precision": {},
            "fold_0.iteration_2_recall": {},
            "fold_1.iteration_0": {},
            "fold_1.iteration_0_precision": {},
            "fold_1.iteration_0_recall": {},
            "fold_1.iteration_1": {},
            "fold_1.iteration_1_precision": {},
            "fold_1.iteration_1_recall": {},
            "fold_1.iteration_2": {},
            "fold_1.iteration_2_precision": {},
            "fold_1.iteration_2_recall": {},
            "fold_2.iteration_0": {},
            "fold_2.iteration_0_precision": {},
            "fold_2.iteration_0_recall": {},
            "fold_2.iteration_1": {},
            "fold_2.iteration_1_precision": {},
            "fold_2.iteration_1_recall": {},
            "fold_2.iteration_2": {},
            "fold_2.iteration_2_precision": {},
            "fold_2.iteration_2_recall": {},
            "fold_3.iteration_0": {},
            "fold_3.iteration_0_precision": {},
            "fold_3.iteration_0_recall": {},
            "fold_3.iteration_1": {},
            "fold_3.iteration_1_precision": {},
            "fold_3.iteration_1_recall": {},
            "fold_3.iteration_2": {},
            "fold_3.iteration_2_precision": {},
            "fold_3.iteration_2_recall": {},
            "fold_4.iteration_0": {},
            "fold_4.iteration_0_precision": {},
            "fold_4.iteration_0_recall": {},
            "fold_4.iteration_1": {},
            "fold_4.iteration_1_precision": {},
            "fold_4.iteration_1_recall": {},
            "fold_4.iteration_2": {},
            "fold_4.iteration_2_precision": {},
            "fold_4.iteration_2_recall": {},
            "loss.0": {
                "data": [
                    [
                        0,
                        0.931158335387804
                    ],
                    [
                        1,
                        0.7365441995840644
                    ],
                    [
                        2,
                        0.6183857253037184
                    ]
                ],
                "meta": {
                    "Best": 0.6183857253037184,
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
                        0.9303328337622111
                    ],
                    [
                        1,
                        0.7274438497643619
                    ],
                    [
                        2,
                        0.6104325708940409
                    ]
                ],
                "meta": {
                    "Best": 0.6104325708940409,
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
                        0.9133338433255753
                    ],
                    [
                        1,
                        0.7186860624803406
                    ],
                    [
                        2,
                        0.5982548303679346
                    ]
                ],
                "meta": {
                    "Best": 0.5982548303679346,
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
                        0.9086718547951493
                    ],
                    [
                        1,
                        0.7260888035765497
                    ],
                    [
                        2,
                        0.6099231818222949
                    ]
                ],
                "meta": {
                    "Best": 0.6099231818222949,
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
                        0.9351296449599206
                    ],
                    [
                        1,
                        0.7511500158113392
                    ],
                    [
                        2,
                        0.6310470625400499
                    ]
                ],
                "meta": {
                    "Best": 0.6310470625400499,
                    "curve_name": "4",
                    "metric_type": "LOSS",
                    "name": "train",
                    "unit_name": "iters"
                }
            },
            "train_fold_0": {
                "data": [
                    [
                        "accuracy",
                        0.792899
                    ],
                    [
                        "precision",
                        0.804972
                    ],
                    [
                        "recall",
                        0.79988
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
                        0.846154
                    ],
                    [
                        1,
                        0.655814
                    ],
                    [
                        2,
                        0.874346
                    ],
                    [
                        3,
                        0.843575
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
                        0.442529
                    ],
                    [
                        1,
                        0.787709
                    ],
                    [
                        2,
                        0.982353
                    ],
                    [
                        3,
                        0.986928
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
            "train_fold_2_recall": {},
            "train_fold_3": {},
            "train_fold_3_precision": {},
            "train_fold_3_recall": {},
            "train_fold_4": {},
            "train_fold_4_precision": {},
            "train_fold_4_recall": {},
        },
        "validate": {
            # 仅保留fold_0与iteration_0相关数据
            "fold_0.iteration_0": {
                "data": [
                    [
                        "accuracy",
                        0.682353
                    ],
                    [
                        "precision",
                        0.647281
                    ],
                    [
                        "recall",
                        0.652281
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "fold_0.iteration_0"
                }
            },
            "fold_0.iteration_0_precision": {
                "data": [
                    [
                        0,
                        0.571429
                    ],
                    [
                        1,
                        0.526316
                    ],
                    [
                        2,
                        0.75
                    ],
                    [
                        3,
                        0.741379
                    ]
                ],
                "meta": {
                    "curve_name": "fold_0.iteration_0",
                    "metric_type": "PRECISION_MULTI_EVALUATION",
                    "name": "fold_0.iteration_0_precision",
                    "ordinate_name": "Precision",
                    "pair_type": "fold_0.iteration_0"
                }
            },
            "fold_0.iteration_0_recall": {
                "data": [
                    [
                        0,
                        0.210526
                    ],
                    [
                        1,
                        0.526316
                    ],
                    [
                        2,
                        0.9375
                    ],
                    [
                        3,
                        0.934783
                    ]
                ],
                "meta": {
                    "curve_name": "fold_0.iteration_0",
                    "metric_type": "RECALL_MULTI_EVALUATION",
                    "name": "fold_0.iteration_0_recall",
                    "ordinate_name": "Recall",
                    "pair_type": "fold_0.iteration_0"
                }
            },
            "fold_0.iteration_1": {},
            "fold_0.iteration_1_precision": {},
            "fold_0.iteration_1_recall": {},
            "fold_0.iteration_2": {},
            "fold_0.iteration_2_precision": {},
            "fold_0.iteration_2_recall": {},
            "fold_1.iteration_0": {},
            "fold_1.iteration_0_precision": {},
            "fold_1.iteration_0_recall": {},
            "fold_1.iteration_1": {},
            "fold_1.iteration_1_precision": {},
            "fold_1.iteration_1_recall": {},
            "fold_1.iteration_2": {},
            "fold_1.iteration_2_precision": {},
            "fold_1.iteration_2_recall": {},
            "fold_2.iteration_0": {},
            "fold_2.iteration_0_precision": {},
            "fold_2.iteration_0_recall": {},
            "fold_2.iteration_1": {},
            "fold_2.iteration_1_precision": {},
            "fold_2.iteration_1_recall": {},
            "fold_2.iteration_2": {},
            "fold_2.iteration_2_precision": {},
            "fold_2.iteration_2_recall": {},
            "fold_3.iteration_0": {},
            "fold_3.iteration_0_precision": {},
            "fold_3.iteration_0_recall": {},
            "fold_3.iteration_1": {},
            "fold_3.iteration_1_precision": {},
            "fold_3.iteration_1_recall": {},
            "fold_3.iteration_2": {},
            "fold_3.iteration_2_precision": {},
            "fold_3.iteration_2_recall": {},
            "fold_4.iteration_0": {},
            "fold_4.iteration_0_precision": {},
            "fold_4.iteration_0_recall": {},
            "fold_4.iteration_1": {},
            "fold_4.iteration_1_precision": {},
            "fold_4.iteration_1_recall": {},
            "fold_4.iteration_2": {},
            "fold_4.iteration_2_precision": {},
            "fold_4.iteration_2_recall": {},
            "validate_fold_0": {
                "data": [
                    [
                        "accuracy",
                        0.717647
                    ],
                    [
                        "precision",
                        0.691109
                    ],
                    [
                        "recall",
                        0.688096
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
                        0.666667
                    ],
                    [
                        1,
                        0.487179
                    ],
                    [
                        2,
                        0.807018
                    ],
                    [
                        3,
                        0.803571
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
                        0.315789
                    ],
                    [
                        1,
                        0.5
                    ],
                    [
                        2,
                        0.958333
                    ],
                    [
                        3,
                        0.978261
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
            "validate_fold_2_recall": {},
            "validate_fold_3": {},
            "validate_fold_3_precision": {},
            "validate_fold_3_recall": {},
            "validate_fold_4": {},
            "validate_fold_4_precision": {},
            "validate_fold_4_recall": {},
        }
    },
    "retcode": 0,
    "retmsg": "success"
}
