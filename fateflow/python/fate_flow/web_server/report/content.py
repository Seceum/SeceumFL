
from enum import Enum, unique, auto


class FateContent:
    """
    定义Fate报告数据中所使用的定义
    """

    # ======
    # common
    # ======
    #
    data = 'data'
    meta = 'meta'
    #
    name = 'name'
    metric_type = 'metric_type'
    #
    fold = 'fold'
    iteration = 'iteration'

    # =========
    # namespace
    # =========
    #
    train = 'train'
    validate = 'validate'

    # =======
    # metrics
    # =======
    #
    accuracy = 'accuracy'
    # Binary
    auc = 'auc'
    ks = 'ks'
    # Multi
    precision = 'precision'
    recall = 'recall'
    # Regression
    mean_absolute_error = 'mean_absolute_error'
    root_mean_squared_error = 'root_mean_squared_error'

    # ======
    # curves
    # ======
    #
    loss = 'loss'
    # Binary
    ks_tpr = 'ks_tpr'
    ks_fpr = 'ks_fpr'
    # Multi

    psi = 'psi'


@unique
class Content(Enum):
    """
    报告项名称
    """

    # ================
    # 数据集、样本相关图表
    # ================

    # 基本信息 求交
    dataset_shape = 'dataset_shape'
    # 融合基本信息
    dataset_shape_fusion="dataset_shape_fusion"
    # 基本信息 样本
    dataset_shape_sample = "dataset_shape_sample"

    # add by tjx 20220727
    # 缺失值基本信息
    dataset_shape_data_preprocess = "dataset_shape_data_preprocess"
    dataset_shape_fill_missing = "dataset_shape_fill_missing"
    dataset_shape_outlier = "dataset_shape_outlier"
    #标准化基本信息
    dataset_shape_standard = "dataset_shape_standard"
    #minmax 基本信息
    dataset_shape_minmax = "dataset_shape_minmax"
    #onehot基本信息
    dataset_shape_onehot = "dataset_shape_onehot"
    #sampling 基本信息
    dataset_shape_sampling = "dataset_shape_sampling"
    #样本分析基本信息
    dataset_shape_statistics = "dataset_shape_statistics"

    #pearson基本信息
    dataset_shape_feature_select = "dataset_shape_feature_select"
    dataset_shape_pearson = "dataset_shape_pearson"
    #iv过滤基本信息
    dataset_shape_iv = "dataset_shape_iv"
    #vif过滤基本信息
    dataset_shape_vif = "dataset_shape_vif"
    #方差过滤基本信息
    dataset_shape_variance = "dataset_shape_variance"
    #嵌入法xgboost基本信息
    dataset_shape_embedded_xgboost = "dataset_shape_embedded_xgboost"
    #嵌入法lightgbm基本信息
    dataset_shape_embedded_lightgbm = "dataset_shape_embedded_lightgbm"
    #包装法lr,linr,poisson基本信息
    dataset_shape_wrapper = "dataset_shape_wrapper_lr"
    # #包装法linr基本信息
    # dataset_shape_wrapper = "dataset_shape_wrapper_linr"
    # #包装法poisson基本信息
    # dataset_shape_wrapper = "dataset_shape_wrapper_poisson"

    # 元数据信息
    dataset_meta = 'dataset_meta'
    # 融合样本元数据信息
    dataset_meta_fusion = "dataset_meta_fusion"
    # 融合样本融合信息
    fusion_info = "fusion_info"
    # 元数据信息 求交
    dataset_meta_sample = "dataset_meta_sample"

    # 数据前100条
    dataset_glance = 'dataset_glance'

    #"隐匿查询"
    pir = "pir"
    #"离线预测" add by tjx 20220829
    off_predict = "off_predict"

    # 统计信息
    statistics = 'statistics'
    #样本分析报告中的样本分布直方图
    sample_distribution_chart1 = "sample_distribution_chart1"
    # 样本分布直方图
    """
    分箱后的样本分布直方图
    """
    sample_distribution_chart = 'sample_distribution_chart'
    """
    样本采样组件
    """
    sample_distribution_chart_unsampled = 'sample_distribution_chart_unsampled'  # 采样前
    sample_distribution_chart2 = 'sample_distribution_chart2' # 采样后

    # 特征箱线图
    feature_box_plot = 'feature_box_plot'

    # 分箱信息
    binning_info = 'binning_info'

    # 分箱详情
    binning_detail = 'binning_detail'

    # 特征选择
    feature_select = 'feature_select'

    # =======
    # 算法模型
    # =======

    # 线性模型权重
    linear_weight = 'linear_weight'

    # 树模型
    trees = 'trees'

    # 特征重要性
    feature_importance = 'feature_importance'

    # Loss曲线
    loss_curve = 'loss_curve'

    # 聚类详情
    cluster_detail = "cluster_detail"

    # 聚类中心详情
    centroid_detail = "centroid_detail"

    # 评分卡
    scorecard = 'scorecard'

    # pearson add by tjx 20220707
    pearson = "pearson"

    # ==========
    # 模型评估报告
    # ==========

    # ----------------------------- 评估指标 ------------------------------

    # 二分类评估指标
    binary_metric = 'binary_metric'  # 用于模型评估组件
    # binary_metric_cv = 'binary_metric_cv'  # TODO: cv suffix? 用于学习算法组件-交叉验证

    # 多分类评估指标
    multi_metric = 'multi_metric'  # 用于模型评估组件
    # multi_metric_cv = 'multi_metric_cv'  # TODO: cv suffix? 用于学习算法组件-交叉验证

    # 回归评估指标
    regression_metric = 'regression_metric'  # 用于模型评估组件
    # regression_metric_cv = 'regression_metric_cv'  # TODO: cv suffix? 用于学习算法组件-交叉验证

    # 聚类评估指标
    clustering_metric = 'clustering_metric'  # 用于模型评估组件

    # ------------------------------ 矩阵 ---------------------------------

    # 分类-混淆矩阵
    confusion_matrix = 'confusion_matrix'

    # 聚类-列联矩阵
    contingency_matrix = 'contingency_matrix'

    # --------------------------- 二分类曲线图 ------------------------------

    # KS曲线
    # 横坐标、纵坐标名称
    ks_curve = 'ks_curve'
    # ROC曲线
    roc_curve = 'roc_curve'
    # PR曲线 (Precision Recall)
    pr_curve = 'pr_curve'
    # 提升图
    lift_graph = 'lift_graph'
    # 增益图
    gain_graph = 'gain_graph'
    # 准确率曲线
    accuracy_curve = 'accuracy_curve'

    # --------------------------- 多分类曲线图 ------------------------------

    # 多分类Precision Recall图
    multi_pr_graph = 'multi_pr_graph'

    # --------------------------- Boosting算法曲线图 ------------------------------

    # 迭代指标图
    metric_iter_curve = 'metric_iter_curve'

    # ------------------------------- PSI ---------------------------------

    # PSI表格
    psi_detail = 'psi_detail'

    # PSI柱状图
    psi_chart = 'psi_chart'

    # Following items is only used in web backend
    # because of the fucking cross validation
    binary_metric_cv = 'binary_metric_cv'
    multi_metric_cv = 'multi_metric_cv'
    regression_metric_cv = 'regression_metric_cv'
    loss_curve_cv = 'loss_curve_cv'
    ks_curve_cv = 'ks_curve_cv'
    multi_pr_graph_cv = 'multi_pr_graph_cv'
    metric_iter_curve_cv = 'metric_iter_curve_cv'
