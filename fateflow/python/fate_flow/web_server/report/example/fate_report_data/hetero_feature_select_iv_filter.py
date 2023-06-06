param = {
    "job_id": "202207190952078904800",
    "component_name": "HeteroFeatureSelection_0",
    "role": "guest",
    "party_id": 9999
}
data1 = {
    "data": {
        "colNames": [
            "x0",
            "x2",
            "x3",
            "x6",
            "x7",
            "x1",
            "x4",
            "x5",
            "x8",
            "x9"
        ],
        "finalLeftCols": {
            "leftCols": {
                "x0": "true",
                "x2": "true",
                "x3": "true",
                "x6": "true",
                "x7": "true"
            },
            "originalCols": [
                "x0",
                "x1",
                "x2",
                "x3",
                "x4",
                "x5",
                "x6",
                "x7",
                "x8",
                "x9"
            ]
        },
        "header": [
            "x0",
            "x1",
            "x2",
            "x3",
            "x4",
            "x5",
            "x6",
            "x7",
            "x8",
            "x9"
        ],
        "hostColNames": [
            {
                "colNames": [
                    "host_10000_0",
                    "host_10000_2",
                    "host_10000_3",
                    "host_10000_6",
                    "host_10000_7",
                    "host_10000_13",
                    "host_10000_1",
                    "host_10000_4",
                    "host_10000_5",
                    "host_10000_8",
                    "host_10000_9",
                    "host_10000_10",
                    "host_10000_11",
                    "host_10000_12",
                    "host_10000_14",
                    "host_10000_15",
                    "host_10000_16",
                    "host_10000_17",
                    "host_10000_18",
                    "host_10000_19"
                ],
                "partyId": "10000"
            }
        ],
        "results": [
            {
                "featureValues": {
                    "x0": 6.0635508467384085,
                    "x1": 1.216519678434303,
                    "x2": 6.393321297738993,
                    "x3": 6.12783164705005,
                    "x4": 0.9630135966579698,
                    "x5": 2.3211253547754036,
                    "x6": 3.624746703800475,
                    "x7": 5.848836960916138,
                    "x8": 1.0835493722414622,
                    "x9": 0.6087731268906653
                },
                "filterName": "iv_value_thres",
                "hostFeatureValues": [
                    {
                        "featureValues": {
                            "host_10000_0": 4.772018140081738,
                            "host_10000_1": 1.287811028329576,
                            "host_10000_10": 2.9130458386091074,
                            "host_10000_11": 0.09267178686810745,
                            "host_10000_12": 3.120542147191226,
                            "host_10000_13": 4.501487054160195,
                            "host_10000_14": 0.07200925512696324,
                            "host_10000_15": 0.9095191689459525,
                            "host_10000_16": 1.6407360729295024,
                            "host_10000_17": 1.3657760383202207,
                            "host_10000_18": 0.09410384703806986,
                            "host_10000_19": 0.26637669813048975,
                            "host_10000_2": 5.024484528177982,
                            "host_10000_3": 4.819594426871891,
                            "host_10000_4": 0.7742384478868862,
                            "host_10000_5": 2.2585110665310637,
                            "host_10000_6": 4.128188080105035,
                            "host_10000_7": 5.584183070804723,
                            "host_10000_8": 0.6217085524040964,
                            "host_10000_9": 0.2561380940428093
                        }
                    }
                ],
                "hostLeftCols": [
                    {
                        "leftCols": {
                            "host_10000_0": "true",
                            "host_10000_13": "true",
                            "host_10000_2": "true",
                            "host_10000_3": "true",
                            "host_10000_6": "true",
                            "host_10000_7": "true"
                        },
                        "originalCols": [
                            "host_10000_0",
                            "host_10000_1",
                            "host_10000_2",
                            "host_10000_3",
                            "host_10000_4",
                            "host_10000_5",
                            "host_10000_6",
                            "host_10000_7",
                            "host_10000_8",
                            "host_10000_9",
                            "host_10000_10",
                            "host_10000_11",
                            "host_10000_12",
                            "host_10000_13",
                            "host_10000_14",
                            "host_10000_15",
                            "host_10000_16",
                            "host_10000_17",
                            "host_10000_18",
                            "host_10000_19"
                        ]
                    }
                ],
                "leftCols": {
                    "leftCols": {
                        "x0": "true",
                        "x2": "true",
                        "x3": "true",
                        "x6": "true",
                        "x7": "true"
                    },
                    "originalCols": [
                        "x0",
                        "x1",
                        "x2",
                        "x3",
                        "x4",
                        "x5",
                        "x6",
                        "x7",
                        "x8",
                        "x9"
                    ]
                }
            }
        ]
    },
    "meta": {
        "meta_data": {
            "cols": [
                "x0",
                "x1",
                "x2",
                "x3",
                "x4",
                "x5",
                "x6",
                "x7",
                "x8",
                "x9"
            ],
            "filterMetas": [
                {
                    "filterOutNames": "",
                    "filterType": "threshold",
                    "metrics": "iv",
                    "selectFederated": "true",
                    "takeHigh": "true",
                    "threshold": 3.5
                }
            ],
            "filterMethods": [
                "iv_value_thres"
            ],
            "needRun": "true"
        },
        "module_name": "HeteroFeatureSelection"
    },
    "retcode": 0,
    "retmsg": "success"
}