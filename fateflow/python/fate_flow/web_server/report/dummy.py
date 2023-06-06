import abc
import typing

from .common import DictObj
from .converter import Converter
from .consts import CollectorEnum, LoaderEnum
from .content import Content
from .component import ComponentContent as CC
from .example.fl_report_data import dataset as dummy_data


Binning = [
    "HeteroQuantile",
    "HeteroBucket",
    "HeteroChi2",
    "HomoQuantile",
    "HomoBucket",
    "HomoChi2",
]


FeatureSelection = [
    "HeteroPearson",
    "HeteroIVFilter",
    "HeteroVIFFilter",
    "HeteroVarianceFilter",
    "HeteroEmbedded",
    "HeteroWrapper",
]


class DummyConverter(Converter):
    """
    用于获取静态报告数据的基类
    """

    def __init__(self):
        super(DummyConverter, self).__init__()
        self.module = None
        self.dummy_data: dict = {}

    def set_block_info(self, block_info):
        """
        覆盖父类方法
        """
        self.block_info = block_info
        self.module = block_info.module

    @property
    def fl_items(self) -> typing.List[str]:
        return list(self.dummy_data.keys())

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self.dummy_data = self.get_dummy_data()
        fl_data.load(self.fl_items, self.dummy_data)

    @abc.abstractmethod
    def get_dummy_data(self) -> dict:
        """
        获取静态报告数据的函数接口
        """
        raise NotImplementedError()


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.dataset_shape)
# class DatasetShape(DummyConverter):
#     """
#     基本信息
#     """
#
#     def get_dummy_data(self) -> dict:
#         if self.module == "Intersection":
#             return dummy_data.dataset_shape_intersection
#         elif self.module in FeatureSelection:
#             return dummy_data.dataset_shape_feature_selection
#         else:
#             return dummy_data.dataset_shape


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.dataset_meta)
# class DatasetMeta(DummyConverter):
#     """
#     元数据信息
#     """
#
#     def get_dummy_data(self) -> dict:
#         if self.module == "OwnerSample":
#             return dummy_data.dataset_meta_owner_sample
#         elif self.module == "PartySample":
#             return dummy_data.dataset_meta_party_sample
#         elif self.module == "Intersection":
#             return dummy_data.dataset_meta_intersection
#         elif self.module == "Union":
#             return dummy_data.dataset_meta_union
#         elif self.module == "HeteroPearson":
#             return dummy_data.dataset_meta_pearson
#         elif self.module == "HeteroIVFilter":
#             return dummy_data.dataset_meta_iv
#         elif self.module == "HeteroVIFFilter":
#             return dummy_data.dataset_meta_vif
#         elif self.module == "HeteroVarianceFilter":
#             return dummy_data.dataset_meta_variance
#         elif self.module == "HeteroEmbedded":
#             return dummy_data.dataset_meta_embedded
#         elif self.module == "HeteroWrapper":
#             return dummy_data.dataset_meta_wrapper
#         else:
#             return dummy_data.dataset_meta


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.dataset_glance)
# class DatasetGlance(DummyConverter):
#     """
#     前100条数据
#     """
#
#     def get_dummy_data(self) -> dict:
#         return dummy_data.dataset_glance


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.statistics)
# class Statistics(DummyConverter):
#     """
#     统计信息
#     """
#
#     def get_dummy_data(self) -> dict:
#         if self.module == "StandardScale":
#             return dummy_data.statistics_standard
#         else:
#             return dummy_data.statistics


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.sample_distribution_chart)
# class SampleDistributionChart(DummyConverter):
#     """
#     样本分布直方图
#     """
#
#     def get_dummy_data(self) -> dict:
#         if self.module in Binning:
#             return dummy_data.sample_distribution_chart_binning
#         else:
#             return dummy_data.sample_distribution_chart


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.sample_distribution_chart_unsampled)
# class SampleDistributionChartUnsampled(DummyConverter):
#     """
#     样本分布直方图(采样前)
#     """
#
#     def get_dummy_data(self) -> dict:
#         return dummy_data.sample_distribution_chart_unsampled


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.feature_box_plot)
# class FeatureBoxPlot(DummyConverter):
#     """
#     特征箱线图
#     """
#
#     def get_dummy_data(self) -> dict:
#         return dummy_data.feature_box_plot


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.binning_info)
# class BinningInfo(DummyConverter):
#     """
#     分箱信息
#     """
#
#     def get_dummy_data(self) -> dict:
#         return dummy_data.binning_info


# @Converter.bind_loader(LoaderEnum.dummy)
# @Converter.bind_collector(CollectorEnum.dummy)
# @Converter.register(Content.binning_detail)
# class BinningDetail(DummyConverter):
#     """
#     分箱详情
#     """
#
#     def get_dummy_data(self) -> dict:
#         return dummy_data.binning_detail
