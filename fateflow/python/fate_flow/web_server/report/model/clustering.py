
import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.cluster_detail)
class ClusterDetail(Converter):
    """
    聚类详情报告数据转换
    """

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        for i, cluster_data in enumerate(fate_data.clusterDetail):
            count, ratio = self._get_one_cluster(cluster_data)
            fl_data.data.append([f'Cluster{i}', round(count, 6), round(ratio, 4)])

    @property
    def fate_items(self) -> typing.List[str]:
        return [
            'clusterDetail'
        ]

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'header',  # 列名
            'data'
        ]

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.header = ["cluster_label", "count", "ratio"]
        fl_data.data = []

    @staticmethod
    def _get_one_cluster(cluster_data):
        _, count, ratio = cluster_data['cluster']
        return count, ratio


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.centroid_detail)
class CentroidDetail(Converter):
    """
    聚类中心详情报告数据转换
    """

    def __init__(self):
        super(CentroidDetail, self).__init__()
        self.num = 0
        self.centroids = []

    @property
    def fate_items(self) -> typing.List[str]:
        return [
            "header",  # 特征名称
            "centroidDetail"
        ]

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'header',  # 列名
            'data'
        ]

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        self._get_centroids(fate_data.centroidDetail)
        fl_data.header.extend([f'Cluster{i}' for i in range(self.num)])
        for i, name in enumerate(fate_data.header):
            row = [name, ]
            row.extend([round(self.centroids[j][i], 5) for j in range(self.num)])
            fl_data.data.append(row)

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.header = ["feature"]
        fl_data.data = []

    def _get_centroids(self, centroid_detail):
        self.num = len(centroid_detail)
        self.centroids = [item['centroid'] for item in centroid_detail]
