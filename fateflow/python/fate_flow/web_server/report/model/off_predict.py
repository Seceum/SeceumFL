from ..consts import CollectorEnum,LoaderEnum
from ..common import DictObj
from ..converter import Converter
from ..content import Content


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.data)
@Converter.register(Content.off_predict)
class OffPredict(Converter):
    """
    离线预测
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self.__init_fl_data(fl_data)

        d = fate_data.data[0]
        b = open("d1031.json",'w')
        b.write(str(d))
        b.close()
        # fl_data.data = [v[0:5] for v in d]
        for v in d:
            v = v[0:5]
            v[-1] = str(v[-1])
            v[3] = round(v[3],8)
            fl_data.data.append(v)

    @property
    def fl_items(self):
        return ["data","header"]

    @property
    def fate_items(self):
        return ["data"]

    @staticmethod
    def __init_fl_data(fl_data:DictObj):
        fl_data.data = []
        fl_data.header = [f"编号",f"标签",f"预测结果",f"预测分数",f"预测详情"]