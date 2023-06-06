
import abc
import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content


class Metric(Converter):
    """
    模型评估组件报告 - 评估指标 基类
    """

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'header',
            'data'
        ]

    @property
    @abc.abstractmethod
    def fate_metrics(self) -> typing.List[str]:
        # metrics from fate in order
        # defined in federatedml.util.consts
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def fl_metrics(self) -> typing.List[str]:
        # metrics for fate in order
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def metric_map(self) -> typing.Dict[str, str]:
        # map metric name from fl to fate
        raise NotImplementedError()

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        ml_component = self.block_info.algo_cpt_name
        # metric_data = fate_data.train[ml_component]['data']
        # add by tjx 20220927
        metric_data = fate_data.validate[ml_component]["data"]
        metric_data = {name: value for name, value in metric_data}
        for name in self.fl_metrics:
            if name in self.metric_map:
                name = self.metric_map[name]
            fl_data.data.append(metric_data.get(name))

    def _init_fl_data(self, fl_data: DictObj):
        fl_data.header = self.fl_metrics
        fl_data.data = []


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.binary_metric)
class BinaryMetric(Metric):
    """
    模型评估组件报告 - 二分类 - 评估指标
    """

    @property
    def fate_metrics(self) -> typing.List[str]:
        return [
            'auc',
            'ks',
        ]

    @property
    def fl_metrics(self) -> typing.List[str]:
        return [
            'AUC',
            'KS',
            # TODO: where to get the following metrics?
            'Lift',
            'Precision',
            'Recall',
            'F1 Score',
            'Accuracy'
        ]

    @property
    def metric_map(self) -> typing.Dict[str, str]:
        return {
            'AUC': 'auc',
            'KS': 'ks'
        }


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.multi_metric)
class MultiMetric(Metric):
    """
    模型评估组件报告 - 多分类 - 评估指标
    """

    @property
    def fate_metrics(self) -> typing.List[str]:
        return [
            "accuracy",
            "precision",
            "recall",
        ]

    @property
    def fl_metrics(self) -> typing.List[str]:
        return [
            "Precision",
            "Recall",
            "Accuracy",
        ]

    @property
    def metric_map(self) -> typing.Dict[str, str]:
        return {
            'Precision': 'precision',
            'Recall': 'recall',
            'Accuracy': 'accuracy'
        }


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.regression_metric)
class RegressionMetric(Metric):
    """
    模型评估组件报告 - 回归 - 评估指标
    """

    @property
    def fate_metrics(self) -> typing.List[str]:
        return [
            "explained_variance",
            "mean_absolute_error",
            "mean_squared_error",
            "median_absolute_error",
            "r2_score",
            "root_mean_squared_error",
        ]

    @property
    def fl_metrics(self) -> typing.List[str]:
        return [
            "Explained Variance",
            "MAE",
            "MSE",
            "MedAE",
            "R2 Score",
            "RMSE"
        ]

    @property
    def metric_map(self) -> typing.Dict[str, str]:
        return {
            "Explained Variance": "explained_variance",
            "MAE": "mean_absolute_error",
            "MSE": "mean_squared_error",
            "MedAE": "median_absolute_error",
            "R2 Score": "r2_score",
            "RMSE": "root_mean_squared_error"
        }


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.clustering_metric)
class ClusteringMetric(Metric):
    """
    模型评估组件报告 - 聚类 - 评估指标
    """

    @property
    def fate_metrics(self) -> typing.List[str]:
        return [
            "adjusted_rand_score",
            "fowlkes_mallows_score",
            "jaccard_similarity_score",
        ]

    @property
    def fl_metrics(self) -> typing.List[str]:
        return [
            'JC',
            'FMI',
            'RI',
            'Distance Measure'
        ]

    @property
    def metric_map(self) -> typing.Dict[str, str]:
        return {
            'JC': 'jaccard_similarity_score',
            'FMI': 'fowlkes_mallows_score',
            'RI': 'adjusted_rand_score',
        }
