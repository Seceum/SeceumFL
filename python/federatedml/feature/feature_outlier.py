#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import copy

import numpy as np

from federatedml.model_base import ModelBase
from federatedml.feature.outlier import Outlier
from federatedml.protobuf.generated.feature_outliertion_param_pb2  import FeatureOutliertionParam, FeatureOutlierParam
from federatedml.protobuf.generated.feature_outliertion_meta_pb2 import FeatureOutliertionMeta,FeatureOutlierMeta
from federatedml.statistic.data_overview import get_header
from federatedml.util import LOGGER
from federatedml.util.io_check import assert_io_num_rows_equal


class FeatureOutlier(ModelBase):
    def __init__(self):
        super(FeatureOutlier, self).__init__()
        self.summary_obj = None
        self.missing_impute_rate = None
        self.skip_cols = []
        self.col_outlier_fill_method = None
        self.header = None
        from federatedml.param.feature_outlier_param import FeatureOutlierParam
        self.model_param = FeatureOutlierParam()

        self.model_param_name = 'FeatureOutliertionParam'
        self.model_meta_name = 'FeatureOutliertionMeta'

    def _init_model(self, model_param):
        self.outlier_fill_method = model_param.outlier_fill_method
        self.col_outlier_fill_method = model_param.col_outlier_fill_method
        self.default_value = [v for v in model_param.default_value if v!=None and len(str(v))>0] if model_param.default_value else model_param.default_value
        # add by tjx 2023322
        self.d_value = model_param.default_value
        self.missing_impute = model_param.missing_impute
        self.outlier_by_std = model_param.outlier_by_std
        self.outlier_by_quantile = model_param.outlier_by_quantile

    def get_summary(self):
        outlier_summary = dict()
        outlier_summary["missing_value"] = self.missing_impute
        outlier_summary["outlier_impute_value"] = dict(zip(self.header, self.default_value))
        # add by tjx 2023322
        self.d_value = self.default_value
        outlier_summary["outlier_impute_rate"] = dict(zip(self.header, self.missing_impute_rate))
        outlier_summary["skip_cols"] = self.skip_cols
        outlier_summary["outlier_by_std"] = self.outlier_by_std
        outlier_summary["outlier_by_quantile"] = self.outlier_by_quantile
        outlier_summary["col_outlier_fill_method"] = self.col_outlier_fill_method
        outlier_summary["outlier_fill_method"] = self.outlier_fill_method
        return outlier_summary

    def load_model(self, model_dict):
        param_obj = list(model_dict.get('model').values())[0].get(self.model_param_name)
        meta_obj = list(model_dict.get('model').values())[0].get(self.model_meta_name)
        self.header = param_obj.header
        self.missing_fill, self.outlier_fill_method,self.col_outlier_fill_method, \
            self.missing_impute, self.default_value, self.skip_cols,self.outlier_by_std,self.outlier_by_quantile = load_feature_imputer_model(self.header,
                                                                                                 "Outlier",
                                                                                                 meta_obj.imputer_meta,
                                                                                                 param_obj.imputer_param)


    def save_model(self):
        meta_obj, param_obj = save_feature_imputer_model(missing_fill=True,
                                                         outlier_fill_method=self.outlier_fill_method,
                                                         col_outlier_fill_method=self.col_outlier_fill_method,
                                                         missing_impute=self.missing_impute,
                                                         missing_fill_value=self.d_value,
                                                         missing_replace_rate=self.missing_impute_rate,
                                                         header=self.header,
                                                         skip_cols=self.skip_cols,
                                                         outlier_by_std=self.outlier_by_std,
                                                         outlier_by_quantile=self.outlier_by_quantile)

        return meta_obj, param_obj

    def export_model(self):
        missing_imputer_meta, missing_imputer_param = self.save_model()
        meta_obj = FeatureOutliertionMeta(need_run=self.need_run,
                                         imputer_meta=missing_imputer_meta)
        param_obj = FeatureOutliertionParam(header=self.header,
                                           imputer_param=missing_imputer_param)
        model_dict = {
            self.model_meta_name: meta_obj,
            self.model_param_name: param_obj
        }

        return model_dict

    @assert_io_num_rows_equal
    def fit(self, data):
        LOGGER.info(f"Enter Feature Imputation fit")
        imputer_processor = Outlier(self.missing_impute,outlier_by_std=self.outlier_by_std,outlier_by_quantile=self.outlier_by_quantile)
        self.header = get_header(data)
        if self.col_outlier_fill_method:
            for k in self.col_outlier_fill_method.keys():
                if k not in self.header:
                    raise ValueError(f"{k} not found in data header. Please check col_missing_fill_method keys.")
        imputed_data, self.default_value = imputer_processor.fit(data,
                                                                 replace_method=self.outlier_fill_method,
                                                                 replace_value=self.default_value,
                                                                 col_outlier_fill_method=self.col_outlier_fill_method,
                                                                 outlier_by_std=self.outlier_by_std,outlier_by_quantile=self.outlier_by_quantile)
        if self.missing_impute is None:
            self.missing_impute = imputer_processor.get_missing_value_list()
        self.missing_impute_rate = imputer_processor.get_impute_rate("fit")
        # self.header = get_header(imputed_data)
        self.cols_replace_method = imputer_processor.cols_replace_method
        self.skip_cols = imputer_processor.get_skip_cols()
        self.set_summary(self.get_summary())

        return imputed_data

    @assert_io_num_rows_equal
    def transform(self, data):
        LOGGER.info(f"Enter Feature Imputation transform")
        imputer_processor = Outlier(self.missing_impute,self.outlier_by_std,self.outlier_by_quantile)
        imputed_data = imputer_processor.transform(data,
                                                   transform_value=self.default_value,
                                                   skip_cols=self.skip_cols,outlier_by_std = self.outlier_by_std,outlier_by_quantile=self.outlier_by_quantile)
        if self.missing_impute is None:
            self.missing_impute = imputer_processor.get_missing_value_list()

        self.missing_impute_rate = imputer_processor.get_impute_rate("transform")
        return imputed_data


def save_feature_imputer_model(missing_fill=False,
                               outlier_fill_method= None,
                               col_outlier_fill_method=None,
                               missing_impute=None,
                               missing_fill_value=None,
                               missing_replace_rate=None,
                               header=None,
                               skip_cols=None,outlier_by_std=None,outlier_by_quantile=None):
    model_meta = FeatureOutlierMeta()
    model_param = FeatureOutlierParam()

    model_meta.is_imputer = missing_fill
    if missing_fill:
        if outlier_fill_method:
            model_meta.strategy = outlier_fill_method
        if missing_impute is not None:
            # model_meta.missing_value.extend(map(str, missing_impute))
            # missing_value = {k:v for k,v in missing_impute.items()}
            # model_meta.missing_value.update(missing_value)

            for k,v in missing_impute.items():
                missing_value = model_meta.missing_value
                m = missing_value[k].value
                for v1 in v:
                    m.append(v1)

            model_meta.missing_value_type.extend([type(v).__name__ for v in missing_impute])

        if missing_fill_value is not None and header is not None:
            # add by tjx 2023322
            fill_header = []
            t = copy.deepcopy(missing_fill_value)
            missing_fill_value = []
            for i in range(len(header)):
                if header[i] not in skip_cols:
                    fill_header.append(header[i])
                    missing_fill_value.append(t[i] if isinstance(t, list) and i < len(t) else t)
            feature_value_dict = dict(zip(fill_header, map(str, missing_fill_value)))

            model_param.missing_replace_value.update(feature_value_dict)
            missing_fill_value_type = [type(v).__name__ for v in missing_fill_value]
            feature_value_type_dict = dict(zip(fill_header, missing_fill_value_type))
            model_param.missing_replace_value_type.update(feature_value_type_dict)

        if missing_replace_rate is not None:
            missing_replace_rate_dict = dict(zip(header, missing_replace_rate))
            model_param.missing_value_ratio.update(missing_replace_rate_dict)

        if col_outlier_fill_method is not None:
            col_outlier_fill_method = {k: str(v) for k, v in col_outlier_fill_method.items()}
            model_param.col_outlier_fill_method.update(col_outlier_fill_method)

        model_param.outlier_by_std = 0 if outlier_by_std is None else outlier_by_std
        model_param.outlier_by_quantile = 0 if outlier_by_quantile is None else outlier_by_quantile

        model_param.skip_cols.extend(skip_cols)

    return model_meta, model_param


def load_value_to_type(value, value_type):
    if value is None:
        loaded_value = None
    elif value_type in ["int", "int64", "long", "float", "float64", "double"]:
        loaded_value = getattr(np, value_type)(value)
    elif value_type in ["str", "_str"]:
        loaded_value = str(value)
    elif value_type.lower() in ["none", "nonetype"]:
        loaded_value = None
    else:
        raise ValueError(f"unknown value type: {value_type}")
    return loaded_value


def load_feature_imputer_model(header=None,
                               model_name="Outlier",
                               model_meta=None,
                               model_param=None):
    missing_fill = model_meta.is_imputer
    outlier_fill_method = model_meta.strategy
    col_outlier_fill_method = model_param.col_outlier_fill_method
    missing_value = (model_meta.missing_value)
    missing_value_type = list(model_meta.missing_value_type)
    missing_fill_value = model_param.missing_replace_value
    missing_fill_value_type = model_param.missing_replace_value_type
    outlier_by_std = model_param.outlier_by_std
    outlier_by_quantile = model_param.outlier_by_quantile
    skip_cols = list(model_param.skip_cols)

    if missing_fill:
        if not outlier_fill_method:
            outlier_fill_method = None

        if not missing_value:
            missing_value = None
        else:
            # missing_value = [load_value_to_type(missing_value[i],
            #                                     missing_value_type[i]) for i in range(len(missing_value))]
            missing_value1 = {}
            for i in missing_value:
                value1 = missing_value[i]
                v = [va for va in value1.value]
                missing_value1[i] = v
            import copy
            missing_value = copy.deepcopy(missing_value1)
        if missing_fill_value:
            missing_fill_value = [load_value_to_type(missing_fill_value.get(head),
                                                     missing_fill_value_type.get(head)) for head in header]
        else:
            missing_fill_value = None
    else:
        outlier_fill_method = None
        missing_value = None
        missing_fill_value = None
        outlier_by_std = None
        outlier_by_quantile = None
        col_outlier_fill_method = None
    return missing_fill, outlier_fill_method, col_outlier_fill_method,missing_value, missing_fill_value, skip_cols,outlier_by_std,outlier_by_quantile
