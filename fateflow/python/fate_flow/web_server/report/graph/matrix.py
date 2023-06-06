
import abc
import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content


class Matrix(Converter):
    """
    模型评估组件报告 - 矩阵
    """

    def __init__(self):
        super(Matrix, self).__init__()
        self.full_mat_name = ''
        self.fate_mat_train_data = DictObj()  # 训练集数据
        self.fate_mat_validate_data = DictObj()  # 验证集数据

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'header',  # 列名
            'data'  # 表格行数据
        ]

    @property
    def fate_matrix(self) -> str:
        # 矩阵在Fate报告数据中的名称
        raise NotImplementedError()

    @property
    def fate_elements(self) -> typing.List[str]:
        # 矩阵中对应的元素名称
        raise NotImplementedError()

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        ml_component = self.block_info.algo_cpt_name
        self.full_mat_name = '_'.join((ml_component, self.fate_matrix))

        # add by tjx 20220923
        # if fate_data.validate:
        validate_mat_data = self._get_mat_data(fate_data.validate)
        self.fate_mat_validate_data.load(self.fate_elements,validate_mat_data)
        self._convert_matrix(self.fate_mat_validate_data,fl_data)
        # if fate_data.validate is None and fate_data.train:
        # train_mat_data = self._get_mat_data(fate_data.train)
        # self.fate_mat_train_data.load(self.fate_elements, train_mat_data)
        # self._convert_matrix(self.fate_mat_train_data, fl_data)
        # TODO: how to deal with validate data?

    @abc.abstractmethod
    def _convert_matrix(self, fate_mat_data: DictObj, fl_data: DictObj):
        """
        转换矩阵数据
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def _init_fl_data(fl_data: DictObj):
        raise NotImplementedError()

    def _get_mat_data(self, fate_namespace_data: dict) -> dict:
        return fate_namespace_data[self.full_mat_name]['meta']


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.confusion_matrix)
class ConfusionMatrix(Matrix):
    """
    模型评估组件报告 - 二分类 - 混淆矩阵
    """

    @property
    def fate_matrix(self) -> str:
        return 'confusion_mat'

    @property
    def fate_elements(self) -> typing.List[str]:
        return [
            'tp',
            'tn',
            'fp',
            'fn'
        ]

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.header = [f'正', f'负']
        fl_data.data = []

    def _convert_matrix(self, fate_mat_data: DictObj, fl_data: DictObj):
        idx = self._get_threshold_index()

        fl_data.data = [
            [f'正', fate_mat_data.tp[idx], fate_mat_data.fn[idx]],
            [f'负', fate_mat_data.fp[idx], fate_mat_data.tn[idx]]
        ]

    def _get_threshold_index(self):
        # TODO: 根据算法组件的threshold参数，找到对应的索引

        # return len(self.fate_mat_train_data.tp) // 2  # 假装对应threshold=0.5
        # b = open("/data/fatematvalidatedata.txt",'w')
        # b.write(str(self.fate_mat_validate_data.keys()))
        # b.close()
        # if self.fate_mat_validate_data and self.fate_mat_validate_data.tp:
        return len(self.fate_mat_validate_data.tp)//2
        # else:
        # return len(self.fate_mat_train_data.tp)//2


@Converter.bind_loader(LoaderEnum.evaluation)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.contingency_matrix)
class ContingencyMatrix(Matrix):
    """
    模型评估组件报告 - 聚类 - 列联矩阵
    """

    @property
    def fate_matrix(self) -> str:
        return 'contingency_matrix'

    @property
    def fate_elements(self) -> typing.List[str]:
        return [
            'predicted_labels',  # 预测类别
            'true_labels',  # 真实类别
            "result_table",  # 矩阵元素数据
        ]

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.header = []
        fl_data.data = []

    def _convert_matrix(self, fate_mat_data: DictObj, fl_data: DictObj):
        fl_data.header = [str(label) for label in fate_mat_data.predicted_labels]
        for i, label in enumerate(fate_mat_data.true_labels):
            item = [str(label), ]
            item.extend(fate_mat_data.result_table[i])
            fl_data.data.append(item)
