
# 二分类评估指标 - 评估组件报告
binary_metric = {
    "header": ["auc", "ks", "precision", "recall", "F1_score", "accuracy", "lift"],
    "data": [0.71, 0.69, 0.77, 0.80, 0.84, 0.81, 2.5]
}

# 多分类评估指标 - 评估组件
multi_metric = {
    "metric": ["precision", "recall", "accuracy"],
    "data": [0.91, 0.87, 0.92]
}

# 回归评估指标 - 评估组件
regression_metric = {
    "header": ["explained_variance", "mean_absolute_error",
               "mean_squared_error", "median_absolute_error",
               "r2_score", "root_mean_squared_error"],
    "data": [2.3, 3.4, 1.9, 3.9, 0.89, 2.1]
},

# 聚类评估指标 - 评估组件
clustering_metric = {
    "header": ["JC", "FMI", "RI", "distance_measure"],
    "data": [0.33, 9.45, 0.44, 6.73]
}

