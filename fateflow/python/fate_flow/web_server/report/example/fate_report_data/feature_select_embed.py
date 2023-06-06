param = {
    "job_id": "202207201635287584870",
    "component_name": "HeteroSecureBoost_0",
    "role": "guest",
    "party_id": 9999
}
data1 = {
    "data": {
        "anonymousNameMapping": {},
        "bestIteration": -1,
        "classes": [
            "0",
            "1"
        ],
        "featureImportances": [
            {
                "fid": 1,
                "fullname": "x1",
                "importance": 7.0,
                "importance2": 61.0073916049,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 7,
                "fullname": "x7",
                "importance": 5.0,
                "importance2": 109.7030143041,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 6,
                "fullname": "x6",
                "importance": 4.0,
                "importance2": 30.1428534751,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 1,
                "fullname": "host_10000_1",
                "importance": 4.0,
                "importance2": 0.0,
                "main": "split",
                "sitename": "host:10000"
            },
            {
                "fid": 2,
                "fullname": "x2",
                "importance": 3.0,
                "importance2": 614.6131389753,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 3,
                "fullname": "x3",
                "importance": 3.0,
                "importance2": 218.32889210949998,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 10,
                "fullname": "host_10000_10",
                "importance": 2.0,
                "importance2": 0.0,
                "main": "split",
                "sitename": "host:10000"
            },
            {
                "fid": 13,
                "fullname": "host_10000_13",
                "importance": 2.0,
                "importance2": 0.0,
                "main": "split",
                "sitename": "host:10000"
            },
            {
                "fid": 4,
                "fullname": "x4",
                "importance": 1.0,
                "importance2": 12.3948596337,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 0,
                "fullname": "x0",
                "importance": 1.0,
                "importance2": 3.6351363725,
                "main": "split",
                "sitename": "guest:9999"
            },
            {
                "fid": 7,
                "fullname": "host_10000_7",
                "importance": 1.0,
                "importance2": 0.0,
                "main": "split",
                "sitename": "host:10000"
            },
            {
                "fid": 0,
                "fullname": "host_10000_0",
                "importance": 1.0,
                "importance2": 0.0,
                "main": "split",
                "sitename": "host:10000"
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
            "8": "x8",
            "9": "x9"
        },
        "initScore": [
            0.0
        ],
        "losses": [
            0.4721718463760302,
            0.3408537158876488,
            0.25373153106142293,
            0.1961252860620534,
            0.15548530453114923
        ],
        "modelName": "hetero_sbt",
        "numClasses": 2,
        "treeDim": 1,
        "treeNum": 5,
        "treePlan": [],
        "trees": [
            {
                "leafCount": {
                    "10": 25,
                    "11": 4,
                    "12": 2,
                    "13": 1,
                    "14": 170,
                    "7": 317,
                    "8": 45,
                    "9": 5
                },
                "missingDirMaskdict": {
                    "0": 1,
                    "1": 1,
                    "2": 1,
                    "3": 1,
                    "4": 1,
                    "5": 1,
                    "6": 1
                },
                "splitMaskdict": {
                    "0": 0.206678,
                    "1": 0.502383,
                    "2": -0.395261,
                    "3": -0.199142,
                    "4": 0.067131,
                    "5": 0.407562,
                    "6": -0.157215
                },
                "tree": [
                    {
                        "bid": 0.0,
                        "fid": 2,
                        "id": 0,
                        "isLeaf": "false",
                        "leftNodeid": 1,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 2,
                        "sitename": "guest:9999",
                        "weight": 0.5093080435
                    },
                    {
                        "bid": 0.0,
                        "fid": 7,
                        "id": 1,
                        "isLeaf": "false",
                        "leftNodeid": 3,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 4,
                        "sitename": "guest:9999",
                        "weight": 1.5800203873
                    },
                    {
                        "bid": 0.0,
                        "fid": 6,
                        "id": 2,
                        "isLeaf": "false",
                        "leftNodeid": 5,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 6,
                        "sitename": "guest:9999",
                        "weight": -1.8602029313
                    },
                    {
                        "bid": 0.0,
                        "fid": 3,
                        "id": 3,
                        "isLeaf": "false",
                        "leftNodeid": 7,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 8,
                        "sitename": "guest:9999",
                        "weight": 1.7880794701
                    },
                    {
                        "bid": 0.0,
                        "fid": 4,
                        "id": 4,
                        "isLeaf": "false",
                        "leftNodeid": 9,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 10,
                        "sitename": "guest:9999",
                        "weight": -0.9210526316
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 5,
                        "isLeaf": "false",
                        "leftNodeid": 11,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 12,
                        "sitename": "guest:9999",
                        "weight": 0.625
                    },
                    {
                        "bid": 0.0,
                        "fid": 0,
                        "id": 6,
                        "isLeaf": "false",
                        "leftNodeid": 13,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 14,
                        "sitename": "guest:9999",
                        "weight": -1.9486581097
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 7,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.9218651543
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 8,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.8370044052
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 9,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.8518518518
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 10,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.4960629922
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 11,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.8181818181
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 12,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.6666666667
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 13,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.4285714285
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 14,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.971830986
                    }
                ]
            },
            {
                "leafCount": {
                    "10": 7,
                    "11": 20,
                    "12": 16,
                    "13": 16,
                    "14": 179,
                    "7": 313,
                    "8": 1,
                    "9": 17
                },
                "missingDirMaskdict": {
                    "0": 1,
                    "1": 1,
                    "4": 1,
                    "5": 1,
                    "6": 1
                },
                "splitMaskdict": {
                    "0": -0.079266,
                    "1": 0.246576,
                    "4": 0.249603,
                    "5": 0.350566,
                    "6": -0.843079
                },
                "tree": [
                    {
                        "bid": 0.0,
                        "fid": 2,
                        "id": 0,
                        "isLeaf": "false",
                        "leftNodeid": 1,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 2,
                        "sitename": "guest:9999",
                        "weight": 0.3892134245
                    },
                    {
                        "bid": 0.0,
                        "fid": 7,
                        "id": 1,
                        "isLeaf": "false",
                        "leftNodeid": 3,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 4,
                        "sitename": "guest:9999",
                        "weight": 1.4067938478
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 2,
                        "isLeaf": "false",
                        "leftNodeid": 5,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 6,
                        "sitename": "host:10000",
                        "weight": -1.0908060289
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 3,
                        "isLeaf": "false",
                        "leftNodeid": 7,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 8,
                        "sitename": "host:10000",
                        "weight": 1.5126353483
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 4,
                        "isLeaf": "false",
                        "leftNodeid": 9,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 10,
                        "sitename": "guest:9999",
                        "weight": 0.0388836051
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 5,
                        "isLeaf": "false",
                        "leftNodeid": 11,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 12,
                        "sitename": "guest:9999",
                        "weight": 0.4831181964
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 6,
                        "isLeaf": "false",
                        "leftNodeid": 13,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 14,
                        "sitename": "guest:9999",
                        "weight": -1.3936073652
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 7,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.5262976899
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 8,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.9383322522
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 9,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.9521525378
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 10,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -2.0863365324
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 11,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.4439733179
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 12,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -0.7307792514
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 13,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.1110879661
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 14,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.5305569101
                    }
                ]
            },
            {
                "leafCount": {
                    "10": 35,
                    "11": 5,
                    "12": 4,
                    "13": 1,
                    "14": 167,
                    "7": 314,
                    "8": 19,
                    "9": 24
                },
                "missingDirMaskdict": {
                    "0": 1,
                    "1": 1,
                    "2": 1,
                    "4": 1,
                    "6": 1
                },
                "splitMaskdict": {
                    "0": 0.045735,
                    "1": 0.246576,
                    "2": -0.308426,
                    "4": 0.008594,
                    "6": -1.588903
                },
                "tree": [
                    {
                        "bid": 0.0,
                        "fid": 3,
                        "id": 0,
                        "isLeaf": "false",
                        "leftNodeid": 1,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 2,
                        "sitename": "guest:9999",
                        "weight": 0.3261579501
                    },
                    {
                        "bid": 0.0,
                        "fid": 7,
                        "id": 1,
                        "isLeaf": "false",
                        "leftNodeid": 3,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 4,
                        "sitename": "guest:9999",
                        "weight": 1.0295690186
                    },
                    {
                        "bid": 0.0,
                        "fid": 6,
                        "id": 2,
                        "isLeaf": "false",
                        "leftNodeid": 5,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 6,
                        "sitename": "guest:9999",
                        "weight": -1.2468772477
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 3,
                        "isLeaf": "false",
                        "leftNodeid": 7,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 8,
                        "sitename": "host:10000",
                        "weight": 1.2810764703
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 4,
                        "isLeaf": "false",
                        "leftNodeid": 9,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 10,
                        "sitename": "guest:9999",
                        "weight": -0.2467671418
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 5,
                        "isLeaf": "false",
                        "leftNodeid": 11,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 12,
                        "sitename": "host:10000",
                        "weight": 0.208319989
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 6,
                        "isLeaf": "false",
                        "leftNodeid": 13,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 14,
                        "sitename": "guest:9999",
                        "weight": -1.3365286466
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 7,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.3419917093
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 8,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.3424950985
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 9,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.9859133467
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 10,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.1260687646
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 11,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.4986999511
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 12,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.4476149847
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 13,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.0384935389
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 14,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.355767523
                    }
                ]
            },
            {
                "leafCount": {
                    "10": 24,
                    "11": 5,
                    "12": 4,
                    "13": 5,
                    "14": 163,
                    "7": 314,
                    "8": 19,
                    "9": 35
                },
                "missingDirMaskdict": {
                    "0": 1,
                    "1": 1,
                    "2": 1,
                    "4": 1
                },
                "splitMaskdict": {
                    "0": 0.045735,
                    "1": 0.246576,
                    "2": -0.308426,
                    "4": 0.350566
                },
                "tree": [
                    {
                        "bid": 0.0,
                        "fid": 3,
                        "id": 0,
                        "isLeaf": "false",
                        "leftNodeid": 1,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 2,
                        "sitename": "guest:9999",
                        "weight": 0.2878240433
                    },
                    {
                        "bid": 0.0,
                        "fid": 7,
                        "id": 1,
                        "isLeaf": "false",
                        "leftNodeid": 3,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 4,
                        "sitename": "guest:9999",
                        "weight": 0.9012556734
                    },
                    {
                        "bid": 0.0,
                        "fid": 6,
                        "id": 2,
                        "isLeaf": "false",
                        "leftNodeid": 5,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 6,
                        "sitename": "guest:9999",
                        "weight": -1.1177573845
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 3,
                        "isLeaf": "false",
                        "leftNodeid": 7,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 8,
                        "sitename": "host:10000",
                        "weight": 1.1416000268
                    },
                    {
                        "bid": 0.0,
                        "fid": 1,
                        "id": 4,
                        "isLeaf": "false",
                        "leftNodeid": 9,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 10,
                        "sitename": "guest:9999",
                        "weight": -0.1961456241
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 5,
                        "isLeaf": "false",
                        "leftNodeid": 11,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 12,
                        "sitename": "host:10000",
                        "weight": 0.1737894175
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 6,
                        "isLeaf": "false",
                        "leftNodeid": 13,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 14,
                        "sitename": "host:10000",
                        "weight": -1.2020411432
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 7,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.2108759918
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 8,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.2518186541
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 9,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.4972810998
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 10,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.3463870111
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 11,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.2785675004
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 12,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.2452118684
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 13,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.0753402365
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 14,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.2517035879
                    }
                ]
            },
            {
                "leafCount": {
                    "10": 6,
                    "11": 17,
                    "12": 205,
                    "4": 4,
                    "7": 314,
                    "8": 3,
                    "9": 20
                },
                "missingDirMaskdict": {
                    "0": 1,
                    "1": 1,
                    "2": 1
                },
                "splitMaskdict": {
                    "0": -0.150752,
                    "1": 1.026178,
                    "2": -0.308426
                },
                "tree": [
                    {
                        "bid": 0.0,
                        "fid": 2,
                        "id": 0,
                        "isLeaf": "false",
                        "leftNodeid": 1,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 2,
                        "sitename": "guest:9999",
                        "weight": 0.2568103605
                    },
                    {
                        "bid": 0.0,
                        "fid": 7,
                        "id": 1,
                        "isLeaf": "false",
                        "leftNodeid": 3,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 4,
                        "sitename": "guest:9999",
                        "weight": 1.0347397638
                    },
                    {
                        "bid": 0.0,
                        "fid": 6,
                        "id": 2,
                        "isLeaf": "false",
                        "leftNodeid": 5,
                        "missingDir": 0,
                        "moWeight": [],
                        "rightNodeid": 6,
                        "sitename": "guest:9999",
                        "weight": -0.6561071262
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 3,
                        "isLeaf": "false",
                        "leftNodeid": 7,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 8,
                        "sitename": "host:10000",
                        "weight": 1.0804880505
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 4,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.3394145679
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 5,
                        "isLeaf": "false",
                        "leftNodeid": 9,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 10,
                        "sitename": "host:10000",
                        "weight": 0.9298794291
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 6,
                        "isLeaf": "false",
                        "leftNodeid": 11,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": 12,
                        "sitename": "host:10000",
                        "weight": -0.8788499661
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 7,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.1141173569
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 8,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.0422054005
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 9,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 1.2927859723
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 10,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -0.2842240902
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 11,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": 0.6492355226
                    },
                    {
                        "bid": -1.0,
                        "fid": -1,
                        "id": 12,
                        "isLeaf": "true",
                        "leftNodeid": -1,
                        "missingDir": 1,
                        "moWeight": [],
                        "rightNodeid": -1,
                        "sitename": "guest:9999",
                        "weight": -1.0471879932
                    }
                ]
            }
        ]
    },
    "meta": {
        "meta_data": {
            "boostingStrategy": "std",
            "learningRate": 0.3,
            "module": "HeteroSecureBoost",
            "nIterNoChange": "true",
            "numTrees": 5,
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
                "useMissing": "false",
                "zeroAsMissing": "false"
            },
            "useMissing": "false",
            "workMode": "",
            "zeroAsMissing": "false"
        },
        "module_name": "HeteroSecureBoost"
    },
    "retcode": 0,
    "retmsg": "success"
}