
import abc
import typing

from ..common import DictObj, get_fold
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content
from ..content import FateContent as FC


class MetricCV(Converter):
    """
    算法组件报告 - 交叉验证- 评估指标 基类
    """

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'fold',  # 交叉验证
            'metric',  # 评估指标
            'data'
        ]

    @property
    @abc.abstractmethod
    def fate_metrics(self) -> typing.List[str]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def fl_metrics(self) -> typing.List[str]:
        raise NotImplementedError()

    def _init_fl_data(self, fl_data: DictObj):
        fl_data.fold = []
        fl_data.metric = self.fl_metrics
        fl_data.data = []

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        fl_data.fold = get_fold(self.block_info.n_split)
        train_metric_data = self._get_metric_data(fl_data, FC.train, fate_data.train)
        self._add_metric_data(fl_data, FC.train, train_metric_data)
        if fate_data.validate:
            validate_metric_data = self._get_metric_data(fl_data, FC.validate, fate_data.validate)
            self._add_metric_data(fl_data, FC.validate, validate_metric_data)

    @staticmethod
    def _get_metric_data(fl_data: DictObj, namespace: str, namespace_data: dict) -> list:
        metric_data = []
        for fold in fl_data.fold:
            content = f'{namespace}_{fold}'
            metrics = namespace_data[content][FC.data]
            metric_data.append({name: value for name, value in metrics})
        return metric_data

    def _add_metric_data(self, fl_data: DictObj, namespace: str, metric_data: list):
        for i, fold in enumerate(fl_data.fold):
            values = [metric_data[i][name] for name in self.fl_metrics]
            values.extend([namespace, fold])
            fl_data.data.append(values)


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.cv_metric)
@Converter.register(Content.binary_metric_cv)
class BinaryMetricCV(MetricCV):
    """
    算法组件报告 - 二分类 - 交叉验证- 评估指标
    """

    @property
    def fate_metrics(self) -> typing.List[str]:
        return [
            FC.auc,
            FC.ks,
        ]

    @property
    def fl_metrics(self) -> typing.List[str]:
        return self.fate_metrics


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.cv_metric)
@Converter.register(Content.multi_metric_cv)
class MultiMetricCV(MetricCV):
    """
    算法组件报告 - 多分类 - 交叉验证- 评估指标
    """

    @property
    def fate_metrics(self) -> typing.List[str]:
        return [
            FC.accuracy,
            FC.precision,
            FC.recall,
        ]

    @property
    def fl_metrics(self) -> typing.List[str]:
        return [
            FC.precision,
            FC.recall,
            FC.accuracy,
        ]


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.cv_metric)
@Converter.register(Content.regression_metric_cv)
class RegressionMetricCV(MetricCV):
    """
    算法组件报告 - 回归 - 交叉验证- 评估指标
    """

    @property
    def fate_metrics(self) -> typing.List[str]:
        return [
            FC.mean_absolute_error,
            FC.root_mean_squared_error
        ]

    @property
    def fl_metrics(self) -> typing.List[str]:
        return self.fate_metrics
