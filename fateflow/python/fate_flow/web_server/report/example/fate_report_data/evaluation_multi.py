
job_id = "202204110730062806680"
component_name = "evaluation_0"
guest_id = 9999
algorithm = "hetero_secure_boost_0"

metrics = {
    "data": {
        "train": [
            "hetero_secure_boost_0",
            "hetero_secure_boost_0_precision",
            "hetero_secure_boost_0_recall"
        ]
    },
    "retcode": 0,
    "retmsg": "success"
}

metric_all = {
    "data": {
        "train": {
            "hetero_secure_boost_0": {
                "data": [
                    [
                        "accuracy",
                        0.782506
                    ],
                    [
                        "precision",
                        0.771918
                    ],
                    [
                        "recall",
                        0.78549
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "hetero_secure_boost_0"
                }
            },
            "hetero_secure_boost_0_precision": {
                "data": [
                    [
                        0,
                        0.717647
                    ],
                    [
                        1,
                        0.680851
                    ],
                    [
                        2,
                        0.884298
                    ],
                    [
                        3,
                        0.804878
                    ]
                ],
                "meta": {
                    "curve_name": "hetero_secure_boost_0",
                    "metric_type": "PRECISION_MULTI_EVALUATION",
                    "name": "hetero_secure_boost_0_precision",
                    "ordinate_name": "Precision",
                    "pair_type": "hetero_secure_boost_0"
                }
            },
            "hetero_secure_boost_0_recall": {
                "data": [
                    [
                        0,
                        0.575472
                    ],
                    [
                        1,
                        0.589862
                    ],
                    [
                        2,
                        0.981651
                    ],
                    [
                        3,
                        0.994975
                    ]
                ],
                "meta": {
                    "curve_name": "hetero_secure_boost_0",
                    "metric_type": "RECALL_MULTI_EVALUATION",
                    "name": "hetero_secure_boost_0_recall",
                    "ordinate_name": "Recall",
                    "pair_type": "hetero_secure_boost_0"
                }
            }
        }
    },
    "retcode": 0,
    "retmsg": "success"
}

output_model = {}
