BASE_PARAM = {
    "pid": 9999,
    "guest": 9999,
    "hosts": [10000],
    "arbiter":10000,
    "rol": "guest"
}

GUEST_ONLY_PARAM = {
    "with_label": True,
    "output_format": "dense",
}

HOST_ONLY_PARAM = {
    "with_label": False,
}

SELECT_NAMES = []

BINNING_PARAM = {
    "name": 'hetero_feature_binning_0',
    "method": "quantile",
    "compress_thres": 10000,
    "head_size": 10000,
    "error": 0.001,
    "bin_num": 10,
    "bin_indexes": -1,
    "bin_names": None,
    "category_indexes": None,
    "category_names": None,
    "adjustment_factor": 0.5,
    "local_only": False,
    "transform_param": {
        "transform_cols": -1,
        "transform_names": None,
        "transform_type": "bin_num"
    }
}

STATISTIC_PARAM = {
    "name": "statistic_0",
    "statistics": ["95%", "coefficient_of_variance", "stddev"],
    "column_indexes": -1,
    "column_names": []
}

PSI_PARAM = {
    "name": "psi_0",
    "max_bin_num": 20
}

PEARSON_PARAM = {
    "name":"hetero_pearson_0",
    "column_indexes":-1
}

HOMO_SBT_PARAM = {
    "name": "homo_secureboost_0",
    "num_trees": 3,
    "task_type": 'classification',
    'objective_param':{"objective":"cross_entropy"},
    "tree_param":{
        "max_depth":3
    },
    "validation_freqs":1
}

FAST_SBT_PARAM = {
    "name": "fast_secureboost_0",
    "task_type": "classification",
    "learning_rate": 0.1,
    "num_trees": 4,
    "subsample_feature_rate": 1,
    "n_iter_no_change": False,
    #"work_mode": "layered",
    #"guest_depth": 2,
    #"host_depth": 3,
    "tol": 0.0001,
    "bin_num": 50,
    "metrics": ["Recall", "ks", "auc", "roc"],
    "objective_param": {
        "objective": "cross_entropy"
    },
    "encrypt_param": {
        "method": "paillier"
    },
    "predict_param": {
        "threshold": 0.5
    },
    "validation_freqs": 1
}

XGB_SBT_PARAM = {
    "name": "xgb_0",
    "task_type": "classification",
    "learning_rate": 0.1,
    "num_trees": 4,
    "subsample_feature_rate": 1,
    "n_iter_no_change": False,
    "tol": 0.0001,
    "bin_num": 50,
    "metrics": ["Recall", "ks", "auc", "roc"],
    "objective_param": {
        "objective": "cross_entropy"
    },
    "encrypt_param": {
        "method": "paillier"
    },
    "predict_param": {
        "threshold": 0.5
    },
    "validation_freqs": 1
}

CORRELATION_PARAM = {

}