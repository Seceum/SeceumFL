
import abc
import typing

from ..common import DictObj, get_fold
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content
from ..content import FateContent as FC


class CurveCV(Converter):
    """
    模型评估组件报告 - 曲线

    # TODO: abstract all Curve classes
    """

    def __init__(self):
        super(CurveCV, self).__init__()
        self.x_axis = DictObj()  # 横轴数据
        self.y_axis = DictObj()  # 纵轴数据
        self._init_axis()

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'fold',  # 交叉验证
            'xAxis',  # 横轴
            'yAxis'  # 纵轴
        ]

    @property
    @abc.abstractmethod
    def fate_curves(self) -> typing.List[str]:
        # fate中的曲线键值后缀
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def x_name(self) -> str:
        # 横轴变量名称
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def y_name(self) -> dict:
        # 纵轴变量名称
        raise NotImplementedError()

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        fl_data.fold = get_fold(self.block_info.n_split)
        # Handle train data
        self._convert_curve_data(fl_data, fate_data.train)
        # Handle validate data
        if fate_data.validate:
            self._convert_curve_data(fl_data, fate_data.validate, True)
        self._save_axis_data(fl_data)

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.fold = []
        fl_data.xAxis = {}
        fl_data.yAxis = {}

    def _init_axis(self):
        """
        初始化坐标轴信息
        """
        self.x_axis.name = self.x_name
        self.x_axis.data = []
        self.y_axis.name = self.y_name
        self.y_axis.train = {}
        self.y_axis.validate = {}

    def _save_axis_data(self, fl_data: DictObj):
        fl_data.xAxis = self.x_axis.dump(['name', 'data'])
        fl_data.yAxis = self.y_axis.dump(['name', FC.train, FC.validate])

    @staticmethod
    def _gen_curve_full_name(namespace: str, fold: str, curve: str) -> str:
        return f'{namespace}_{fold}_{curve}'

    def _set_y_axis(self, y_axis_data: dict, is_validate: bool):
        if is_validate:
            self.y_axis.validate.update(y_axis_data)
        else:
            self.y_axis.train.update(y_axis_data)

    @staticmethod
    def _parse_one_curve(fate_one_curve: dict) -> (list, list):
        points = fate_one_curve['data']
        thresholds = fate_one_curve['meta'].get('thresholds')
        return points, thresholds

    @abc.abstractmethod
    def _convert_curve_data(self, fl_data, fate_namespace_data, is_validate=False):
        """
        转换曲线数据
        """


@Converter.bind_loader(LoaderEnum.metric)
@Converter.bind_collector(CollectorEnum.cv_metric)
@Converter.register(Content.ks_curve_cv)
class KSCurveCV(CurveCV):
    """
    算法组件报告 - 二分类 - 交叉验证 - Loss曲线
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return [
            FC.ks_tpr,
            FC.ks_fpr
        ]

    @property
    def x_name(self) -> str:
        return 'threshold'

    @property
    def y_name(self) -> dict:
        return {
            "tpr": True,
            "fpr": True,
            "threshold": False,
            "ks": False
        }

    def _convert_curve_data(self, fl_data, fate_namespace_data, is_validate=False):
        namespace = FC.validate if is_validate else FC.train
        for fold in fl_data.fold:
            tpr_full_name = self._gen_curve_full_name(namespace, fold, FC.ks_tpr)
            fpr_full_name = self._gen_curve_full_name(namespace, fold, FC.ks_fpr)
            tpr_data = fate_namespace_data[tpr_full_name]
            fpr_data = fate_namespace_data[fpr_full_name]
            tpr_points, thresholds = self._parse_one_curve(tpr_data)
            fpr_points, _ = self._parse_one_curve(fpr_data)
            if not self.x_axis.data:
                self.x_axis.data = [percentile for percentile, _ in tpr_points]
            tprs = [tpr for _, tpr in tpr_points]
            fprs = [fpr for _, fpr in fpr_points]
            kss = [tpr - fpr for tpr, fpr in zip(tprs, fprs)]
            y_axis_data = {
                f"{fold}_threshold": thresholds,
                f"{fold}_tpr": tprs,
                f"{fold}_fpr": fprs,
                f"{fold}_ks": kss
            }
            self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.metric)
@Converter.bind_collector(CollectorEnum.cv_metric)
@Converter.register(Content.multi_pr_graph_cv)
class MultiPRGraphCV(CurveCV):
    """
    算法组件报告 - 多分类 - 交叉验证 - PR曲线
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return [
            FC.precision,
            FC.recall
        ]

    @property
    def x_name(self) -> str:
        return 'class'

    @property
    def y_name(self) -> dict:
        return {
            "precision": True,
            "recall": True
        }

    def _convert_curve_data(self, fl_data, fate_namespace_data, is_validate=False):
        namespace = FC.validate if is_validate else FC.train
        for fold in fl_data.fold:
            precision_full_name = self._gen_curve_full_name(namespace, fold, FC.precision)
            recall_full_name = self._gen_curve_full_name(namespace, fold, FC.recall)
            precision_data = fate_namespace_data[precision_full_name]
            recall_data = fate_namespace_data[recall_full_name]
            precision_points, thresholds = self._parse_one_curve(precision_data)
            recall_points, _ = self._parse_one_curve(recall_data)
            if not self.x_axis.data:
                self.x_axis.data = [name for name, _ in precision_points]
            y_axis_data = {
                f"{fold}_precision": [precision for _, precision in precision_points],
                f"{fold}_recall": [recall for _, recall in recall_points],
            }
            self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.metric)
@Converter.bind_collector(CollectorEnum.cv_metric)
@Converter.register(Content.loss_curve_cv)
class LossCurveCV(CurveCV):
    """
    算法组件报告 - 交叉验证 - Loss曲线
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return [
            FC.loss
        ]

    @property
    def x_name(self) -> str:
        return 'iters'

    @property
    def y_name(self) -> dict:
        return {
            'loss': True
        }

    @staticmethod
    def _gen_curve_full_name(n: int) -> str:
        return f'{FC.loss}.{n}'

    def _convert_curve_data(self, fl_data, fate_namespace_data, is_validate=False):
        if is_validate:
            return
        for i, fold in enumerate(fl_data.fold):
            full_name = self._gen_curve_full_name(i)
            loss_data = fate_namespace_data[full_name]
            points, thresholds = self._parse_one_curve(loss_data)
            if not self.x_axis.data:
                self.x_axis.data = [i for i, _ in points]
            y_axis_data = {
                f"{fold}_loss": [loss for _, loss in points]
            }
            self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.metric)
@Converter.bind_collector(CollectorEnum.cv_metric)
@Converter.register(Content.metric_iter_curve_cv)
class MetricIterCurveCV(CurveCV):
    """
    Boosting算法组件 - 交叉验证 - 迭代指标图

    包括 二分类 多分类 回归

    TODO: the following shit code thanks to the fucking design
    """

    binary_y_name = {
        "auc": True,
        "ks": True,
    }

    multi_y_name = {
        "precision": True,
        "recall": True,
        "accuracy": True,
    }

    regression_y_name = {
        "mae": True,
        "rmse": True,
    }

    metric_map = {
        FC.mean_absolute_error: 'mae',
        FC.root_mean_squared_error: 'rmse'
    }

    def __init__(self):
        super(MetricIterCurveCV, self).__init__()
        self.iterations: int = 0
        self._fate_curves = []  # this is depend on task type

    @property
    def fate_curves(self) -> typing.List[str]:
        return self._fate_curves

    @property
    def x_name(self) -> str:
        return 'folds'  # TODO: This is different from mock data

    @property
    def y_name(self) -> dict:
        return {}

    @staticmethod
    def _gen_curve_full_name(namespace: str, n: int) -> str:
        return f'{namespace}_{FC.fold}_{n}'

    @staticmethod
    def _parse_one_curve(fate_one_curve: list) -> dict:
        return {name: value for name, value in fate_one_curve}

    def _convert_curve_data(self, fl_data, fate_namespace_data, is_validate=False):
        fl_data.fold = ['fold_0', ]
        self.iterations = self._get_iterations()
        if not self.iterations:
            return
        self.x_axis.data = list(range(self.iterations))
        namespace = FC.validate if is_validate else FC.train
        full_name = self._gen_curve_full_name(namespace, 0)
        one_curve_data = fate_namespace_data[full_name][FC.data]
        values = self._parse_one_curve(one_curve_data)
        if FC.auc in values:
            self._convert_binary(fate_namespace_data, is_validate)
        elif FC.recall in values:
            self._convert_multi(fate_namespace_data, is_validate)
        else:
            self._convert_regression(fate_namespace_data, is_validate)

    def _get_iterations(self):
        return self.block_info.n_split

    def _convert_binary(self, fate_namespace_data, is_validate):
        self.y_axis.name = self.binary_y_name
        namespace = FC.validate if is_validate else FC.train
        aucs = []
        kss = []
        for i in range(self.iterations):
            full_name = self._gen_curve_full_name(namespace, i)
            one_curve_data = fate_namespace_data[full_name][FC.data]
            values = self._parse_one_curve(one_curve_data)
            aucs.append(values[FC.auc])
            kss.append(values[FC.ks])
        y_axis_data = {
            'fold_0_auc': aucs,
            'fold_0_ks': kss
        }
        self._set_y_axis(y_axis_data, is_validate)

    def _convert_multi(self, fate_namespace_data, is_validate):
        self.y_axis.name = self.multi_y_name
        namespace = FC.validate if is_validate else FC.train
        precisions = []
        recalls = []
        accuracies = []
        for i in range(self.iterations):
            full_name = self._gen_curve_full_name(namespace, i)
            one_curve_data = fate_namespace_data[full_name][FC.data]
            values = self._parse_one_curve(one_curve_data)
            precisions.append(values[FC.precision])
            recalls.append(values[FC.recall])
            accuracies.append(values[FC.accuracy])
        y_axis_data = {
            'fold_0_precision': precisions,
            'fold_0_recall': recalls,
            'fold_0_accuracy': accuracies
        }
        self._set_y_axis(y_axis_data, is_validate)

    def _convert_regression(self, fate_namespace_data, is_validate):
        self.y_axis.name = self.regression_y_name
        namespace = FC.validate if is_validate else FC.train
        maes = []
        rmses = []
        for i in range(self.iterations):
            full_name = self._gen_curve_full_name(namespace, i)
            one_curve_data = fate_namespace_data[full_name][FC.data]
            values = self._parse_one_curve(one_curve_data)
            maes.append(values[FC.mean_absolute_error])
            rmses.append(values[FC.root_mean_squared_error])
        y_axis_data = {
            'fold_0_mae': maes,
            'fold_0_rmse': rmses
        }
        self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.metric)
@Converter.bind_collector(CollectorEnum.cv_metric)
@Converter.register(Content.metric_iter_curve)
class MetricIterCurve(MetricIterCurveCV):
    """
    Boosting算法组件 - 迭代指标图

    包括 二分类 多分类 回归

    虽然该图不在交叉验证的页面显示，但是从Fate接口
    获取迭代数据的形式与交叉验证类似，故在此定义
    """

    def _get_iterations(self):
        return self.block_info.n_iter

    @staticmethod
    def _gen_curve_full_name(namespace: str, n: int) -> str:
        """
        This is different
        """
        return f'{FC.iteration}_{n}'
