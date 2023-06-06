
# 二分类评估指标 - 学习算法组件 - 交叉验证
binary_metric_cv = {
    # 交叉验证的次数
    "fold": ["fold_0", "fold_1", "fold_2"],
    #
    "metric": ["auc", "ks"],
    "data": [
        # 训练集结果
        [0.73, 0.68, "train", "fold_0"],
        [0.74, 0.69, "train", "fold_1"],
        [0.71, 0.67, "train", "fold_2"],
        # 测试集结果
        [0.73, 0.68, "validate", "fold_0"],
        [0.74, 0.69, "validate", "fold_1"],
        [0.71, 0.67, "validate", "fold_2"],
    ]
}

# 多分类评估指标 - 学习算法组件 - 交叉验证
multi_metric_cv = {
    "fold": ["fold_0", "fold_1", "fold_2"],
    "metric": ["precision", "recall", "accuracy"],
    "data": [
        # 训练集结果
        [0.91, 0.87, 0.92, "train", "fold_0"],
        [0.92, 0.88, 0.93, "train", "fold_1"],
        [0.89, 0.90, 0.91, "train", "fold_2"],
        # 测试集结果
        [0.91, 0.87, 0.92, "validate", "fold_0"],
        [0.92, 0.88, 0.93, "validate", "fold_1"],
        [0.89, 0.90, 0.91, "validate", "fold_2"]
    ]
}

# 回归评估指标 - 学习算法组件 - 交叉验证
regression_metric_cv = {
    "fold": ["fold_0", "fold_1"],
    "metric": ["mean_absolute_error", "root_mean_squared_error"],
    "data": [
        [1.2, 12, "train", "fold_0"],
        [1.2, 12, "train", "fold_1"],
        [1.2, 12, "train", "fold_2"],
        [1.2, 12, "validate", "fold_0"],
        [1.2, 12, "validate", "fold_0"],
        [1.2, 12, "validate", "fold_0"]
    ]
}
