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
import collections


class SampleParam(BaseParam):
    """
    Define the sample method

    Parameters
    ----------
    mode: {'random', 'stratified', 'exact_by_weight'}'
        specify sample to use, default: 'random'

    method: {'downsample', 'upsample'}, default: 'downsample'
        specify sample method

    fractions: None or float or list category type
        if mode equals to random, it should be a float number greater than 0,
        otherwise a list of elements of pairs like [label_i, sample_rate_i],
        e.g. [[0, 0.5], [1, 0.8], [2, 0.3]]. default: None

    # add by tjx 202339
    split_points : None or list, default : None continue type
        split_points and fractions one out of two choose
        Specify the point(s) by which continuous label values are bucketed into bins for stratified split.
        eg.[0.2] for two bins or [0.1, 1, 3] for 4 bins

    # add by tjx 202339
    rate:None or list
       连续性变量每一个区间采样比例

    random_state: int, RandomState instance or None, default: None
        random state

    need_run: bool, default True
        Indicate if this module needed to be run
    """

    def __init__(self, mode="random", method="downsample", fractions=None,split_points=None,rate=None,
                 random_state=None, task_type="hetero", need_run=True):
        self.mode = mode
        self.method = method
        self.fractions = fractions
        self.split_points = split_points
        self.rate = rate
        self.random_state = random_state
        self.task_type = task_type
        self.need_run = need_run

    def check(self):
        descr = "sample param"
        self.mode = self.check_and_change_lower(self.mode,
                                                ["random", "stratified", "exact_by_weight"],
                                                descr)

        self.method = self.check_and_change_lower(self.method,
                                                  ["upsample", "downsample"],
                                                  descr)

        if self.mode == "stratified" and self.fractions is not None:
            if not isinstance(self.fractions, list):
                raise ValueError("fractions of sample param when using stratified should be list")
            for ele in self.fractions:
                if not isinstance(ele, collections.Container) or len(ele) != 2:
                    raise ValueError(
                        "element in fractions of sample param using stratified should be a pair like [label_i, rate_i]")
        if self.split_points is not None:
            if not isinstance(self.split_points, list):
                raise ValueError(f"split_points should be list type")
        return True
