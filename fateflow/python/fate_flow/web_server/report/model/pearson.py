from ..common import DictObj
from ..converter import Converter
from ..content import Content
from ..consts import CollectorEnum,LoaderEnum
import pandas as pd
import numpy as np


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.pearson)
class Pearson(Converter):
    """
    pearson 报告内容
    TODO pearson 报告待优化 1 基本信息和pearson系数一起返回有问题，暂时框架不支持，2 pearson系数应该是指标之间的两两相关性
    TODO 因此要表示每一个指标的相关性设计上有问题
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        """
        所有特征包括guest,host
        """
        feature_list = []
        features = fate_data.allNames
        for f in features:
            f1 = f["names"]
            feature_list.append(f1)
        """
        guest方和host方特征维度数量
        """
        shapes = fate_data.shapes
        """
        guest方每一个特征和host方每一个特征的pearson矩阵系数 guest shape * host shape
        """
        corr = fate_data.corr
        """
        guest 方每一个特征之间的pearson矩阵系数 guest shape * guest shape
        """
        localCorr = fate_data.localCorr
        """
        guest方每一个特征的vif系数
        """
        localVif = fate_data.localVif

    @property
    def fl_items(self):
        return ["data","header","range"]


    @property
    def fate_items(self):
        return ["allNames","corr","localCorr","localVif","shapes"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data.data = []
        fl_data.header = ["feature", "party", "type", "distribution", "pearson"]
        fl_data.range = {
            "party": ["party_1", "party_2"],
            "type": ["int", "float", "str"],
            "distribution": ["离散", "连续"]
        }
