
import typing

import numpy as np

from fate_arch.abc import CTableABC
from federatedml.feature.instance import Instance
from federatedml.util import LOGGER


class Bundle:
    """
    包含互斥特征信息的特征捆
    """

    def __init__(self, max_conflict: int):
        self.max_conflict: int = max_conflict
        self.conflict: int = 0  # current conflict numbers
        self.indexes: typing.List[int] = []  # index of features
        self.offsets: typing.List[float] = []  # offsets of each feature
        self.maximums: typing.List[float] = []  # maximum of each feature

    def is_valid(self) -> bool:
        """捆中的特征数量大于1时才有价值"""
        return len(self.indexes) > 1

    def can_hold(self, conflict: int) -> bool:
        """捆中能否容纳一个特征"""
        return self.conflict + conflict <= self.max_conflict

    def add_feature(self, idx: int, conflict: int, maximum: float):
        """在捆中加入新特征"""
        if not self.can_hold(conflict):
            return
        self.indexes.append(idx)
        self.conflict += conflict
        self._update_offsets(maximum)

    def _update_offsets(self, maximum: float):
        """
        更新特征的偏移量
        """
        if self.offsets is []:
            # 第一个被添加的特征，其偏移量为0
            self.offsets.append(0)
        else:
            # 当前被添加的特征，其偏移量 = 上一个特征的偏移量 + 上一个特征的最大值
            offset = self.offsets[-1] + self.maximums[-1]
            self.offsets.append(offset)
        self.maximums.append(maximum)


class EFB(object):
    """
    互斥特征绑定 (Exclusive Feature Bundling)

    接口设计参考了sk-learn的fit()与transform()

    纵向联邦:
        参与方分别对本地的特征进行互斥绑定，以近似全局的互斥绑定
    """

    def __init__(self, categorical_features):
        self.categorical_features: typing.List[str] = categorical_features  # names of categorical features
        self.features: typing.List[str] = []  # names of all features in order
        self.categorical_indexes: typing.List[int] = []  # indexes of categorical features
        self.frozen_indexes: typing.List[int] = []  # indexes of features that need nothing to do
        self.bundles: typing.List[Bundle] = []
        self.maximums: typing.List[float] = []  # maximums of each feature
        self.max_conflict: int = 0
        self.output_schema: dict = {}  # schema of data table after EFB process

    def fit(self, data_inst: CTableABC):
        """
        构建互斥特征捆
        """
        self.features = self._get_features(data_inst)
        self.categorical_indexes = [self.features.index(name) for name in self.categorical_features]
        self._init_max_conflict(data_inst)
        self.maximums, non_zeros = self._run_statistics(data_inst)
        self._search_bundles(non_zeros)
        self.output_schema = self._gen_new_schema(data_inst)

    def _init_max_conflict(self, data_inst: CTableABC):
        """设定最大冲突数量"""
        # TODO: Why?
        self.max_conflict = data_inst.count() // 2  # 样本数量的一半

    @staticmethod
    def _run_statistics(data_inst: CTableABC):
        """获取样本的统计量"""
        table = data_inst.mapValues(lambda instance: instance.features)
        return EFB._cal_maximums(table), EFB._cal_non_zeros(table)

    @staticmethod
    def _cal_maximums(table: CTableABC) -> np.ndarray:
        """计算每个特征的最大值"""
        return table.reduce(lambda x, y: np.max([x, y], axis=0))

    @staticmethod
    def _cal_non_zeros(table: CTableABC) -> np.ndarray:
        """计算每个特征的非零样本数"""
        table = table.mapValues(lambda x: np.where(x != 0, 1, 0))
        return table.reduce(lambda x, y: x + y)

    def _search_bundles(self, non_zeros: np.ndarray):
        """
        搜索互斥特征，建立特征捆

        通过非零值数量近似判断特征是否互斥，非零值越大，冲突越大
        """
        self.bundles = []
        self.frozen_indexes = []
        bundle = Bundle(self.max_conflict)
        self.bundles.append(bundle)
        # 根据非零值数量，从小到大排序
        for idx in np.argsort(non_zeros):
            non_zero_count = non_zeros[idx]
            # 跳过离散型特征与独占一捆的特征
            if idx in self.categorical_indexes or \
                    non_zero_count >= self.max_conflict:
                self.frozen_indexes.append(idx)
                continue
            # 特征捆已满时，需要创建新的捆
            if not bundle.can_hold(non_zero_count):
                bundle = Bundle(self.max_conflict)
                self.bundles.append(bundle)
            # 将特征加入捆中
            bundle.add_feature(idx, non_zero_count, self.maximums[idx])
        # 去除无价值的特征捆
        self.bundles = [bundle for bundle in self.bundles if bundle.is_valid()]
        self.frozen_indexes.sort()

    @staticmethod
    def _get_features(data_inst: CTableABC) -> list:
        """
        schema: {
            "header": list[str]
            "sid_name": str,
            "label_name": str
        }
        """
        return data_inst.schema['header']

    def _gen_bundle_name(self, bundle: Bundle) -> str:
        """根据捆内特征名称，生成新特征名称"""
        features = [self.features[i] for i in bundle.indexes]
        return 'efb#}' + '_'.join(features)

    def _gen_new_features(self) -> typing.List[str]:
        """生成绑定后的所有特征名称"""
        features = [self.features[i] for i in self.frozen_indexes]
        bundle_names = [self._gen_bundle_name(bundle) for bundle in self.bundles]
        features.extend(bundle_names)
        return features

    def _gen_new_schema(self, data_inst: CTableABC) -> dict:
        """生成特征绑定后的表的描述信息"""
        schema = data_inst.schema.copy()
        schema['header'] = self._gen_new_features()
        return schema

    def transform(self, data_inst: CTableABC) -> CTableABC:
        """合并互斥特征"""
        new_data_inst = data_inst.mapValues(self._transform_one_inst)
        new_data_inst.schema = self.output_schema.copy()
        return new_data_inst

    @staticmethod
    def _bind_one_bundle(data: np.ndarray, bundle: Bundle):
        """将一个特征捆对应的特征数据进行合并"""
        # TODO: 有溢出的风险
        data = data[bundle.indexes]  # 1D ndarray
        offsets = np.array(bundle.offsets)
        return np.sum(data + offsets)  # a float number

    def _transform_one_inst(self, inst: Instance) -> Instance:
        """对一条样本数据进行特征绑定"""
        data = inst.features  # 1D ndarray
        new_data = list(data[self.frozen_indexes])
        new_feature_data = [self._bind_one_bundle(data, bundle) for bundle in self.bundles]
        new_data.extend(new_feature_data)
        inst.features = np.array(new_data)
        return inst
