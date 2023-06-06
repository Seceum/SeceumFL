
import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.feature_importance)
class FeatureImportance(Converter):
    """
    特征重要性报告数据转换
    """

    @property
    def fate_items(self) -> typing.List[str]:
        return ['featureImportances']

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'header',
            'data',
            "range"
        ]

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        if not fate_data.featureImportances:
            return
        temp = []
        for item in fate_data.featureImportances:
            temp.append(item["sitename"])
            fl_data.data.append([
                item['fullname'],  # feature
                round(item['importance'],8),  # split
                round(item['importance2'],8),  # gain
                item['sitename'],  # sitename
            ])
        fl_data.range.update({"sitename":set(temp)})

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.header = ["feature", "split", "gain", "sitename"]
        fl_data.data = []
        fl_data.range={
            "sitename":[]
        }
