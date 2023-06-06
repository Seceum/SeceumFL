
import abc

import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content
from ..content import FateContent as FC


class Curve(Converter):
    """
    算法组件报告 - 曲线

    TODO: almost the same as roc_curve.Curve
    """

    def __init__(self):
        super(Curve, self).__init__()
        self.fate_curve_contents = []  # 曲线对应的键值
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
    def fate_curves(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def x_name(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def y_name(self):
        raise NotImplementedError()

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.fold = ["fold_0"]
        fl_data.xAxis = {}
        fl_data.yAxis = {}

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_axis()
        self._init_fl_data(fl_data)
        # Handle train data
        self._load_curve_data(fate_data.train, self.fate_train_data)
        self._convert_curve_data(self.fate_train_data)
        # TODO: this is different from roc_curve.Curve
        self._save_axis_data(fl_data)

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
        for name in self.fate_curves:
            # TODO: this is different from roc_curve.Curve
            setattr(target, name, source[name])

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

    @abc.abstractmethod
    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        """
        转换曲线数据
        """
        raise NotImplementedError()


@Converter.bind_loader(LoaderEnum.metric)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.loss_curve)
class LossCurve(Curve):
    """
    算法组件报告 - Loss曲线
    """

    @property
    def fate_curves(self):
        return [
            'loss'
        ]

    @property
    def x_name(self):
        return 'iters'

    @property
    def y_name(self):
        return {
            'loss': True
        }

    def _load_curve_data(self, source, target):
        for name in self.fate_curves:
            setattr(target, name, source[name])

    def _convert_curve_data(self, fate_curve_data, is_validate=False):
        points, thresholds = self._parse_one_curve(fate_curve_data.loss)
        self.x_axis.data = [i for i, _ in points]
        y_axis_data = {
            "fold_0_loss": [loss for _, loss in points]
        }
        self._set_y_axis(y_axis_data, is_validate)
