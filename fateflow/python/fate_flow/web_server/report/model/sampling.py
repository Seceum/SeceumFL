from ..consts import CollectorEnum,LoaderEnum
from ..common import DictObj
from ..converter import Converter
from ..content import Content

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.sample_distribution_chart2)
class SampleDistributionChart2(Converter):
    """
    TODO 前端需要改变key 待完善 sample 组件
    样本分布直方图采样后，这个key sample_distribution_chart2 前端需要改变一下

    """

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        sample_count = fate_data.sample_count
        if sample_count is None:
            return

        feature = []
        count = []
        for key in sample_count.keys():
            value = sample_count[key]
            data = value["data"]

            for d in data:
                y = d[0]
                num = d[1]
                feature.append(y)
                count.append(num)
        fl_data.xAxis["data"]["y"] = feature
        fl_data.yAxis["data"]["y_count"] = count

    @property
    def fl_items(self):
        return ["features", "xAxis", "yAxis"]

    @property
    def fate_items(self):
        return ["sample_count"]

    @staticmethod
    def _init_fl_data(fl_data:dict):
        fl_data.features = ["feature_1", "feature_2"]
        fl_data.xAxis = {}
        fl_data.xAxis["name"] = "interval"
        fl_data.xAxis["data"] = {}
        fl_data.yAxis = {}
        fl_data.yAxis["name"] = {}
        fl_data.yAxis["name"]["count"] = ["bar"]
        fl_data.yAxis["data"] = {}


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.sample_distribution_chart_unsampled)
class SampleDistributionChartUnsampled(Converter):
    """
    样本分布直方图(采样前)

    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        b = open("1004.json",'w')
        b.write(str(fate_data.original_count))
        b.close()
        original_count = fate_data.original_count
        if original_count is None:
            return

        feature = []
        count = []
        for key in original_count.keys():
            value = original_count[key]
            data = value["data"]

            for d in data:
                y = d[0]
                num = d[1]
                feature.append(y)
                count.append(num)
        fl_data.xAxis["data"]["y"] = feature
        fl_data.yAxis["data"]["y_count"] = count


    @property
    def fl_items(self):
        return ["features","xAxis","yAxis"]

    @property
    def fate_items(self):
        return ["original_count"]

    @staticmethod
    def _init_fl_data(fl_data:dict):
        fl_data.features = ["feature_1","feature_2"]
        fl_data.xAxis = {}
        fl_data.xAxis["name"] = "interval"
        fl_data.xAxis["data"] = {}
        fl_data.yAxis = {}
        fl_data.yAxis["name"] = {}
        fl_data.yAxis["name"]["count"] = ["bar"]
        fl_data.yAxis["data"] = {}

