
# ================================
# 数据样本、数据预处理、分箱、特征选择报告
# ================================

#########
# 基本信息
#########

# 基本信息
dataset_shape = {
    "sample": 300,  # 样本数量
    "feature": 10,  # 特征数量
}

# 基本信息 - 求交
dataset_shape_intersection = {
    "sample": 300,  # 样本数量
    "feature": 10,  # 特征数量
    "match": 1.0  # 匹配率 100%
}

# 基本信息 - 特征选择
dataset_shape_feature_selection = {
    "sample": 300,  # 样本数量
    "feature": 10,  # 特征数量
    "removed_feature": 4  # 减少特征量
}


##########
# 元数据信息
##########

# 元数据信息 - 样本数据类、求交组件
dataset_meta = {
    # 列名:       名称      所属节点  数据类型       分布          业务属性         描述         样例
    "header": ["feature", "party", "type", "distribution", "attribute", "description", "sample"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
        "attribute": ["标签", "特征"]
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "party_1", "int", "离散", "标签", "", "1, 2, 3"],
        ["feature_2", "party_2", "float", "连续", "特征", "", "1.0, 2.0, 3.0"]
    ]
}

# 元数据信息 - 自有样本
dataset_meta_owner_sample = {
    # 列名:       名称     数据类型       分布          业务属性         描述         样例
    "header": ["feature", "type", "distribution", "attribute", "description", "sample"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
        "attribute": ["标签", "特征"]
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "int", "离散", "标签", "", "1, 2, 3"],
        ["feature_2", "float", "连续", "特征", "", "1.0, 2.0, 3.0"]
    ]
}

# 元数据信息 - 自有样本
dataset_meta_party_sample = {
    # 列名:       名称     数据类型       分布          业务属性         描述
    "header": ["feature", "type", "distribution", "attribute", "description"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
        "attribute": ["标签", "特征"]
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "int", "离散", "标签", ""],
        ["feature_2", "float", "连续", "特征", ""]
    ]
}

# 元数据信息 - 求交组件
dataset_meta_intersection = {
    # 列名:       名称      所属节点  数据类型       分布          业务属性         描述
    "header": ["feature", "party", "type", "distribution", "attribute", "description"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
        "attribute": ["标签", "特征"]
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "party_1", "int", "离散", "标签", ""],
        ["feature_2", "party_2", "float", "连续", "特征", ""]
    ]
}

# 元数据信息 - 求并组件
dataset_meta_union = dataset_meta_party_sample

# 元数据信息 - 皮尔逊
dataset_meta_pearson = {
    # 列名:       名称      所属节点  数据类型       分布          皮尔逊
    "header": ["feature", "party", "type", "distribution", "pearson"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "party_1", "int", "离散", 0.5],
        ["feature_2", "party_2", "float", "连续", 1.0]
    ]
}

# 元数据信息 - IV过滤
dataset_meta_iv = {
    # 列名:       名称      所属节点  数据类型       分布         IV
    "header": ["feature", "party", "type", "distribution", "iv"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "party_1", "int", "离散", 0.5],
        ["feature_2", "party_2", "float", "连续", 1.0]
    ]
}

# 元数据信息 - VIF过滤
dataset_meta_vif = {
    # 列名:       名称      所属节点  数据类型       分布        VIF
    "header": ["feature", "party", "type", "distribution", "vif"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "party_1", "int", "离散", 0.5],
        ["feature_2", "party_2", "float", "连续", 1.0]
    ]
}

# 元数据信息 - 方差过滤
dataset_meta_variance = {
    # 列名:       名称      所属节点  数据类型       分布           方差
    "header": ["feature", "party", "type", "distribution", "variance"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "party_1", "int", "离散", 0.5],
        ["feature_2", "party_2", "float", "连续", 1.0]
    ]
}

# 元数据信息 - 嵌入法
dataset_meta_embedded = {
    # 列名:       名称      所属节点  数据类型       分布              特征重要性
    "header": ["feature", "party", "type", "distribution", "feature_importance"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "party_1", "int", "离散", 0.5],
        ["feature_2", "party_2", "float", "连续", 1.0]
    ]
}

# 元数据信息 - 包装法
dataset_meta_wrapper = {
    # 列名:       名称      所属节点  数据类型       分布           权重系数
    "header": ["feature", "party", "type", "distribution", "coefficient"],
    # 每列取值范围，用于下拉菜单
    "range": {
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
    },
    # 表格数据，按行排列
    "data": [
        ["feature_1", "party_1", "int", "离散", 0.5],
        ["feature_2", "party_2", "float", "连续", 1.0]
    ]
}


############
# 数据前100条
############

dataset_glance = {
    # 列名
    "header": ["id", "y", "x0", "x1", "x2", "x3"],
    # 数据，按行
    "data": [
        [1, 0, 10, 11, 12, 13],
        [2, 1, 20, 21, 22, 23]
    ]
}


########
# 统计信息
########

# 统计信息
# 用于以下组件：缺失值 异常值 归一化 编码与哑变量 采样 样本分析
statistics = {
    # 列名
    #             名称    所属节点  数据类型        分布
    "header": ["feature", "party", "type", "distribution",
               #    缺失数        平均数    中位数    最大值  最小值   求和          标准差
               'missing_count', 'mean', 'median', 'max', 'min', 'sum', 'standard_deviation'],
    # 每列取值范围，用于下拉菜单
    "range": {
        "feature": ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"],
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
        "attribute": ["标签", "特征"]
    },
    # 表格数据，按行排列
    "data": [
        # None代表空值，与null等效
        ["feature_1", "party_1", "int", "离散", None, None, None, None, None, None, None],
        ["feature_2", "party_2", "int", "离散", None, None, None, None, None, None, None],
        ["feature_3", "party_1", "float", "连续", 100, 10, 11, 99, 0, 10000, 9.0],
        ["feature_4", "party_2", "float", "连续", 50, 7, 6, 56, 10, 100, 2.5],
        ["feature_5", "party_2", "float", "连续", 75, 3, 11, 61, 3, 66, 1.7]
    ]
}

# 统计信息
# 用于标准化组件
statistics_standard = {
    # 列名
    #             名称    所属节点  数据类型        分布
    "header": ["feature", "party", "type", "distribution",
               #    缺失数        平均数    中位数    最大值  最小值   求和          标准差             峰度         偏度
               'missing_count', 'mean', 'median', 'max', 'min', 'sum', 'standard_deviation', 'skewness', 'kurtosis'],
    # 每列取值范围，用于下拉菜单
    "range": {
        "feature": ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"],
        "party": ["party_1", "party_2"],
        "type": ["int", "float", "str"],
        "distribution": ["离散", "连续"],
        "attribute": ["标签", "特征"]
    },
    # 表格数据，按行排列
    "data": [
        # None代表空值，与null等效
        ["feature_1", "party_1", "int", "离散", None, None, None, None, None, None, None, None, None],
        ["feature_2", "party_2", "int", "离散", None, None, None, None, None, None, None, None, None],
        ["feature_3", "party_1", "float", "连续", 100, 10, 11, 99, 0, 10000, 9.0, 1.0, 2.0],
        ["feature_4", "party_2", "float", "连续", 50, 7, 6, 56, 10, 100, 2.5, 1.1, 2.1],
        ["feature_5", "party_2", "float", "连续", 75, 3, 11, 61, 3, 66, 1.7, 1.2, 2.2]
    ]
}


##############
# 样本分布直方图
##############

# 样本分布直方图
sample_distribution_chart = {
    "features": ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"],  # 可能有多个
    "xAxis": {
        "name": "interval",  # 区间
        "data": {
            # 各个特征的区间
            "feature_1": ["0", "1"],
            "feature_2": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "feature_3": ["[0.0, 0.5)", "[0.6, 1.0)"],
            "feature_4": ["[0.0, 0.3)", "[0.3, 0.6)", "[0.6, 1.0)"],
            "feature_5": ["[0.0, 0.2)", "[0.2, 0.4)", "[0.4, 0.6)", "[0.6, 0.8)", "[0.8, 1.0)"],
        }
    },
    "yAxis": {
        "name": {
            "count": "bar",  # 记录数: 条形
        },
        "data": {
            # 各个特征的记录数
            "feature1_count": [569, 531],
            "feature2_count": [40, 80, 40, 20, 40, 70, 60, 40, 20, 50],
            "feature3_count": [977, 451],
            "feature4_count": [273, 179, 198],
            "feature5_count": [398, 255, 147, 296, 189],
        }
    }
}

# 样本分布直方图 - 采样前
sample_distribution_chart_unsampled = {
    "features": ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"],  # 可能有多个
    "xAxis": {
        "name": "interval",  # 区间
        "data": {
            # 各个特征的区间
            "feature_1": ["0", "1"],
            "feature_2": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "feature_3": ["[0.0, 0.5)", "[0.6, 1.0)"],
            "feature_4": ["[0.0, 0.3)", "[0.3, 0.6)", "[0.6, 1.0)"],
            "feature_5": ["[0.0, 0.2)", "[0.2, 0.4)", "[0.4, 0.6)", "[0.6, 0.8)", "[0.8, 1.0)"],
        }
    },
    "yAxis": {
        "name": {
            "count": "bar",  # 记录数: 条形
        },
        "data": {
            # 各个特征的记录数
            "feature1_count": [597, 31],
            "feature2_count": [4, 80, 10, 20, 8, 17, 60, 140, 2, 50],
            "feature3_count": [77, 451],
            "feature4_count": [273, 79, 198],
            "feature5_count": [398, 55, 147, 96, 189],
        }
    }
}

# 样本分布直方图 - 分箱
sample_distribution_chart_binning = {
    "features": ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"],  # 可能有多个
    "xAxis": {
        "name": "interval",  # 区间
        "data": {
            # 各个特征的区间
            "feature_1": ["0", "1"],
            "feature_2": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "feature_3": ["[0.0, 0.5)", "[0.6, 1.0)"],
            "feature_4": ["[0.0, 0.3)", "[0.3, 0.6)", "[0.6, 1.0)"],
            "feature_5": ["[0.0, 0.2)", "[0.2, 0.4)", "[0.4, 0.6)", "[0.6, 0.8)", "[0.8, 1.0)"],
        }
    },
    "yAxis": {
        "name": {
            "count": "bar",  # 记录数: 条形
            "woe": "curve"  # WOE: 曲线  分箱组件中使用
        },
        "data": {
            # 各个特征的记录数
            "feature1_count": [569, 531],
            "feature1_woe": [0.2, 0.8],
            "feature2_count": [40, 80, 40, 20, 40, 70, 60, 40, 20, 50],
            "feature2_woe": [0.05, 0.15, 0.12, 0.08, 0.06, 0.14, 0.02, 0.18, 0.11, 0.09],
            "feature3_count": [977, 451],
            "feature3_woe": [0.6, 0.4],
            "feature4_count": [273, 179, 198],
            "feature4_woe": [0.3, 0.2, 0.5],
            "feature5_count": [398, 255, 147, 296, 189],
            "feature5_woe": [0.3, 0.4, 0.1, 0.2, 0.1],
        }
    }
}


##########
# 特征箱线图
##########

feature_box_plot = {
    "features": ["x1", "x2"],  # 可能有多个
    "yAxis": {
        "name": {
            "value": "box",  # 特征值: 箱线图
        },
        "data": {
            "x1": {
                'min': 0,  # 下限
                'max': 100,  # 上限
                'q1': 23,  # 下四分位
                'q2': 52,  # 中位数
                'q3': 81,  # 上四分位
                'outlier': [123, 157, 337]  # 异常值
            },
            "x2": {
                'min': 100,  # 下限
                'max': 1000,  # 上限
                'q1': 257,  # 下四分位
                'q2': 523,  # 中位数
                'q3': 871,  # 上四分位
                'outlier': [56, 1234, -41]  # 异常值
            }
        }
    }
}

#########
# 分箱信息
#########

# 分箱信息
binning_info = {
    "header": ["feature", "bin_num", "iv"],
    "data": [
        ["x1", 5, 1.0],
        ["x2", 6, 1.1],
        ["x3", 7, 1.2],
        ["x4", 8, 1.3],
        ["x5", 9, 1.4],
    ]
}

# 分箱详情
binning_detail = {
    "header": ["binning", "iv", "woe", "event_count", "event_ratio", "non_event_count", "non_event_ratio"],
    "data": [
        [
            ["x0 <= -1.144792", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-1.144792 < x0 <= -0.562683", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-0.562683 < x0 <= 0.019426", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"]
        ],
        [
            ["x0 <= -1.144792", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-1.144792 < x0 <= -0.562683", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-0.562683 < x0 <= 0.019426", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"]
        ],
        [
            ["x0 <= -1.144792", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-1.144792 < x0 <= -0.562683", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-0.562683 < x0 <= 0.019426", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"]
        ],
        [
            ["x0 <= -1.144792", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-1.144792 < x0 <= -0.562683", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-0.562683 < x0 <= 0.019426", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"]
        ],
        [
            ["x0 <= -1.144792", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-1.144792 < x0 <= -0.562683", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"],
            ["-0.562683 < x0 <= 0.019426", 0.352612, -3.718575, 0, "0.2358%", 34, "9.7183%"]
        ]
    ]
}

