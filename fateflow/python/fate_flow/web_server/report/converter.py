
import abc
import typing

from .common import DictObj, BlockInfo
from .content import Content
from .consts import LoaderEnum, CollectorEnum


class Converter:
    """
    转换报告数据的基类

    对应命令模式中的接收者类
    """

    LoaderType: LoaderEnum = None
    CollectorType: CollectorEnum = None

    __converters = {}

    def __init__(self):
        self.block_info: BlockInfo = None

    def set_block_info(self, block_info: BlockInfo):
        self.block_info = block_info

    @abc.abstractmethod
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        """
        转换报告数据的接口函数
        """
        raise NotImplementedError()

    @property
    def fate_items(self) -> typing.List[str]:
        """
        Fate报告数据中的字段
        """
        return []

    @property
    @abc.abstractmethod
    def fl_items(self) -> typing.List[str]:
        """
        FL报告数据中的字段
        """
        raise NotImplementedError()

    @staticmethod
    def bind_loader(type_: LoaderEnum):
        """用于绑定Loader类的装饰器"""
        def bind_conv(cls_):
            cls_.LoaderType = type_
            return cls_
        return bind_conv

    @property
    def loader_type(self) -> LoaderEnum:
        return self.LoaderType

    @staticmethod
    def bind_collector(type_: CollectorEnum):
        """用于定义Collector类的装饰器"""
        def def_type(cls_):
            cls_.CollectorType = type_
            return cls_
        return def_type

    @property
    def collector_type(self) -> CollectorEnum:
        return self.CollectorType

    @staticmethod
    def register(content: Content):
        """用于注册Converter子类的装饰器"""
        def reg(cls_):
            Converter.__converters[content] = cls_
            return cls_
        return reg

    @staticmethod
    def create_converter(content: Content):
        """
        创建Converter对象的工厂类
        """
        cls_ = Converter.__converters[content]
        return cls_()
