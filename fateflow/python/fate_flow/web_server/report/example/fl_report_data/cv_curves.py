
# Loss曲线 - 交叉验证
loss_curve_cv = {
    "fold": ["fold_0", "fold_1", "fold_2"],
    "xAxis": {
        "name": "iters",
        "data": [0, 1, 2]
    },
    "yAxis": {
        "name": {
            "loss": True
        },
        "train": {
            "fold_0_loss": [0.3, 0.1, 0.05],
            "fold_1_loss": [0.3, 0.09, 0.01],
            "fold_2_loss": [0.3, 0.09, 0.01]
        },
        "validate": {}
    }
}

# KS曲线 - 交叉验证
ks_curve_cv = {
    # 交叉验证的次数，未做交叉验证时仅有fold_0
    "fold": ["fold_0", "fold_1"],
    # 横轴
    "xAxis": {
        "name": "percentile",
        "data": [0.2, 0.4, 0.6, 0.8, 1.0],
    },
    # 纵轴
    "yAxis": {
        "name": {
            "tpr": True,  # True代表绘制该曲线(图中1区域)，同时鼠标悬停时要显示(图中2区域)
            "fpr": True,
            "threshold": False,  # False代表不绘制该曲线，但是鼠标悬停时要显示(图中2区域)
            "ks": False
        },
        # 训练集结果
        "train": {
            # fold_0
            "fold_0_threshold": [0.9, 0.7, 0.5, 0.3, 0.2],
            "fold_0_tpr": [0.1, 0.4, 0.8, 0.9, 0.9],
            "fold_0_fpr": [0.0, 0.1, 0.2, 0.6, 0.8],
            "fold_0_ks": [0.1, 0.3, 0.6, 0.3, 0.1],
            # fold_1
            "fold_1_threshold": [0.9, 0.7, 0.5, 0.3, 0.2],
            "fold_1_tpr": [0.1, 0.4, 0.8, 0.9, 0.9],
            "fold_1_fpr": [0.0, 0.1, 0.2, 0.6, 0.8],
            "fold_1_ks": [0.1, 0.3, 0.6, 0.3, 0.1],
        },
        # 测试集结果
        "validate": {
            # fold_0
            "fold_0_threshold": [0.9, 0.7, 0.5, 0.3, 0.2],
            "fold_0_tpr": [0.1, 0.4, 0.8, 0.9, 0.9],
            "fold_0_fpr": [0.0, 0.1, 0.2, 0.6, 0.8],
            "fold_0_ks": [0.1, 0.3, 0.6, 0.3, 0.1],
            # fold_1
            "fold_1_threshold": [0.9, 0.7, 0.5, 0.3, 0.2],
            "fold_1_tpr": [0.1, 0.4, 0.8, 0.9, 0.9],
            "fold_1_fpr": [0.0, 0.1, 0.2, 0.6, 0.8],
            "fold_1_ks": [0.1, 0.3, 0.6, 0.3, 0.1]
        }
    }
}

# 多分类Precision Recall图 - 交叉验证
multi_pr_grap_cv = {
    "fold": ["fold_0", "fold_1"],
    "xAxis": {
        "name": "class",
        "data": ["0", "1", "2"],
    },
    "yAxis": {
        "name": {
            "precision": True,
            "recall": True
        },
        "train": {
            "fold_0_precision": [0.4, 0.5, 0.3],
            "fold_0_recall": [0.45, 0.55, 0.35],
            "fold_1_precision": [0.42, 0.52, 0.32],
            "fold_1_recall": [0.47, 0.57, 0.37],
        },
        "validate": {
            "fold_0_precision": [0.4, 0.5, 0.3],
            "fold_0_recall": [0.45, 0.55, 0.35],
            "fold_1_precision": [0.42, 0.52, 0.32],
            "fold_1_recall": [0.47, 0.57, 0.37],
        }
    }
}

# 迭代指标图 - 二分类 交叉验证
metric_iter_curve_binary_cv = {
    # 交叉验证的次数
    "fold": ["fold_0", "fold_1"],
    # 横轴
    "xAxis": {
        "name": "iteration",
        "data": [0, 1, 2],
    },
    # 纵轴
    "yAxis": {
        "name": {
            "auc": True,  # True代表绘制该曲线(图中1区域)，同时鼠标悬停时要显示(图中2区域)
            "ks": True,
        },
        # 训练集结果
        "train": {
            # fold_0
            "fold_0_auc": [0.5, 0.7, 0.8],
            "fold_0_ks": [0.55, 0.65, 0.85],
            # fold_1
            "fold_1_auc": [0.4, 0.5, 0.8],
            "fold_1_ks": [0.6, 0.7, 0.85],
        },
        # 测试集结果
        "validate": {
        }
    }
}

# 迭代指标图 - 多分类 交叉验证
metric_iter_curve_multi_cv = {
    # 交叉验证的次数
    "fold": ["fold_0", "fold_1"],
    # 横轴
    "xAxis": {
        "name": "iteration",
        "data": [0, 1, 2],
    },
    # 纵轴
    "yAxis": {
        "name": {
            "precision": True,  # True代表绘制该曲线(图中1区域)，同时鼠标悬停时要显示(图中2区域)
            "recall": True,
            "accuracy": True,
        },
        # 训练集结果
        "train": {
            # fold_0
            "fold_0_precision": [0.5, 0.7, 0.8],
            "fold_0_recall": [0.55, 0.65, 0.85],
            "fold_0_accuracy": [0.6, 0.7, 0.75],
            # fold_1
            "fold_1_precision": [0.6, 0.65, 0.75],
            "fold_1_recall": [0.5, 0.7, 0.8],
            "fold_1_accuracy": [0.55, 0.75, 0.8],
        },
        # 测试集结果
        "validate": {
        }
    }
}

# 迭代指标图 - 回归 交叉验证
metric_iter_curve_regression_cv = {
    # 交叉验证的次数
    "fold": ["fold_0", "fold_1"],
    # 横轴
    "xAxis": {
        "name": "iteration",
        "data": [0, 1, 2],
    },
    # 纵轴
    "yAxis": {
        "name": {
            "mae": True,  # True代表绘制该曲线(图中1区域)，同时鼠标悬停时要显示(图中2区域)
            "rmse": True,
        },
        # 训练集结果
        "train": {
            # fold_0
            "fold_0_mae": [0.5, 0.7, 0.8],
            "fold_0_rmse": [0.55, 0.65, 0.85],
            # fold_1
            "fold_1_mae": [0.4, 0.5, 0.8],
            "fold_1_rmse": [0.6, 0.7, 0.85],
        },
        # 测试集结果
        "validate": {
        }
    }
}
