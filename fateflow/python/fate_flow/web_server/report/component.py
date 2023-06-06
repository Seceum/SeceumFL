
from .content import Content


class ContentTemplate:

    Dataset = [
        Content.dataset_shape,
        # modify by tjx 20220811 这个dataset meta和融合样本的dataset_meta_fusion应该类似 待测试
        # Content.dataset_meta
        Content.dataset_meta_fusion
    ]

    Sample = [
        Content.dataset_shape_sample,
        # Content.dataset_glance,
        Content.dataset_meta_sample
    ]
    FusionSample = [
        Content.dataset_shape_fusion,
        Content.dataset_meta_fusion,
        Content.fusion_info
    ]

    Preprocessing = [
        Content.dataset_shape_data_preprocess,
        Content.statistics
    ]

    Binning = [
        Content.sample_distribution_chart,
        Content.binning_info,
        Content.binning_detail
    ]
    Binning1 = [
        Content.binning_info
    ]

    FeatureSelection = [
        Content.dataset_shape_feature_select,
        Content.feature_select
    ]
    # add by tjx 202284
    FeatureSelection1 = [
        Content.dataset_shape_wrapper,
        Content.feature_select
    ]

    Kmeans = [
        Content.cluster_detail,
        Content.centroid_detail
    ]

    LinR = [
        Content.linear_weight,
    ]

    LinRCV = [
        Content.linear_weight,
        # Content.regression_metric_cv
        Content.regression_metric
    ]

    # 纵向Boost
    HeteroBoostBinary = [
        Content.trees,
        Content.feature_importance,
        Content.loss_curve,
        Content.metric_iter_curve
    ]

    HeteroBoostBinaryCV = [
        Content.feature_importance,  # TODO: Remove this?
        Content.loss_curve,
        Content.ks_curve,
        Content.metric_iter_curve
    ]

    HeteroBoostMulti = [
        Content.trees,
        Content.feature_importance,
        Content.loss_curve,
        Content.metric_iter_curve
    ]

    HeteroBoostMultiCV = [
        Content.feature_importance,  # TODO: Remove this?
        Content.loss_curve,
        Content.metric_iter_curve
    ]

    HeteroBoostRegression = [
        Content.trees,
        Content.feature_importance,
        Content.loss_curve,
        Content.metric_iter_curve
    ]

    HeteroBoostRegressionCV = [
        Content.feature_importance,  # TODO: Remove this?
        Content.loss_curve,
        Content.metric_iter_curve
    ]


# 各组件对应的报告内容项
# 这个地方key需要算法自己修改，与前段无关 add by tjx 202283
ComponentContent = {
    # ======
    # 数据样本
    # ======
    # 自有样本
    "OwnerSample": ContentTemplate.Sample,
    # 合作方样本
    "PartySample": ContentTemplate.Sample,
    # 融合样本
    "FusionSample": ContentTemplate.FusionSample,

    # ======
    # 数据融合
    # ======
    # 求交
    "Intersection": ContentTemplate.Dataset,
    # 求并
    "Union": ContentTemplate.Dataset,

    # ========
    # 数据预处理
    # ========
    # 缺失值处理
    "FillMissing": ContentTemplate.Preprocessing,
    # 异常值处理
    "FillOutlier": ContentTemplate.Preprocessing,
    # 标准化
    "StandardScale": ContentTemplate.Preprocessing,
    # 归一化
    "MinMaxScale": ContentTemplate.Preprocessing,
    # 编码与哑变量
    "HeteroOneHotEncoder": [
        # Content.sample_distribution_chart,
        Content.dataset_shape_data_preprocess,
        Content.statistics
    ],
    # 采样
    "Sampling": [
        Content.dataset_shape_data_preprocess,
        Content.sample_distribution_chart_unsampled,
        Content.sample_distribution_chart2
        ,
        Content.statistics
    ],
    # 样本分析
    "Statistics": [
        Content.dataset_shape_data_preprocess,
        # 这个需要的
        Content.sample_distribution_chart1,
        Content.statistics
    ],

    # ======
    # 特征分箱
    # ======
    # 纵向等频
    "HeteroQuantile": ContentTemplate.Binning,
    # 纵向等距
    "HeteroBucket": ContentTemplate.Binning,
    # 纵向卡方
    "HeteroChi2": ContentTemplate.Binning,
    # 横向等频
    "HomoQuantile": ContentTemplate.Binning1,
    # 横向等距
    "HomoBucket": ContentTemplate.Binning1,
    # 横向卡方
    "HomoChi2": ContentTemplate.Binning1,

    # ======
    # 特征选择
    # ======
    # 皮尔逊
    "HeteroPearson": ContentTemplate.FeatureSelection,
    # IV过滤
    "HeteroIVFilter": ContentTemplate.FeatureSelection,
    # VIF过滤
    "HeteroVIFFilter": ContentTemplate.FeatureSelection,
    # 方差过滤
    "HeteroVarianceFilter": ContentTemplate.FeatureSelection,
    # 嵌入法 xgboost
    "HeteroEmbedded": ContentTemplate.FeatureSelection,
    # 嵌入法 lightgbm add by tjx 202284
    "HeteroEmbedded1":ContentTemplate.FeatureSelection,
    # 包装法 lr
    "HeteroWrapper": ContentTemplate.FeatureSelection1,
    # 包装法 linr
    "HeteroWrapper1":ContentTemplate.FeatureSelection1,
    # 包装法 poisson
    "HeteroWrapper2":ContentTemplate.FeatureSelection1,

    # ======
    # 学习算法
    # ======
    # 纵向K-means
    "HeteroKmeans": ContentTemplate.Kmeans,
    "HeteroKmeansClustering": ContentTemplate.Kmeans,
    # 纵向线性回归
    "HeteroLinR": ContentTemplate.LinR,
    "HeteroLinRRegression": ContentTemplate.LinR,
    "HeteroLinRCV": ContentTemplate.LinRCV,
    "HeteroLinRRegressionCV": ContentTemplate.LinRCV,

    # 纵向泊松回归
    "HeteroPoisson": ContentTemplate.LinR,
    "HeteroPoissonRegression": ContentTemplate.LinR,
    "HeteroPoissonCV": ContentTemplate.LinRCV,
    "HeteroPoissonRegressionCV": ContentTemplate.LinRCV,

    # 纵向逻辑回归
    "HeteroLRBinary": ContentTemplate.LinR,
    "HeteroLRMulti": ContentTemplate.LinR,
    "HeteroLRBinaryCV": [
        Content.linear_weight,
        # Content.binary_metric_cv,
        Content.binary_metric,
        Content.ks_curve
    ],
    "HeteroLRMultiCV": [
        Content.linear_weight,
        # Content.multi_metric_cv,
        Content.multi_metric,
        Content.multi_pr_graph
    ],
    # 纵向SecureBoost
    "HeteroSecureBoostBinary": ContentTemplate.HeteroBoostBinary,
    "HeteroSecureBoostBinaryCV": ContentTemplate.HeteroBoostBinaryCV,
    "HeteroSecureBoostMulti": ContentTemplate.HeteroBoostMulti,
    "HeteroSecureBoostMultiCV": ContentTemplate.HeteroBoostMultiCV,
    "HeteroSecureBoostRegression": ContentTemplate.HeteroBoostRegression,
    "HeteroSecureBoostRegressionCV": ContentTemplate.HeteroBoostRegressionCV,
    # 纵向XGBoost
    "HeteroXGBoostBinary": ContentTemplate.HeteroBoostBinary,
    "HeteroXGBoostBinaryCV": ContentTemplate.HeteroBoostBinaryCV,
    "HeteroXGBoostMulti": ContentTemplate.HeteroBoostMulti,
    "HeteroXGBoostMultiCV": ContentTemplate.HeteroBoostMultiCV,
    "HeteroXGBoostRegression": ContentTemplate.HeteroBoostRegression,
    "HeteroXGBoostRegressionCV": ContentTemplate.HeteroBoostRegressionCV,
    # 纵向LightGBM
    "HeteroLightGBMBinary": ContentTemplate.HeteroBoostBinary,
    "HeteroLightGBMBinaryCV": ContentTemplate.HeteroBoostBinaryCV,
    "HeteroLightGBMMulti": ContentTemplate.HeteroBoostMulti,
    "HeteroLightGBMMultiCV": ContentTemplate.HeteroBoostMultiCV,
    "HeteroLightGBMRegression": ContentTemplate.HeteroBoostRegression,
    "HeteroLightGBMRegressionCV": ContentTemplate.HeteroBoostRegressionCV,
    # 纵向神经网络
    "HeteroNNBinary": [
        Content.loss_curve
    ],
    "HeteroNNBinaryCV": [
        # Content.binary_metric_cv,
        Content.binary_metric,
        Content.ks_curve,
        Content.loss_curve
    ],
    "HeteroNNMulti": [
        Content.loss_curve
    ],
    "HeteroNNMultiCV": [
        # Content.multi_metric_cv,
        Content.multi_metric,
        Content.multi_pr_graph,
        Content.loss_curve
    ],
    # 横向逻辑回归
    "HomoLRBinary": [
        Content.linear_weight,
        Content.loss_curve
    ],
    "HomoLRBinaryCV": [
        Content.linear_weight,
        # Content.binary_metric_cv,
        Content.binary_metric,
        Content.ks_curve,
        Content.loss_curve
    ],
    # HomoLR support binary task only
    # HomoLRMulti = []
    # HomoLRMultiCV = []
    # 横向XGBoost
    "HomoXGBoostBinary": [
        Content.trees,
        Content.feature_importance,
        Content.metric_iter_curve
    ],
    "HomoXGBoostBinaryCV": [
        Content.feature_importance,  # TODO: Remove this?
        Content.metric_iter_curve,
        Content.ks_curve,
    ],
    "HomoXGBoostMulti": [
        Content.trees,
        Content.feature_importance,
        Content.metric_iter_curve
    ],
    "HomoXGBoostMultiCV": [
        Content.feature_importance,  # TODO: Remove this?
        Content.metric_iter_curve
    ],
    "HomoXGBoostRegression": [
        Content.trees,
        Content.feature_importance,
        Content.metric_iter_curve
    ],
    # 隐匿查询 add by tjx 202284
    "PIR":[
        Content.pir
    ],
    # 离线预测 add by tjx 20220829
    "Predict":[
        Content.off_predict
    ],
    # HomoXGBoost cv failed in regression tasks
    # HomoXGBoostRegressionCV = []
    # 横向lightGBM
    # TODO
    # 横向神经网络
    "HomoNNBinary": [],  # really no report data
    "HomoNNMulti": [],  # really no report data
    # HomoNN cv failed
    # HomoNNBinaryCV = []
    # HomoNNMultiCV = []

    # ======
    # 场景算法
    # ======
    # 评分卡
    "Scorecard": [
        Content.scorecard
    ],

    # ======
    # 模型评估
    # ======
    # 模型评估 - 二分类
    "EvaluationBinary": [
        Content.binary_metric,
        Content.confusion_matrix,
        Content.ks_curve,
        Content.roc_curve,
        Content.pr_curve,
        Content.lift_graph,
        Content.gain_graph,
        Content.accuracy_curve,
        Content.psi_detail,
        Content.psi_chart
    ],

    # 模型评估 - 多分类
    "EvaluationMulti": [
        Content.multi_metric,
        Content.multi_pr_graph,
        Content.psi_detail,  # TODO: Remove this?
        Content.psi_chart  # TODO: Remove this?
    ],

    # 模型评估 - 回归
    "EvaluationRegression": [
        Content.regression_metric,
        Content.psi_detail,  # TODO: Remove this?
        Content.psi_chart  # TODO: Remove this?
    ],

    # 模型评估 - 聚类
    "EvaluationClustering": [
        Content.clustering_metric,
        Content.contingency_matrix,
        Content.psi_detail,  # TODO: Remove this
        Content.psi_chart  # TODO: Remove this
    ]
}


def get_component_content(module: str):
    """获取一般组件的报告内容项"""
    contents = ComponentContent[module]
    return [content.name for content in contents]


def get_ml_content(module: str, task_type: str, need_cv: bool):
    """获取学习算法类组件、模型评估组件的报告内容项"""
    model = module
    model += task_type.title()
    if need_cv:
        model += 'CV'
    return get_component_content(model)
