
# 线性模型权重 - 二分类
linear_weight_binary = {
    # 列名       名称     特征权重
    "header": ["feature", "weight"],
    # 对应交叉验证次数，未交叉验证时仅有fold_0
    "fold": ["fold_0"],
    # 对应任务类别，二分类时仅有一项
    "model": ["model_0"],
    # 模型权重
    "data": [
        # 按行
        # fold_0, model_0
        ["feature_1", 0.1, "fold_0", "model_0"],
        ["feature_2", 0.2, "fold_0", "model_0"],
    ]
}

# 线性模型权重 - 二分类 - 交叉验证
linear_weight_binary_cv = {
    # 列名       名称     特征权重
    "header": ["feature", "weight"],
    # 对应交叉验证次数
    "fold": ["fold_0", "fold_1"],
    # 对应任务类别，二分类时仅有一项
    "model": ["model_0"],
    # 模型权重
    "data": [
        # 按行
        # fold_0, model_0
        ["feature_1", 0.1, "fold_0", "model_0"],
        ["feature_2", 0.2, "fold_0", "model_0"],
        # fold_1, model_0
        ["feature_1", 0.1, "fold_1", "model_0"],
        ["feature_2", 0.2, "fold_1", "model_0"],
    ]
}

# 线性模型权重 - 多分类
linear_weight_multi = {
    # 列名       名称     特征权重
    "header": ["feature", "weight"],
    # 对应交叉验证次数，未交叉验证时仅有fold_0
    "fold": ["fold_0"],
    # 对应任务类别
    "model": ["model_0", "model_1"],
    # 模型权重
    "data": [
        # 按行
        # fold_0, model_0
        ["feature_1", 0.1, "fold_0", "model_0"],
        ["feature_2", 0.2, "fold_0", "model_0"],
        # fold_0, model_1
        ["feature_1", 0.1, "fold_0", "model_1"],
        ["feature_2", 0.2, "fold_0", "model_1"],
    ]
}

# 线性模型权重 - 多分类 - 交叉验证
linear_weight_multi_cv = {
    # 列名       名称     特征权重
    "header": ["feature", "weight"],
    # 对应交叉验证次数，未交叉验证时仅有fold_0
    "fold": ["fold_0", "fold_1"],
    # 对应任务类别，二分类时仅有一项
    "model": ["model_0", "model_1"],
    # 模型权重
    "data": [
        # 按行
        # fold_0, model_0
        ["feature_1", 0.1, "fold_0", "model_0"],
        ["feature_2", 0.2, "fold_0", "model_0"],
        # fold_0, model_1
        ["feature_1", 0.1, "fold_0", "model_1"],
        ["feature_2", 0.2, "fold_0", "model_1"],
        # fold_1, model_0
        ["feature_1", 0.1, "fold_1", "model_0"],
        ["feature_2", 0.2, "fold_1", "model_0"],
        # fold_1, model_1
        ["feature_1", 0.1, "fold_1", "model_1"],
        ["feature_2", 0.2, "fold_1", "model_1"],
    ]
}

# 线性模型权重 - 回归
linear_weight_regression = linear_weight_binary

# 线性模型权重 - 回归 - 交叉验证
linear_weight_regression_cv = linear_weight_binary_cv

