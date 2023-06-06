
import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.data)
@Converter.register(Content.scorecard)
class ScoreCard(Converter):
    """
    评分卡报告 后端返回100条数据，前端只返回10条，前端需要排查一下
    """

    @property
    def fate_items(self) -> typing.List[str]:
        return ["data"]

    @property
    def fl_items(self) -> typing.List[str]:
        return ["data","header"]

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        data = fate_data.data[0]
        for d in data:
            d[3]=round(d[3],6)
            fl_data.data.append(d)

    @staticmethod
    def _init_fl_data(fl_data:dict):
        fl_data.data = []
        fl_data.header = ["id","label","predict_result","predict_score","credit_score"]
