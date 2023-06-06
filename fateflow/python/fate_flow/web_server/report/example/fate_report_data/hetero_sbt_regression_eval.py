
job_id = "202204141509368840500"
component_name = "hetero_secure_boost_0"
guest_id = 9999

metrics = {
    "data": {
        "train": [
            "loss",
            "iteration_0",
            "iteration_1",
            "iteration_2"
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
                        "mean_absolute_error",
                        3.217599
                    ],
                    [
                        "root_mean_squared_error",
                        4.215412
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "iteration_0"
                }
            },
            "iteration_1": {
                "data": [
                    [
                        "mean_absolute_error",
                        3.071757
                    ],
                    [
                        "root_mean_squared_error",
                        3.989688
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "iteration_1"
                }
            },
            "iteration_2": {
                "data": [
                    [
                        "mean_absolute_error",
                        2.973997
                    ],
                    [
                        "root_mean_squared_error",
                        3.86564
                    ]
                ],
                "meta": {
                    "metric_type": "EVALUATION_SUMMARY",
                    "name": "iteration_2"
                }
            },
            "loss": {
                "data": [
                    [
                        0,
                        17.76970093398998
                    ],
                    [
                        1,
                        15.917612795496986
                    ],
                    [
                        2,
                        14.94317324306748
                    ]
                ],
                "meta": {
                    "Best": 14.94317324306748,
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
        "classes": [],
        "featureImportances": [
            {
                "fid": 6,
                "fullname": "host_9998_6",
                "importance": 5.0,
                "importance2": 3837.0369526536997,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 5,
                "fullname": "x5",
                "importance": 4.0,
                "importance2": 3672.5015178071,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 1,
                "fullname": "x1",
                "importance": 2.0,
                "importance2": 414.69719946910004,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 3,
                "fullname": "host_9998_3",
                "importance": 2.0,
                "importance2": 389.2391766661,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 3,
                "fullname": "x3",
                "importance": 2.0,
                "importance2": 244.8885275263,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 2,
                "fullname": "host_9998_2",
                "importance": 2.0,
                "importance2": 313.0964477672,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 1,
                "fullname": "host_9998_1",
                "importance": 2.0,
                "importance2": 289.8211790627,
                "main": "split",
                "sitename": "host:9998"
            },
            {
                "fid": 4,
                "fullname": "x4",
                "importance": 1.0,
                "importance2": 71.0367498548,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 4,
                "fullname": "host_9998_4",
                "importance": 1.0,
                "importance2": 47.9894394113,
                "main": "split",
                "sitename": "host:9998"
            }
        ],
        "featureNameFidMapping": {
            "0": "x0",
            "1": "x1",
            "2": "x2",
            "3": "x3",
            "4": "x4",
            "5": "x5"
        },
        "initScore": [
            10.415189873417722
        ],
        "losses": [
            17.76970093398998,
            15.917612795496986,
            14.94317324306748
        ],
        "modelName": "hetero_sbt",
        "numClasses": 1,
        "treeDim": 1,
        "treeNum": 3,
        "treePlan": [],
        "trees": [
            # 仅保留第1棵树的数据
            {
                "leafCount": {
                    "10": 57,
                    "11": 24,
                    "12": 2,
                    "13": 49,
                    "14": 8,
                    "7": 32,
                    "8": 86,
                    "9": 137
                },
                "missingDirMaskdict": {
                    "0": 1,
                    "1": 1,
                    "5": 1,
                    "6": 1
                },
                "splitMaskdict": {
                    "0": 0.0,
                    "1": 2.0,
                    "5": 3.0,
                    "6": 2.0
                },
                "tree": [
                    {
                        "bid": 0.0,
                        "fid": 5,
                        "id": 0,
                        "isLeaf": False,
                        "leftNodeid": 1,
                        "missingDir": 0,
                        "rightNodeid": 2,
                        "sitename": "guest:9999",
                        "weight": -1e-10
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 1,
                        "isLeaf": False,
                        "leftNodeid": 3,
                        "missingDir": 0,
                        "rightNodeid": 4,
                        "sitename": "guest:9999",
                        "weight": 0.8378809789
                    },
                    {
                        "bid": 0.0,
                        "fid": 6,
                        "id": 2,
                        "isLeaf": False,
                        "leftNodeid": 5,
                        "missingDir": 1,
                        "rightNodeid": 6,
                        "sitename": "host:9998",
                        "weight": -3.1482331065
                    },
                    {
                        "bid": 0.0,
                        "fid": 6,
                        "id": 3,
                        "isLeaf": False,
                        "leftNodeid": 7,
                        "missingDir": 1,
                        "rightNodeid": 8,
                        "sitename": "host:9998",
                        "weight": 0.0170063103
                    },
                    {
                        "bid": 0.0,
                        "fid": 3,
                        "id": 4,
                        "isLeaf": False,
                        "leftNodeid": 9,
                        "missingDir": 1,
                        "rightNodeid": 10,
                        "sitename": "host:9998",
                        "weight": 1.3370428474
                    },
                    {
                        "bid": 0.0,
                        "fid": 3,
                        "id": 5,
                        "isLeaf": False,
                        "leftNodeid": 11,
                        "missingDir": 0,
                        "rightNodeid": 12,
                        "sitename": "guest:9999",
                        "weight": -8.130323866
                    },
                    {
                        "bid": 0.0,
                        "fid": 4,
                        "id": 6,
                        "isLeaf": False,
                        "leftNodeid": 13,
                        "missingDir": 0,
                        "rightNodeid": 14,
                        "sitename": "guest:9999",
                        "weight": -0.8705665695
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
                        "weight": -1.5377870812
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
                        "weight": 0.5960914687
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
                        "weight": 1.8323165803
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
                        "weight": 0.1460854901
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
                        "weight": -8.6471749257
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
                        "weight": -1.8684779253
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 13,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.189486316
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 14,
                        "isLeaf": True,
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.0780721754
                    }
                ]
            },
            {},
            {}
        ]
    },
    "meta": {
        "meta_data": {
            "learningRate": 0.3,
            "nIterNoChange": True,
            "numTrees": 3,
            "objectiveMeta": {
                "objective": "lse",
                "param": []
            },
            "quantileMeta": {
                "binNum": 32,
                "quantileMethod": ""
            },
            "taskType": "regression",
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