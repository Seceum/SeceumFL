
job_id = "202204142250048900820"
component_name = "evaluation_0"
guest_id = 9999
algorithm = "hetero_kmeans_0"

metrics = {
    "data": {
        "train": [
            "hetero_kmeans_0",
            "hetero_kmeans_0_contingency_matrix"
        ]
    },
    "retcode": 0,
    "retmsg": "success"
}

metric_all = {
    "data": {
        "train": {
            "hetero_kmeans_0": {
                "data": [
                    [
                        "adjusted_rand_score",
                        0.479498
                    ],
                    [
                        "fowlkes_mallows_score",
                        0.726712
                    ],
                    [
                        "jaccard_similarity_score",
                        0.021524
                    ]
                ],
                "meta": {
                    "metric_type": "CLUSTERING_EVALUATION_SUMMARY",
                    "name": "hetero_kmeans_0"
                }
            },
            "hetero_kmeans_0_contingency_matrix": {
                "data": [],
                "meta": {
                    "metric_type": "CONTINGENCY_MATRIX",
                    "name": "hetero_kmeans_0_contingency_matrix",
                    "predicted_labels": [
                        0,
                        1,
                        2
                    ],
                    "result_table": [
                        [
                            29,
                            137,
                            46
                        ],
                        [
                            290,
                            0,
                            67
                        ]
                    ],
                    "true_labels": [
                        0,
                        1
                    ]
                }
            }
        }
    },
    "retcode": 0,
    "retmsg": "success"
}

output_model = {}
