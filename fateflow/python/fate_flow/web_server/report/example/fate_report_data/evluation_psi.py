
job_id = "202204162052105101100"
component_name = "Evaluation_0"
guest_id = 9999
algorithm = "HeteroSecureBoost_0"

metrics = {
    "data": {
        "train": [
            "HeteroSecureBoost_0",
            "HeteroSecureBoost_0_ks_fpr",
            "HeteroSecureBoost_0_ks_tpr",
            "HeteroSecureBoost_0_lift",
            "HeteroSecureBoost_0_gain",
            "HeteroSecureBoost_0_accuracy",
            "HeteroSecureBoost_0_precision",
            "HeteroSecureBoost_0_recall",
            "HeteroSecureBoost_0_roc",
            "HeteroSecureBoost_0_confusion_mat",
            "HeteroSecureBoost_0_f1_score",
            "HeteroSecureBoost_0_quantile_pr"
        ],
        "validate": [
            "HeteroSecureBoost_0",
            "HeteroSecureBoost_0_ks_fpr",
            "HeteroSecureBoost_0_ks_tpr",
            "HeteroSecureBoost_0_lift",
            "HeteroSecureBoost_0_gain",
            "HeteroSecureBoost_0_accuracy",
            "HeteroSecureBoost_0_precision",
            "HeteroSecureBoost_0_recall",
            "HeteroSecureBoost_0_roc",
            "HeteroSecureBoost_0_confusion_mat",
            "HeteroSecureBoost_0_psi",
            "HeteroSecureBoost_0_f1_score",
            "HeteroSecureBoost_0_quantile_pr"
        ]
    },
    "retcode": 0,
    "retmsg": "success"
}

metric_all = {
    # 只保留PSI数据
    "data": {
        "train": {},
        "validate": {
            "HeteroSecureBoost_0_psi": {
                "data": [],
                "meta": {
                    "actual_interval": [
                        0,
                        34,
                        1,
                        9,
                        5,
                        3,
                        0,
                        62
                    ],
                    "actual_percentage": [
                        8.771929824561403e-09,
                        0.2982456140350877,
                        0.008771929824561403,
                        0.07894736842105263,
                        0.043859649122807015,
                        0.02631578947368421,
                        8.771929824561403e-09,
                        0.543859649122807
                    ],
                    "expected_interval": [
                        4,
                        132,
                        23,
                        21,
                        24,
                        23,
                        10,
                        218
                    ],
                    "expected_percentage": [
                        0.008791208791208791,
                        0.29010989010989013,
                        0.05054945054945055,
                        0.046153846153846156,
                        0.05274725274725275,
                        0.05054945054945055,
                        0.02197802197802198,
                        0.47912087912087914
                    ],
                    "intervals": [
                        "[0.099716, 0.10193)",
                        "[0.10193, 0.116648)",
                        "[0.116648, 0.334523)",
                        "[0.334523, 0.692915)",
                        "[0.692915, 0.812061)",
                        "[0.812061, 0.884441)",
                        "[0.884441, 0.890831)",
                        "[0.890831, 0.891634]"
                    ],
                    "metric_type": "PSI",
                    "name": "HeteroSecureBoost_0_psi",
                    "psi_scores": [
                        0.121474,
                        0.000225,
                        0.073169,
                        0.017604,
                        0.00164,
                        0.015819,
                        0.323824,
                        0.008205
                    ],
                    "total_psi": 0.56196,
                    "train_pos_perc": [
                        0.0,
                        0.0,
                        0.0,
                        0.42857142857142855,
                        0.9166666666666666,
                        1.0,
                        1.0,
                        0.9954128440366973
                    ],
                    "validate_pos_perc": [
                        0.0,
                        0.0,
                        0.0,
                        0.7777777777777778,
                        0.8,
                        1.0,
                        0.0,
                        1.0
                    ]
                }
            },
        }
    },
    "retcode": 0,
    "retmsg": "success"
}

output_model = {}
