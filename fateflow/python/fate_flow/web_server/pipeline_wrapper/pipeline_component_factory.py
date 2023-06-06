from pipeline.component import *

__m = {
    "DataStatistics": DataStatistics,
    "DataIO": DataIO,
    "Evaluation": Evaluation,
    "HeteroDataSplit": HeteroDataSplit,

    "HeteroFastSecureBoost": HeteroFastSecureBoost,
    "HeteroFeatureBinning": HeteroFeatureBinning,
    "HeteroFeatureSelection": HeteroFeatureSelection,

    "HeteroFTL": HeteroFTL,
    "HeteroLinR": HeteroLinR,
    "HeteroLR": HeteroLR,
    "HeteroNN": HeteroNN,

    "HeteroPearson": HeteroPearson,
    "HeteroPoisson": HeteroPoisson,
    "HeteroSecureBoost": HeteroSecureBoost,
    "HomoDataSplit": HomoDataSplit,

    "HomoLR": HomoLR,
    "HomoNN": HomoNN,
    "HomoSecureBoost": HomoSecureBoost,
    "HomoFeatureBinning": HomoFeatureBinning,
    "Intersection": Intersection,

    "LocalBaseline": LocalBaseline,
    "OneHotEncoder": OneHotEncoder,
    "PSI": PSI,
    "Reader": Reader,
    "Scorecard": Scorecard,

    "Sample": FederatedSample,
    "FeatureScale": FeatureScale,
    "Union": Union,
    "ColumnExpand": ColumnExpand,
    "FeldmanVerifiableSum": FeldmanVerifiableSum,

    "HeteroLightGBM": HeteroLightGBM,
    "HeteroXGBoost": HeteroXGBoost,
    "HomoXGBoost": HomoXGBoost,

    "SampleWeight": SampleWeight,
    "DataTransform": DataTransform,
    "FeatureImputation": FeatureImputation,
    "FeatureOutlier": FeatureOutlier,

    "LabelTransform": LabelTransform,
    "SIR": SecureInformationRetrieval,
    "CacheLoader": CacheLoader,
    "ModelLoader": ModelLoader,

    "HeteroSSHELR": HeteroSSHELR,
    "HeteroKmeans": HeteroKmeans,
    "HomoOneHotEncoder": HomoOneHotEncoder,
    "HeteroSSHELinR": HeteroSSHELinR,

    "PositiveUnlabeled": PositiveUnlabeled
}

__m = {k.lower():v for k,v in __m.items()}

import re
def Factory(nm: str):
    global __m
    return __m.get(re.sub(r"_.*", "", nm.lower()))
