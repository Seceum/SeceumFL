
# Loss曲线
loss_curve = {
    "fold": ["fold_0"],
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
        },
        "validate": {}
    }
}

# -----------------------------------------------------------------------------

# 二分类曲线图

# KS曲线
ks_curve = {
    # 交叉验证的次数，未做交叉验证时仅有fold_0
    "fold": ["fold_0"],
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
        },
        # 测试集结果
        "validate": {
            # fold_0
            "fold_0_threshold": [0.9, 0.7, 0.5, 0.3, 0.2],
            "fold_0_tpr": [0.1, 0.4, 0.8, 0.9, 0.9],
            "fold_0_fpr": [0.0, 0.1, 0.2, 0.6, 0.8],
            "fold_0_ks": [0.1, 0.3, 0.6, 0.3, 0.1],
        }
    }
}

# ROC曲线
roc_curve = {
    "fold": ["fold_0"],
    "xAxis": {
        "name": "fpr",
        "data": [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    },
    "yAxis": {
        "name": {
            "threshold": False,
            "tpr": True
        },
        "train": {
            "fold_0_threshold": [1.0, 0.9, 0.7, 0.5, 0.4, 0.3, 0.2, 0.0],
            "fold_0_tpr": [0.0, 0.4, 0.6, 0.75, 0.82, 0.86, 0.90, 0.92]
        },
        "validate": {}
    }
}

# PR曲线 (Precision Recall)
pr_curve = {
    "fold": ["fold_0"],
    "xAxis": {
        "name": "recall",
        "data": [0.0, 0.3, 0.6, 0.8, 0.9, 1.0],
    },
    "yAxis": {
        "name": {
            "threshold": False,
            "precision": True
        },
        "train": {
            "fold_0_threshold": [0.9, 0.7, 0.5, 0.3, 0.2],
            "fold_0_precision": [1.0, 0.98, 0.90, 0.85, 0.78, 0.0]
        },
        "validate": {}
    }
}

# 提升图
lift_graph = {
    "fold": ["fold_0"],
    "xAxis": {
        "name": "percentile",
        "data": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    },
    "yAxis": {
        "name": {
            "threshold": False,
            "lift": True
        },
        "train": {
            "fold_0_threshold": [0.9, 0.7, 0.5, 0.3, 0.2],
            "fold_0_lift": [2.5, 2.4, 2.3, 2.2, 1.6, 1.0]
        },
        "validate": {}
    }
}

# 增益图
gain_graph = {
    "fold": ["fold_0"],
    "xAxis": {
        "name": "percentile",
        "data": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    },
    "yAxis": {
        "name": {
            "threshold": False,
            "gain": True
        },
        "train": {
            "fold_0_threshold": [0.9, 0.7, 0.5, 0.3, 0.2],
            "fold_0_gain": [0.0, 0.3, 0.6, 0.8, 0.9, 1.0]
        },
        "validate": {}
    }
}

# 准确率曲线
accuracy_curve = {
    "fold": ["fold_0"],
    "xAxis": {
        "name": "percentile",
        "data": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    },
    "yAxis": {
        "name": {
            "threshold": False,
            "accuracy": True
        },
        "train": {
            "fold_0_threshold": [0.0, 0.4, 0.8, 0.9, 0.7, 0.5],
            "fold_0_accuracy": [0.0, 0.4, 0.8, 0.9, 0.7, 0.5]
        },
        "validate": {}
    }
}

# -----------------------------------------------------------------------------

# 多分类曲线图

# 多分类Precision Recall图
multi_pr_graph = {
    "fold": ["fold_0"],
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
        },
        "validate": {
            "fold_0_precision": [0.4, 0.5, 0.3],
            "fold_0_recall": [0.45, 0.55, 0.35],
        }
    }
}

# -----------------------------------------------------------------------------

# 迭代指标图 - 二分类
metric_iter_curve_binary = {
    # 交叉验证的次数，未做交叉验证时仅有fold_0
    "fold": ["fold_0"],
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
        },
        # 测试集结果
        "validate": {
        }
    }
}

# 迭代指标图 - 多分类
metric_iter_curve_multi = {
    # 交叉验证的次数，未做交叉验证时仅有fold_0
    "fold": ["fold_0"],
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
        },
        # 测试集结果
        "validate": {
        }
    }
}

# 迭代指标图 - 回归
metric_iter_curve_regression = {
    # 交叉验证的次数，未做交叉验证时仅有fold_0
    "fold": ["fold_0"],
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
        },
        # 测试集结果
        "validate": {
        }
    }
}

