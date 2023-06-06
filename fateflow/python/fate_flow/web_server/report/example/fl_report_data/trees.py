
tree_0 = {
    "state": [
        {
            "label": "ID: 0\nx7<= -0.085\nGuest:9999",
            "class": "type-suss"
        },
        {
            "label": "ID: 1\nx5<= -0.84\nGuest:9999",
            "class": "type-TOP"
        },
        {
            "label": "ID: 2\nHost:10000",
            "class": "type-TOP"
        },
        {
            "label": "ID: 3\nx3<= -0.55\nGuest:9999",
            "class": "type-TOP"
        },
        {
            "label": "ID: 4\nx0<= 0.48\nGuest:9999",
            "class": "type-TOP"
        },
        {
            "label": "ID: 5\nHost:10000",
            "class": "type-TOP"
        },
        {
            "label": "ID: 6\nx5<= -0.88\nGuest:9999",
            "class": "type-TOP"
        },
    ],
    "edg": [
        {
            "start": 0, "end": 1, "option": {}
        },
        {
            "start": 0, "end": 2, "option": {}
        },
        {
            "start": 1, "end": 3, "option": {}
        },
        {
            "start": 1, "end": 4, "option": {}
        },
        {
            "start": 2, "end": 5, "option": {}
        },
        {
            "start": 2, "end": 6, "option": {}
        },
    ]
}

tree_1 = {
    "state": [
        {
            "label": "ID: 0\nx7<= -0.085\nGuest:9999",
            "class": "type-suss"
        },
        {
            "label": "ID: 1\nx5<= -0.84\nGuest:9999",
            "class": "type-TOP"
        },
        {
            "label": "ID: 2\nHost:10000",
            "class": "type-TOP"
        },
        {
            "label": "ID: 5\nHost:10000",
            "class": "type-TOP"
        },
        {
            "label": "ID: 6\nx5<= -0.88\nGuest:9999",
            "class": "type-TOP"
        },
    ],
    "edg": [
        {
            "start": 0, "end": 1, "option": {}
        },
        {
            "start": 0, "end": 2, "option": {}
        },
        {
            "start": 2, "end": 3, "option": {}
        },
        {
            "start": 2, "end": 4, "option": {}
        },
    ]
}

tree_2 = {
    "state": [
        {
            "label": "ID: 0\nx7<= -0.085\nGuest:9999",
            "class": "type-suss"
        },
        {
            "label": "ID: 1\nx5<= -0.84\nGuest:9999",
            "class": "type-TOP"
        },
        {
            "label": "ID: 2\nHost:10000",
            "class": "type-TOP"
        },
        {
            "label": "ID: 3\nx3<= -0.55\nGuest:9999",
            "class": "type-TOP"
        },
        {
            "label": "ID: 4\nx0<= 0.48\nGuest:9999",
            "class": "type-TOP"
        },
    ],
    "edg": [
        {
            "start": 0, "end": 1, "option": {}
        },
        {
            "start": 0, "end": 2, "option": {}
        },
        {
            "start": 1, "end": 3, "option": {}
        },
        {
            "start": 1, "end": 4, "option": {}
        },
    ]
}

trees_binary = {
    "treeDim": 1,  # 模型数量
    "treeNum": 3,  # 树的总数量
    "iteration": 3,  # 每个模型中的树数量，对应进度条方块个数
    # 列表长度为treeNum
    "data": [
        tree_0,
        tree_1,
        tree_2,
    ]
}

trees_multi = {
    "treeDim": 2,  # 模型数量
    "treeNum": 6,  # 树的总数量
    "iteration": 3,  # 每个模型中的树数量，对应进度条方块个数
    # 列表长度为treeNum
    "data": [
        # model_0的树
        tree_0,
        tree_1,
        tree_2,
        # model_1的树
        tree_0,
        tree_1,
        tree_2,
    ]
}

trees_regression = trees_binary
