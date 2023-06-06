"""
报告部分参考了设计模式中的命令模式与策略模式

============
简要的类图如下
============

  + ------------ +      + ------------- +      + --------- +
  | ReportClient | ---> | ReportInvoker | ---> | Collector |
  + ------------ +      + ------------- +      + --------- +
                                |
                                |
                                |      + ------------- +      + ------ +
                                + ---> | ReportCommand | ---> | Loader |
                                       + ------------- +      + ------ +
                                              |
                                              |
                                              |      + --------- +
                                              + ---> | Converter |
                                                     + --------- +

=======
类的职责
=======

ReportClient：创建与组装Invoker、Collector、ReportCommand与Converter对象

ReportInvoker：调用Collector对象及ReportCommand对象，以获取报告数据

ReportCommand：将Loader与Converter对象联系起来，封装了报告数据的生成过程

Collector：从Fate中获取报告数据

Loader：加载从Fate中获取的报告数据

Converter：承担具体的格式转换任务
"""

import typing

from .content import Content
from .consts import CollectorEnum
from .common import DictObj, BlockInfo
from .loader import Loader
from .collector import Collector
from .converter import Converter
from fate_flow.web_server.report.report_utils import *
from fate_flow.web_server.fl_config import config


class ReportCommand:
    """
    对应命令模式中的命令类

    将Loader与Converter对象联系起来，封装了报告数据的生成过程
    """

    def __init__(self, converter: Converter):
        self.fate_data = DictObj()
        self.fl_data = DictObj()
        self.converter: Converter = converter
        self.loader: Loader = self._get_loader()

    def execute(self, fate_report_data: dict, block_info: BlockInfo) -> dict:
        """命令模式的执行接口"""
        self.converter.set_block_info(block_info)
        self.loader.load(self, fate_report_data, block_info)
        self.converter.convert(self.fate_data, self.fl_data)
        return self.dump()

    def dump(self):
        return self.fl_data.dump(self.converter.fl_items)

    @property
    def collector_type(self) -> CollectorEnum:
        return self.converter.collector_type

    def _get_loader(self) -> Loader:
        return Loader.create_loader(self.converter.loader_type)


class ReportInvoker:
    """
    对应命令模式中的调用者类

    调用Collector对象及ReportCommand对象，以获取报告数据
    """

    def __init__(self, collector: Collector):
        self.collector: Collector = collector
        self.commands: typing.Dict[Content, ReportCommand] = {}

    def add_command(self, content: Content, command: ReportCommand):
        self.commands[content] = command

    def get_report_data(self, block_info: BlockInfo) -> list:
        """获取报告数据"""
        if not self.commands:
            return []
        # 获取Fate原始报告数据
        fate_report_data = self.collector.collect(block_info)
        report_data = []
        # 逐项对原始报告数据进行格式转换
        for content, command in self.commands.items():
            report = command.execute(fate_report_data, block_info)
            report_data.append((content, report))
        return report_data


class ReportClient:
    """
    对应命令模式中的客户类

    创建与组装Invoker、Collector、ReportCommand与Converter对象
    """

    __converters: typing.Dict[Content, type] = {}

    def __init__(self, job_id: str, role: str, party_id: int, component_name: str):
        self.job_id: str = job_id
        self.role: str = role
        self.party_id: int = party_id
        self.component_name: str = component_name
        self.block_info = BlockInfo()
        self.invokers = self._init_invokers()

    def set_block_info(self, **kw):
        """设置组件信息"""
        self.block_info.set_info(kw)

    def get_report_data(self, contents: typing.List[str]):
        """获取报告数据"""
        report_data = {}
        contents = self._check_contents(contents)
        # 1. 创建ReportCommand对象，并与Invoker对象关联
        for content in contents:
            command = self._creat_command(content, self.block_info.need_cv)
            invoker = self.invokers[command.collector_type]
            invoker.add_command(content, command)
        # 2. 通过Invoker来获得报告数据
        for invoker in self.invokers.values():
            for content, report in invoker.get_report_data(self.block_info):
                report_data[content.name] = report
        self._add_extra_info(report_data)

        # 保存前面缓存的信息
        # add by tjx 20220913
        save_cache_data(report_data,self.block_info,self.job_id)
        report_data = result_convert(report_data)
        if self.block_info.module in ["Intersection"]:
            return report_data
        # add by tjx 20220728
        """
        获取指标的所属节点，数据类型，分布等三个字段信息
        """
        feature_info = get_feature_info(self.job_id)
        report_data = merge_report_data_info(self.block_info,report_data,feature_info["data"],self.job_id)
        return report_data


    def _init_invokers(self) -> typing.Dict[CollectorEnum, ReportInvoker]:
        """根据报告内容项的类型，初始化Invoker对象"""
        return {type_: self._creat_invoker(type_) for type_ in CollectorEnum}

    @staticmethod
    def _check_contents(contents: typing.List[str]) -> typing.List[Content]:
        """检查content是否被定义
        KeyError异常将由Flask框架承接
        """
        return [Content[name] for name in contents]

    def _creat_invoker(self, type_: CollectorEnum) -> ReportInvoker:
        """创建Collector与Invoker对象的工厂函数"""
        collector = Collector.create_collector(type_, self.job_id, self.role,
                                               self.party_id, self.component_name)
        return ReportInvoker(collector)

    @classmethod
    def _creat_command(cls, content: Content, need_cv: bool) -> ReportCommand:
        """创建Command对象的工厂函数"""
        # 交叉验证报告项添加"_cv"后缀
        if need_cv:
            content_name = content.name + '_cv'
            try:
                content = Content[content_name]
            except KeyError:
                pass  # 该报告内容项无需添加"_cv"后缀
        converter = Converter.create_converter(content)
        return ReportCommand(converter)

    def _add_extra_info(self, report_data: dict) -> dict:
        """
        算法组件及评估组件需要在添加任务类型、交叉验证的信息
        以方便前段通过这些状态调去不同的页面
        """
        if self.block_info.is_evaluation:
            report_data.update({
                'task_type': self.block_info.task_type
            })
        elif self.block_info.is_algorithm:
            report_data.update({
                'need_cv': self.block_info.need_cv,
                'task_type': self.block_info.task_type
            })
        return report_data
