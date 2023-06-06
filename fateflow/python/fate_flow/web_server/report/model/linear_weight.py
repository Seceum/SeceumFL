
import typing

from ..common import DictObj, get_model
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.linear_weight)
class LinearWeight(Converter):
    """
    线性权重报告数据转换
    """

    @property
    def fate_items(self) -> typing.List[str]:
        return [
            'header',  # features names
            'intercept',  # bias
            'weight',  # binary classes model
            "needOneVsRest",  # if multi classes
            'oneVsRestResult'  # multi classes model
        ]

    @property
    def fl_items(self) -> typing.List[str]:
        return [
            'header',
            'fold',
            'model',
            'data'
        ]

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        features = fate_data.header
        if fate_data.needOneVsRest:
            self._convert_multi(fl_data, features, fate_data.oneVsRestResult)
        else:
            self._convert_binary(fl_data, features, fate_data.weight, fate_data.intercept)

    @staticmethod
    def _init_fl_data(fl_data: DictObj):
        fl_data.header = ["feature", "weight"]
        fl_data.fold = ['fold_0']  # Fate中交叉验证目前无数据
        fl_data.model = []
        fl_data.data = []

    @staticmethod
    def _convert_binary(fl_data, features, weight, intercept):
        """
        二分类权重数据转换
        """
        fl_data.model = get_model()
        for feature in features:
            fl_data.data.append([feature, round(weight[feature],8),
                                'fold_0', fl_data.model[0]])
        fl_data.data.append(['intercept', round(intercept,8),
                            'fold_0', fl_data.model[0]])

    @staticmethod
    def _convert_multi(fl_data, features, ovr_result):
        """
        多分类权重数据转换
        """
        classes = ovr_result['oneVsRestClasses']
        model_data = ovr_result['completedModels']
        fl_data.model = get_model(classes)
        for i, data in enumerate(model_data):
            weight = data['weight']
            intercept = data['intercept']
            for feature in features:
                fl_data.data.append([feature, round(weight[feature],8),
                                    'fold_0', fl_data.model[i]])
            fl_data.data.append(['intercept', round(intercept,8),
                                'fold_0', fl_data.model[i]])
