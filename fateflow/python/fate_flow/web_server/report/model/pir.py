import typing

from ..consts import CollectorEnum,LoaderEnum
from ..common import DictObj
from ..converter import Converter
from ..content import Content


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.data)
@Converter.register(Content.pir)
class PIR(Converter):
    """
    隐匿查询
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        temp = fate_data.data[0]
        for t in temp:
            fl_data.data.append(t)
        header = ['id' if f=='sid' else f for f in fate_data.meta["header"][0]]
        fl_data.header = header

        # a = open("temp123.txt","w")
        # a.write(str(fl_data.data))
        # a.close()


    @property
    def fl_items(self):
        return ["data","header"]

    @property
    def fate_items(self):
        return ["data","meta"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data.data = []
        fl_data.header = []