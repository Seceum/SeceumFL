
from .pipeline_component_factory import Factory
from .wrapper import WrapperBase
from .wrapper import MLWrapperBase
from .wrapper import UnionWrapper
from .wrapper import DataTransformWrapper
from .wrapper import EvaluationWrapper
from .wrapper import PredictWrapper
from .wrapper import PositiveUnlabeledWrapper
from .wrapper import HeteroNNWrapper, HomoNNWrapper
from .feature_selection_wrapper import HeteroFeatureSelectionWrapper
from .psi_wrapper import PsiWrapper
from .job_names import pickname


__m = {
    "Intersection": (WrapperBase, "求交"),
    "FeatureImputation": (WrapperBase, "缺失值"),
    "FeatureOutlier": (WrapperBase, "异常值"),
    "DataTransform1": (WrapperBase, ""),
    "DataTransform": (DataTransformWrapper, "数据源"),
    "FeatureScale": (WrapperBase, "归一化"),
    "OneHotEncoder": (WrapperBase, "独热编码"),
    "HomoOneHotEncoder": (WrapperBase, "独热编码"),
    "Sample": (WrapperBase, "采样"),
    "SampleWeight": (WrapperBase, "样本权重"),
    "HeteroFeatureBinning": (WrapperBase, "特征分箱"),
    "HomoFeatureBinning": (WrapperBase, "特征分箱"),
    "HeteroKmeans": (MLWrapperBase, "K-means"),
    "HeteroLinR": (MLWrapperBase, "线性回归"),
    "HeteroSSHELinR": (MLWrapperBase, "线性回归"),
    "HeteroPoisson": (MLWrapperBase, "泊松回归"),
    "HeteroLR": (MLWrapperBase, "逻辑回归"),
    "HomoLR": (MLWrapperBase, "逻辑回归"),
    "HeteroSSHELR": (MLWrapperBase, "逻辑回归"),
    "HeteroXGBoost": (MLWrapperBase, "XGBoost"),
    "HeteroNN": (HeteroNNWrapper, "深度神经网络"),
    "HomoNN": (HomoNNWrapper, "深度神经网络"),
    "HomoXGBoost": (MLWrapperBase, "XGBoost"),
    "HeteroLightGBM": (MLWrapperBase, "LightGBM"),
    "HeteroFeatureSelection": (HeteroFeatureSelectionWrapper, "特征选择"),
    "PSI": (PsiWrapper, "PSI"),
    "HeteroPearson": (WrapperBase, "皮尔逊"),
    "Evaluation": (EvaluationWrapper, "模型评估"),
    "SIR": (WrapperBase, "隐匿查询"),
    "Prediction": (PredictWrapper, "离线预测"),
    "Reader": (None, "样本加载"),
    "PositiveUnlabeled": (PositiveUnlabeledWrapper, "正样本无标签")
}

__m = {k.lower(): v for k, v in __m.items()}


def WrapperFactory(nm: str, idx: int = 0):
    global __m
    import re
    return __m.get(re.sub(r"_.*", "", nm).lower(), [None,""])[idx]

from .canvas_jobs import data_transform, component_run, component_stop, \
    component_data_features, exception_interpret
