#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from federatedml.param.base_param import BaseParam


class FeatureOutlierParam(BaseParam):
    """
    Define feature imputation parameters

    Parameters
    ----------

    default_value : None or single object type or list
        the value to replace missing value.
        if None, it will use default value defined in federatedml/feature/imputer.py,
        if single object, will fill missing value with this object,
        if list, it's length should be the same as input data' feature dimension,
            means that if some column happens to have missing values, it will replace it
            the value by element in the identical position of this list.

    outlier_fill_method : [None, 'min', 'max', 'mean', 'designated']
        the method to replace missing value

    col_outlier_fill_method: None or dict of (column name, missing_fill_method) pairs
        specifies method to replace missing value for each column;
        any column not specified will take missing_fill_method,
        if missing_fill_method is None, unspecified column will not be imputed;

    missing_impute : None or dict
        element of list can be any type, or auto generated if value is None, define which values to be consider as missing, default: None
        dict like {column:[value]}

    need_run: bool, default True
        need run or not

    # add by tjx 2022118
    # deal_strategies:int default [1]
    #     异常值处理策略，1 用户直接指定异常值和对应的替换值
    #                     2 用户选择标准差方式处理异常值
    #                     3 用户选择分位数方式处理异常值
    # n_value:int/float default [0]
    #     当deal_strategies=2 n_value=2
    #     当deal_strategies=3 n_value=1.5


    # outlier_by_std float default 1.96
            标准差方式处理异常值 n的值
    # outlier_by_quantile default None，float
            分位数方式处理异常值 n的值

    """

    def __init__(self, default_value=0, outlier_fill_method=None, col_outlier_fill_method=None,
                 missing_impute=None, need_run=True,outlier_by_std=1.96,outlier_by_quantile=None):
        self.default_value = default_value
        self.outlier_fill_method = outlier_fill_method
        self.col_outlier_fill_method = col_outlier_fill_method
        self.missing_impute = missing_impute
        self.need_run = need_run
        self.outlier_by_std = outlier_by_std
        self.outlier_by_quantile = outlier_by_quantile

    def check(self):

        descr = "feature outlier param's "

        self.check_boolean(self.need_run, descr + "need_run")

        # if self.deal_strategies is not None:
        #     for i in self.deal_strategies:
        #         if i not in [1,2,3]:
        #             raise ValueError(f"{descr}deal strategies must be in [1,2,3]")
        # if 2 in self.deal_strategies or 3 in self.deal_strategies:
        #     if self.n_value is None:
        #         raise ValueError(f"{descr} n value can not None")

        if self.outlier_fill_method is not None:
            self.outlier_fill_method = self.check_and_change_lower(self.outlier_fill_method,
                                                                   ['min', 'max', 'mean','median', 'designated'],
                                                                   f"{descr}outlier_fill_method ")
        if self.col_outlier_fill_method:
            if not isinstance(self.col_outlier_fill_method, dict):
                raise ValueError(f"{descr}col_outlier_fill_method should be a dict")
            for k, v in self.col_outlier_fill_method.items():
                if not isinstance(k, str):
                    raise ValueError(f"{descr}col_outlier_fill_method should contain str key(s) only")
                v = self.check_and_change_lower(v,
                                                ['min', 'max', 'mean','median', 'designated'],
                                                f"per column method specified in {descr} col_outlier_fill_method dict")
                self.col_outlier_fill_method[k] = v
        if self.missing_impute:
            if not isinstance(self.missing_impute, dict):
                raise ValueError(f"{descr}missing_impute must be None or dict.")

        return True
