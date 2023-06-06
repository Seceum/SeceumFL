
import re
import abc

from .consts import LoaderEnum
from .common import BlockInfo
from .content import FateContent


class Loader:

    """
    加载Fate报告数据的基类
    """

    __loaders = {}

    @staticmethod
    @abc.abstractmethod
    def load(command, fate_report_data: dict, block_info: BlockInfo):
        """加载数据的接口函数"""
        raise NotImplementedError()

    @staticmethod
    def register(type_: LoaderEnum):
        """
        用于注册子类的装饰器
        """
        def reg(cls_):
            Loader.__loaders[type_] = cls_
            return cls_
        return reg

    @staticmethod
    def create_loader(type_: LoaderEnum):
        """
        获取子类的工厂方法
        """
        return Loader.__loaders[type_]


@Loader.register(LoaderEnum.dummy)
class DummyLoader(Loader):
    """
    用于Mock数据
    TODO: 报告全部开发完成后应该移除该类
    """

    @staticmethod
    def load(command, fate_report_data: dict, block_info):
        pass


@Loader.register(LoaderEnum.normal)
class NormalLoader(Loader):
    """
    用于加载data、model类型的报告数据
    """

    @staticmethod
    def load(command, fate_report_data: dict, block_info):
        command.fate_data.load(command.converter.fate_items, fate_report_data)


@Loader.register(LoaderEnum.metric)
class MetricLoader(Loader):
    """
    用于加载metric类型的报告数据
    """

    @staticmethod
    def load(command, fate_report_data: dict, block_info):
        namespace = (FateContent.train, FateContent.validate)
        command.fate_data.load(namespace, fate_report_data)


@Loader.register(LoaderEnum.evaluation)
class EvaluationLoader(Loader):
    """
    专用于加载模型评估组件的报告数据
    """

    @staticmethod
    def load(command, fate_report_data: dict, block_info):
        namespace = (FateContent.train, FateContent.validate)
        command.fate_data.load(namespace, fate_report_data)
        any_key = next(iter((command.fate_data.train.keys())))
        block_info.algo_cpt_name = EvaluationLoader._get_algo_cpt_name(any_key)

    @staticmethod
    def _get_algo_cpt_name(item_name):
        """
        根据报告内容中的字段名称，获取算法组件名称，用数字来分割
        e.g. hetero_secure_boost_0_ks_tpr -> hetero_secure_boost_0
        """
        pattern = re.compile(r'\d+')  # search number
        _, idx = pattern.search(item_name).span()  # start index, end index
        return item_name[:idx]
