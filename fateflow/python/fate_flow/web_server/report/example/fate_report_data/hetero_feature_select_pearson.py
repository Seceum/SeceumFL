param = {
    "job_id": "202207181328543526600",
    "component_name": "HeteroFeatureSelection_0",
    "role": "guest",
    "party_id": 9999
}
data1 = {
    "data": {
        "colNames": [
            "x4",
            "x5",
            "x6",
            "x8",
            "x9",
            "x0",
            "x1",
            "x2",
            "x3",
            "x7"
        ],
        "finalLeftCols": {
            "leftCols": {
                "x4": "true",
                "x5": "true",
                "x6": "true",
                "x8": "true",
                "x9": "true"
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
                    "host_10000_1",
                    "host_10000_4",
                    "host_10000_5",
                    "host_10000_6",
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
                    "host_10000_19",
                    "host_10000_0",
                    "host_10000_2",
                    "host_10000_3",
                    "host_10000_7"
                ],
                "partyId": "10000"
            }
        ],
        "results": [
            {
                "featureValues": {
                    "x0": 0.993707914821418,
                    "x1": 0.9120450145540422,
                    "x2": 0.9703869006755272,
                    "x3": 0.9775780915728319,
                    "x4": 0.0,
                    "x5": 0.0,
                    "x6": 0.0,
                    "x7": 0.9101553918607206,
                    "x8": 0.0,
                    "x9": 0.0
                },
                "filterName": "correlation_filter",
                "hostFeatureValues": [
                    {
                        "featureValues": {
                            "host_10000_0": 0.9651372336335676,
                            "host_10000_1": 0.0,
                            "host_10000_10": 0.0,
                            "host_10000_11": 0.0,
                            "host_10000_12": 0.0,
                            "host_10000_13": 0.0,
                            "host_10000_14": 0.0,
                            "host_10000_15": 0.0,
                            "host_10000_16": 0.0,
                            "host_10000_17": 0.0,
                            "host_10000_18": 0.0,
                            "host_10000_19": 0.0,
                            "host_10000_2": 0.9703869006755272,
                            "host_10000_3": 0.9591191028668717,
                            "host_10000_4": 0.0,
                            "host_10000_5": 0.0,
                            "host_10000_6": 0.0,
                            "host_10000_7": 0.9101553918607206,
                            "host_10000_8": 0.0,
                            "host_10000_9": 0.0
                        }
                    }
                ],
                "hostLeftCols": [
                    {
                        "leftCols": {
                            "host_10000_1": "true",
                            "host_10000_10": "true",
                            "host_10000_11": "true",
                            "host_10000_12": "true",
                            "host_10000_13": "true",
                            "host_10000_14": "true",
                            "host_10000_15": "true",
                            "host_10000_16": "true",
                            "host_10000_17": "true",
                            "host_10000_18": "true",
                            "host_10000_19": "true",
                            "host_10000_4": "true",
                            "host_10000_5": "true",
                            "host_10000_6": "true",
                            "host_10000_8": "true",
                            "host_10000_9": "true"
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
                        "x4": "true",
                        "x5": "true",
                        "x6": "true",
                        "x8": "true",
                        "x9": "true"
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
                    "filterType": "Sort and filter by threshold",
                    "metrics": "correlation",
                    "selectFederated": "true",
                    "takeHigh": "false",
                    "threshold": 0.9
                }
            ],
            "filterMethods": [
                "correlation_filter"
            ],
            "needRun": "true"
        },
        "module_name": "HeteroFeatureSelection"
    },
    "retcode": 0,
    "retmsg": "success"
}