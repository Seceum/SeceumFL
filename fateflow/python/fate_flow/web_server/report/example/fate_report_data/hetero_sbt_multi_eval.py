
job_id = "202204110730062806680"
component_name = "hetero_secure_boost_0"
guest_id = 9999

metrics = {
    "data": {
        "train": [
            "loss",
            "iteration_0",
            "iteration_0_precision",
            "iteration_0_recall",
            "iteration_1",
            "iteration_1_precision",
            "iteration_1_recall",
            "iteration_2",
            "iteration_2_precision",
            "iteration_2_recall"
        ]
    },
    "retcode": 0,
    "retmsg": "success"
}

metric_all = {
    "data": {
        "train": {
            "iteration_0": {
                "data": [
                    [
                        "accuracy",
                        0.695035
                    ],
                    [
                        "precision",
                        0.6896
                    ],
                    [
                        "recall",
                        0.697333
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "iteration_0"
                }
            },
            "iteration_0_precision": {
                "data": [
                    [
                        0,
                        0.677419
                    ],
                    [
                        1,
                        0.559524
                    ],
                    [
                        2,
                        0.775362
                    ],
                    [
                        3,
                        0.746094
                    ]
                ],
                "meta": {
                    "curve_name": "iteration_0",
                    "metric_type": "PRECISION_MULTI_EVALUATION",
                    "name": "iteration_0_precision",
                    "ordinate_name": "Precision",
                    "pair_type": "iteration_0"
                }
            },
            "iteration_0_recall": {
                "data": [
                    [
                        0,
                        0.198113
                    ],
                    [
                        1,
                        0.64977
                    ],
                    [
                        2,
                        0.981651
                    ],
                    [
                        3,
                        0.959799
                    ]
                ],
                "meta": {
                    "curve_name": "iteration_0",
                    "metric_type": "RECALL_MULTI_EVALUATION",
                    "name": "iteration_0_recall",
                    "ordinate_name": "Recall",
                    "pair_type": "iteration_0"
                }
            },
            "iteration_1": {},
            "iteration_1_precision": {},
            "iteration_1_recall": {},
            "iteration_2": {},
            "iteration_2_precision": {},
            "iteration_2_recall": {},
            "loss": {
                "data": [
                    [
                        0,
                        0.9357985321771857
                    ],
                    [
                        1,
                        0.7315983159781322
                    ],
                    [
                        2,
                        0.6278852884484867
                    ]
                ],
                "meta": {
                    "Best": 0.6278852884484867,
                    "curve_name": "loss",
                    "metric_type": "LOSS",
                    "name": "train",
                    "unit_name": "iters"
                }
            }
        }
    },
    "retcode": 0,
    "retmsg": "success"
}

output_model = {
    "data": {
        "anonymousNameMapping": {},
        "bestIteration": -1,
        "classes": [
            "0",
            "1",
            "2",
            "3"
        ],
        "featureImportances": [
            {
                "fid": 5,
                "fullname": "x5",
                "importance": 10.0,
                "importance2": 709.2858759449,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 0,
                "fullname": "x0",
                "importance": 8.0,
                "importance2": 157.01435197799998,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 8,
                "fullname": "host_9998_8",
                "importance": 8.0,
                "importance2": 95.2247007976,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 0,
                "fullname": "host_9998_0",
                "importance": 7.0,
                "importance2": 233.1855728356,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 7,
                "fullname": "x7",
                "importance": 7.0,
                "importance2": 731.2154965549,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 4,
                "fullname": "x4",
                "importance": 5.0,
                "importance2": 134.0748529709,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 5,
                "fullname": "host_9998_5",
                "importance": 4.0,
                "importance2": 35.102786428799995,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 7,
                "fullname": "host_9998_7",
                "importance": 4.0,
                "importance2": 109.5096407866,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 1,
                "fullname": "x1",
                "importance": 4.0,
                "importance2": 103.8616818781,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 1,
                "fullname": "host_9998_1",
                "importance": 3.0,
                "importance2": 71.84946304399999,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 3,
                "fullname": "x3",
                "importance": 3.0,
                "importance2": 14.0728011066,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 6,
                "fullname": "x6",
                "importance": 3.0,
                "importance2": 32.7039301405,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 4,
                "fullname": "host_9998_4",
                "importance": 3.0,
                "importance2": 48.5209121466,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 3,
                "fullname": "host_9998_3",
                "importance": 2.0,
                "importance2": 4.8712323553,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 2,
                "fullname": "host_9998_2",
                "importance": 2.0,
                "importance2": 146.6058410299,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 2,
                "fullname": "x2",
                "importance": 2.0,
                "importance2": 21.680552657899998,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 8,
                "fullname": "x8",
                "importance": 1.0,
                "importance2": 16.6655114157,
                "main": "split",
                "sitename": "guest:9999"
            }
        ],
        "featureNameFidMapping": {
            "0": "x0",
            "1": "x1",
            "2": "x2",
            "3": "x3",
            "4": "x4",
            "5": "x5",
            "6": "x6",
            "7": "x7",
            "8": "x8"
        },
        "initScore": [
            0.0,
            0.0,
            0.0,
            0.0
        ],
        "losses": [
            0.9357985321771857,
            0.7315983159781322,
            0.6278852884484867
        ],
        "modelName": "hetero_sbt",
        "numClasses": 4,
        "treeDim": 4,
        "treeNum": 12,
        "treePlan": [],
        "trees": [
            # 仅保留第一棵树的数据
            # 类别1对应树1 2 3
            {
                "leafCount": {
                    "10": 274,
                    "11": 20,
                    "12": 22,
                    "6": 5,
                    "7": 153,
                    "8": 305,
                    "9": 67
                },
                "missingDirMaskdict": {
                    "2": 1,
                    "4": 1
                },
                "splitMaskdict": {
                    "2": 0.478261,
                    "4": -0.849057
                },
                "tree": [
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 0,
                        "isLeaf": False,
                        "leftNodeid": 1,
                        "missingDir": 1,
                        "rightNodeid": 2,
                        "sitename": "host:9998",
                        "weight": 0.0031501023
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 1,
                        "isLeaf": False,
                        "leftNodeid": 3,
                        "missingDir": 1,
                        "rightNodeid": 4,
                        "sitename": "host:9998",
                        "weight": -0.1650963062
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 2,
                        "isLeaf": False,
                        "leftNodeid": 5,
                        "missingDir": 0,
                        "rightNodeid": 6,
                        "sitename": "guest:9999",
                        "weight": 2.8330995792
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 3,
                        "isLeaf": False,
                        "leftNodeid": 7,
                        "missingDir": 1,
                        "rightNodeid": 8,
                        "sitename": "host:9998",
                        "weight": -0.5990113406
                    },
                    {
                        "bid": 0.0,
                        "fid": 5,
                        "id": 4,
                        "isLeaf": False,
                        "leftNodeid": 9,
                        "missingDir": 0,
                        "rightNodeid": 10,
                        "sitename": "guest:9999",
                        "weight": 0.4177239898
                    },
                    {
                        "bid": 0.0,
                        "fid": 5,
                        "id": 5,
                        "isLeaf": False,
                        "leftNodeid": 11,
                        "missingDir": 1,
                        "rightNodeid": 12,
                        "sitename": "host:9998",
                        "weight": 3.3228840125
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 6,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.2048192772
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 7,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.3039513677
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 8,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.0517128519
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 9,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.1648568609
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 10,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.80621661
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 11,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 2.5974025974
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 12,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 3.9053254437
                    }
                ]
            },
            {},
            {},
            # 类别2对应树4 5 6
            {},
            {},
            {},
            # 类别3对应树7 8 9
            {},
            {},
            {},
            # 类别4对应树10 11 12
            {},
            {},
            {},
        ]
    },
    "meta": {
        "meta_data": {
            "learningRate": 0.3,
            "nIterNoChange": True,
            "numTrees": 3,
            "objectiveMeta": {
                "objective": "cross_entropy",
                "param": []
            },
            "quantileMeta": {
                "binNum": 32,
                "quantileMethod": ""
            },
            "taskType": "classification",
            "tol": 0.0001,
            "treeMeta": {
                "criterionMeta": {
                    "criterionMethod": "xgboost",
                    "criterionParam": [
                        0.1,
                        0.0
                    ]
                },
                "maxDepth": 3,
                "minImpuritySplit": 0.001,
                "minLeafNode": 1,
                "minSampleSplit": 2,
                "useMissing": False,
                "zeroAsMissing": False
            },
            "useMissing": False,
            "workMode": "",
            "zeroAsMissing": False
        },
        "module_name": "HeteroSecureBoost"
    },
    "retcode": 0,
    "retmsg": "success"
}