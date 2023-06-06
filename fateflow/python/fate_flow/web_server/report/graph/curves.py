
import abc
import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content
from ..content import FateContent as FC


class Curve(Converter):
    """
    模型评估组件报告 - 曲线
    """

    def __init__(self):
        super(Curve, self).__init__()
        self.fate_curve_contents = []  # 曲线对应的键值 TODO: no use yet?
        self.fate_train_data = DictObj()  # 训练集数据
        self.fate_validate_data = DictObj()  # 验证集数据
        self.x_axis = DictObj()  # 横轴数据
        self.y_axis = DictObj()  # 纵轴数据

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
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def x_name(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def y_name(self) -> dict:
        raise NotImplementedError()

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_axis()
        self._init_fl_data(fl_data)
        # Handle train data
        self._load_curve_data(fate_data.train,
                              self.fate_train_data)
        self._convert_curve_data(self.fate_train_data)
        # Handle validate data
        if fate_data.validate:
            self._load_curve_data(fate_data.validate,
                                  self.fate_validate_data)
            # self._convert_curve_data(self.fate_train_data, True)
            # add by tjx 20220927
            self._convert_curve_data(self.fate_validate_data,True)
        self._save_axis_data(fl_data)

    @abc.abstractmethod
    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        """
        转换曲线数据
        """
        raise NotImplementedError()

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.fold = ['fold_0']
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

    def _load_curve_data(self, source, target):
        ml_component = self.block_info.algo_cpt_name
        for name in self.fate_curves:
            fate_curve_name = '_'.join((ml_component, name))
            setattr(target, name, source[fate_curve_name])

    def _set_y_axis(self, y_axis_data: dict, is_validate: bool):
        if is_validate:
            self.y_axis.validate = y_axis_data
        else:
            self.y_axis.train = y_axis_data

    @staticmethod
    def _parse_one_curve(fate_one_curve: dict) -> (list, list):
        points = fate_one_curve['data']
        thresholds = fate_one_curve['meta'].get('thresholds')
        return points, thresholds


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.ks_curve)
class KSCurve(Curve):
    """
    模型评估组件报告 - 二分类 - KS曲线
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return [
            'ks_fpr',
            'ks_tpr'
        ]

    @property
    def x_name(self):
        return 'threshold'

    @property
    def y_name(self) -> dict:
        return {
            "tpr": True,  # True代表绘制该曲线，同时鼠标悬停时要显示
            "fpr": True,
            "threshold": False,  # False代表不绘制该曲线，但是鼠标悬停时要显示
            "ks": False
        }

    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        tpr_points, thresholds = self._parse_one_curve(fate_curve_data.ks_tpr)
        fpr_points, _ = self._parse_one_curve(fate_curve_data.ks_fpr)
        self.x_axis.data = [percentile for percentile, _ in tpr_points]
        tprs = [tpr for _, tpr in tpr_points]
        fprs = [fpr for _, fpr in fpr_points]
        kss = [tpr - fpr for tpr, fpr in zip(tprs, fprs)]
        y_axis_data = {
            "fold_0_threshold": thresholds,
            "fold_0_tpr": tprs,
            "fold_0_fpr": fprs,
            "fold_0_ks": kss
        }
        self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.roc_curve)
class ROCCurve(Curve):
    """
    模型评估组件报告 - 二分类 - ROC曲线
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return ['roc']

    @property
    def x_name(self) -> str:
        return 'fpr'

    @property
    def y_name(self) -> dict:
        return {
            "threshold": False,
            "tpr": True
        }

    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        points, thresholds = self._parse_one_curve(fate_curve_data.roc)
        self.x_axis.data = [fpr for fpr, _ in points]
        y_axis_data = {
            "fold_0_threshold": thresholds,
            "fold_0_tpr": [tpr for _, tpr in points]
        }
        self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.pr_curve)
class PRCurve(Curve):
    """
    模型评估组件报告 - 二分类 - PR曲线
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return [
            'precision',
            'recall'
        ]

    @property
    def x_name(self) -> str:
        return 'recall'

    @property
    def y_name(self) -> dict:
        return {
            "threshold": False,
            "precision": True
        }

    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        recall_points, thresholds = self._parse_one_curve(fate_curve_data.recall)
        precision_points, _ = self._parse_one_curve(fate_curve_data.precision)
        self.x_axis.data = [recall for _, recall in recall_points]
        y_axis_data = {
            "fold_0_threshold": thresholds,
            "fold_0_precision": [precision for _, precision in precision_points]
        }
        self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.accuracy_curve)
class AccuracyCurve(Curve):
    """
    模型评估组件报告 - 二分类 - Accuracy曲线
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return [
            'accuracy'
        ]

    @property
    def x_name(self) -> str:
        return 'threshold'

    @property
    def y_name(self) -> dict:
        return {
            "threshold": False,
            "accuracy": True
        }

    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        # TODO: almost the same as ROCCurve
        points, thresholds = self._parse_one_curve(fate_curve_data.accuracy)
        self.x_axis.data = [percentile for percentile, _ in points]
        y_axis_data = {
            "fold_0_threshold": thresholds,
            "fold_0_accuracy": [acc for _, acc in points]
        }
        self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.lift_graph)
class LiftGraph(Curve):
    """
    模型评估组件报告 - 二分类 - Lift图
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return [
            'lift'
        ]

    @property
    def x_name(self) -> str:
        return 'threshold'

    @property
    def y_name(self) -> dict:
        return {
            "threshold": False,
            "lift": True
        }

    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        # TODO: almost the same as ROCCurve
        points, thresholds = self._parse_one_curve(fate_curve_data.lift)
        self.x_axis.data = [percentile for percentile, _ in points]
        y_axis_data = {
            "fold_0_threshold": thresholds,
            "fold_0_lift": [lift for _, lift in points]
        }
        self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.gain_graph)
class GainGraph(Curve):
    """
    模型评估组件报告 - 二分类 - Gain图
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return ['gain']

    @property
    def x_name(self) -> str:
        return 'threshold'

    @property
    def y_name(self) -> dict:
        return {
            "threshold": False,
            "gain": True
        }

    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        # TODO: almost the same as ROCCurve
        points, thresholds = self._parse_one_curve(fate_curve_data.gain)
        self.x_axis.data = [percentile for percentile, _ in points]
        y_axis_data = {
            "fold_0_threshold": thresholds,
            "fold_0_gain": [gain for _, gain in points]
        }
        self._set_y_axis(y_axis_data, is_validate)


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.multi_pr_graph)
class MultiPRGraph(Curve):
    """
    模型评估组件报告 - 多分类 - PR图
    """

    @property
    def fate_curves(self) -> typing.List[str]:
        return [
            'precision',
            'recall'
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

    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        precision_points, thresholds = self._parse_one_curve(fate_curve_data.precision)
        recall_points, _ = self._parse_one_curve(fate_curve_data.recall)
        self.x_axis.data = [name for name, _ in precision_points]
        y_axis_data = {
            "fold_0_precision": [precision for _, precision in precision_points],
            "fold_0_recall": [recall for _, recall in recall_points],
        }
        self._set_y_axis(y_axis_data, is_validate)
