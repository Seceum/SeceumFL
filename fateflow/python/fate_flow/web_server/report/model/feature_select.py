import typing

from ..common import DictObj
from ..consts import CollectorEnum, LoaderEnum
from ..converter import Converter
from ..content import Content


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.feature_select)
class FeatureSelect(Converter):
    """
    特征选择pearson，ok 前端传过来的是dataset_meta，需要修改为feature_select
    特征选择iv filter ok 前端传过来的是dataset_meta，需要修改为feature_select
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):

        self.__init_fl_data(fl_data)
        # fl_data.data.append([self.block_info.module,None,None,None,self.block_info.module])
        """
        包装法特征选择
        """
        if self.block_info.module in ["HeteroWrapper","HeteroWrapper1","HeteroWrapper2"]:
            data = fate_data.weight
            intercept = fate_data.intercept
            for key in data.keys():
                feature = key
                weight = data[feature]
                fl_data.data.append([feature,None,None,None,round(weight,8)])
            fl_data.data.append(["intercept",None,None,None,round(intercept,8)])


        elif self.block_info.module in ["HeteroPearson","HeteroIVFilter","HeteroVIFFilter","HeteroVarianceFilter",
                                        "HeteroEmbedded","HeteroEmbedded1"]:
            """
            HeteroVarianceFilter 待测试
            pearson，vif,iv,var 特征选择方法
            """
            guestresult = fate_data.results[0]["featureValues"]
            hostresult = fate_data.results[0]["hostFeatureValues"]
            """
            guest 方特征及pearson
            """
            for guestfeature in guestresult.keys():
                feature = guestfeature
                value = guestresult[feature]
                fl_data.data.append([feature,None,None,None,round(value,8)])
            """
            host 方特征及pearson，可能会存在多个host
            """
            for item in hostresult:
                host = item["featureValues"]
                if host:
                    for hostfeature in host.keys():
                        feature = hostfeature
                        value = host[feature]
                        fl_data.data.append([feature,None,None,None,round(value,8)])


            #host方剩余特征 ,可能存在多个host
            hostleftcols = fate_data.results[0]["hostLeftCols"]
            for item in hostleftcols:
                leftcols = item["leftCols"]
                originalCols = item["originalCols"]
                for original in originalCols:
                    if original not in leftcols:
                        fl_data.deletefeature.append(original)
            # guest方剩余特征
            leftcols = fate_data.results[0]["leftCols"]
            originalCols = leftcols["originalCols"]
            guestleftCols = leftcols["leftCols"]
            for original in originalCols:
                if original not in guestleftCols:
                    fl_data.deletefeature.append(original)

        if self.block_info.module == "HeteroPearson":
            fl_data.header = ["feature", "party", "type", "distribution", "pearson"]
        elif self.block_info.module == "HeteroIVFilter":
            fl_data.header = ["feature", "party", "type", "distribution", "iv"]
        elif self.block_info.module == "HeteroVIFFilter":
            fl_data.header = ["feature", "party", "type", "distribution", "vif"]
        elif self.block_info.module in ["HeteroVarianceFilter"]:
            fl_data.header = ["feature", "party", "type", "distribution", "variance"]
        elif self.block_info.module in ["HeteroEmbedded","HeteroEmbedded"]:
            fl_data.header = ["feature", "party", "type", "distribution", "feature_importance"]
        elif self.block_info.module in ["HeteroWrapper","HeteroWrapper1","HeteroWrapper2"]:
            fl_data.header = ["feature", "party", "type", "distribution", "coefficient"]


    @property
    def fl_items(self):
        return ["data","header","range","deletefeature"]

    @property
    def fate_items(self):
        return ["results","featureImportances","featureNameFidMapping","weight","intercept"]

    @staticmethod
    def __init_fl_data(fl_data:DictObj):
        fl_data.header = ["feature", "party", "type", "distribution", "pearson"]
        fl_data.data = []
        fl_data.range = {}
        fl_data.deletefeature=[]
        fl_data.range["party"] = []
        fl_data.range["type"] = []
        fl_data.range["distribution"] = []
