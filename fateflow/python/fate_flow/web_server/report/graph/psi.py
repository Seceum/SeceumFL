
import abc
import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content
from ..content import FateContent as FC


class PSI(Converter):
    """
    模型评估组件报告 - PSI图表 基类
    """

    fate_psi_contents = [
        'intervals',
        'actual_percentage',
        'expected_percentage',
        'psi_scores'
    ]

    def __init__(self):
        super(PSI, self).__init__()
        self.fate_psi_data = DictObj()

    @staticmethod
    @abc.abstractmethod
    def _init_fl_data(fl_data: DictObj):
        raise NotImplementedError()

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        # PSI data only in fate validate data
        self._init_fl_data(fl_data)
        if fate_data.validate:
            self._load_psi_data(fate_data)
            self._convert_psi_data(fl_data)

    def _load_psi_data(self, fate_data):
        ml_component = self.block_info.algo_cpt_name
        full_psi_name = '_'.join((ml_component, FC.psi))
        if full_psi_name in fate_data.validate:
            fate_psi_data = fate_data.validate[full_psi_name]['meta']
        else:
            fate_psi_data = {}
        self.fate_psi_data.load(self.fate_psi_contents, fate_psi_data)

    @abc.abstractmethod
    def _convert_psi_data(self, fl_data: DictObj):
        """
        转换PSI数据
        """
        raise NotImplementedError()


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.psi_chart)
class PSIChart(PSI):
    """
    模型评估组件报告 - PSI图
    # TODO: 与曲线部分有重复代码
    """

    def __init__(self):
        super(PSIChart, self).__init__()
        self.x_axis = DictObj()  # 横轴数据
        self.y_axis = DictObj()  # 纵轴数据
        self._init_axis()

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'features',  # 特征
            'xAxis',  # 横轴
            'yAxis'  # 纵轴
        ]

    @property
    def x_name(self):
        return 'interval'

    @property
    def y_name(self):
        return {
            "expected": "bar",  # 条形
            "actual": "bar",
            'psi': 'curve'  # 曲线
        }

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.features = ['y']
        fl_data.xAxis = {}
        fl_data.yAxis = {}

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        super(PSIChart, self).convert(fate_data, fl_data)
        self._save_axis_data(fl_data)

    def _init_axis(self):
        """
        初始化坐标轴信息
        """
        self.x_axis.name = self.x_name
        self.x_axis.data = {}
        self.y_axis.name = self.y_name
        self.y_axis.data = {}

    def _save_axis_data(self, fl_data: DictObj):
        fl_data.xAxis = self.x_axis.dump(['name', 'data'])
        fl_data.yAxis = self.y_axis.dump(['name', 'data'])

    def _convert_psi_data(self, fl_data: DictObj):
        self._convert_x_axis()
        self._convert_y_axis()

    def _convert_x_axis(self):
        self.x_axis.data = {
            'y': self.fate_psi_data.intervals
        }

    def _convert_y_axis(self):
        self.y_axis.data = {
            "y_actual": self.fate_psi_data.actual_percentage,
            "y_expected": self.fate_psi_data.expected_percentage,
            "y_psi": self.fate_psi_data.psi_scores
        }


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.psi_detail)
class PSIDetail(PSI):
    """
    模型评估组件报告 - PSI表格
    """

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'header',  # 列名
            'label',  # TODO: remove this?
            'y'
        ]

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.header = ["interval", "actual", "expected", "psi"]
        fl_data.label = ['y']
        fl_data.y = []

    def _convert_psi_data(self, fl_data: DictObj):
        if not self.fate_psi_data.psi_scores:
            return None
        rows = zip(
            self.fate_psi_data.intervals,
            self.fate_psi_data.actual_percentage,
            self.fate_psi_data.expected_percentage,
            self.fate_psi_data.psi_scores
        )
        fl_data.y = [row for row in rows]
