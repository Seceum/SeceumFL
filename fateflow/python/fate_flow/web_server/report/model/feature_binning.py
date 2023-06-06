from ..consts import CollectorEnum,LoaderEnum
from ..common import DictObj
from ..converter import Converter
from ..content import Content


Hetero_Binning = [
        "HeteroQuantile",
        "HeteroBucket",
        "HeteroChi2",
    ]

Homo_Binning = [
        "HomoQuantile",
        "HomoBucket",
        "HomoChi2"
    ]

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.binning_info)
class BinningInfo(Converter):
    """
    binning info 信息
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        #纵向分箱
        if self.block_info.module in Hetero_Binning:
            self._init_fl_data(fl_data)
            """
            guest方分箱信息 等频分箱ok
            """
            guestbinningresult = fate_data.binningResult["binningResult"]
            for guestdatafeature in guestbinningresult.keys():
                feature = guestdatafeature
                value = guestbinningresult[guestdatafeature]
                binnum = value["binNums"]
                iv = round(value["iv"],8)
                fl_data.data.append([feature,binnum,iv])

            """
            host方分箱信息 host方可能有多个
            """
            hostResults = fate_data.hostResults
            for result in hostResults:
                r = result["binningResult"]
                for hostdatafeature in r.keys():
                    feature = hostdatafeature
                    value = r[feature]
                    binnum = value["binNums"]
                    iv = round(value["iv"],8)
                    fl_data.data.append([feature,binnum,iv])
        elif self.block_info.module in Homo_Binning:
            #横向分箱
            self._init_fl_data(fl_data)
            """
            guest方分箱信息
            """
            guestbinningresult = fate_data.binningResult["binningResult"]
            for guestdatafeature in guestbinningresult.keys():
                feature = guestdatafeature
                value = guestbinningresult[guestdatafeature]
                binnum = len(value["binAnonymous"])
                iv = value["iv"]

                value1 = guestbinningresult[feature]
                splitPoints = value1["splitPoints"]
                """
                分割点区间信息
               """
                binning = []
                for i in range(binnum):
                    if i == 0:
                        binning.append(" ".join([feature, "<=", str(splitPoints[i])]))
                    elif i < binnum - 1:
                        binning.append(" ".join([str(splitPoints[i - 1]), "<", feature, "<=", str(splitPoints[i])]))
                    else:
                        binning.append(" ".join([feature, ">", str(splitPoints[i - 1])]))
                temp = []
                # 同一个feature信息放在一个list中
                for i in range(binnum):
                    temp.append([binning[i]])
                fl_data.data.append([feature,binnum,round(iv,8),temp])
            fl_data.header = ["feature","bin_num","iv","binning"]
            # guestbinningresult = fate_data.binningResult["binningResult"]
            # for guestdatafeature in guestbinningresult.keys():
            #     feature = guestdatafeature
            #     value = guestbinningresult[feature]
            #     binNums = len(value["binAnonymous"])
            #     splitPoints = value["splitPoints"]
            #     """
            #     分割点区间信息
            #     """
            #     binning = []
            #     for i in range(binNums):
            #         if i == 0:
            #             binning.append(" ".join([feature, "<=", str(splitPoints[i])]))
            #         elif i < binNums - 1:
            #             binning.append(" ".join([str(splitPoints[i - 1]), "<", feature, "<=", str(splitPoints[i])]))
            #         else:
            #             binning.append(" ".join([feature, ">", str(splitPoints[i - 1])]))
            #     temp = []
            #     # 同一个feature信息放在一个list中
            #     for i in range(binNums):
            #         temp.append([binning[i]])
            #     fl_data.data.append(temp)
            # fl_data.header = ["binning"]

    @property
    def fate_items(self):
        return ["binningResult","hostResults"]

    @property
    def fl_items(self):
        return ["data","header"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data.data = []
        fl_data.header = ["feature","bin_num","iv"]


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.binning_detail)
class BinningDetail(Converter):
    """
    binning detail 详情
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        #纵向分箱
        if self.block_info.module in Hetero_Binning:
            self._init_fl_data(fl_data)
            """
            guest方分箱详情 等频分箱 ok
            """
            guestbinningresult = fate_data.binningResult["binningResult"]
            for guestdatafeature in guestbinningresult.keys():
                feature = guestdatafeature
                value = guestbinningresult[feature]
                binNums = int(value["binNums"])
                splitPoints = value["splitPoints"]
                """
                分割点区间信息
                """
                binning = []
                for i in range(binNums):
                    if i == 0:
                        binning.append(" ".join([feature,"<=",str(splitPoints[i])]))
                    elif i < binNums-1:
                        binning.append(" ".join([str(splitPoints[i-1]),"<",feature,"<=",str(splitPoints[i])]))
                    else:
                        binning.append(" ".join([feature,">",str(splitPoints[i-1])]))
                ivArray = value["ivArray"]
                woeArray = value["woeArray"]
                eventCountArray = [int(v) for v in value["eventCountArray"]]
                eventRateArray = ["".join([str(round(v*100,8)),"%"]) for v in value["eventRateArray"]]
                nonEventCountArray = [int(v) for v in value["nonEventCountArray"]]
                nonEventRateArray = ["".join([str(round(v*100,8)),"%"]) for v in value["nonEventRateArray"]]
                temp = []
                # 同一个feature信息放在一个list中
                for i in range(binNums):
                    temp.append([binning[i],round(ivArray[i],8),round(woeArray[i],8),eventCountArray[i],eventRateArray[i],nonEventCountArray[i],nonEventRateArray[i]])
                fl_data.data.append(temp)

            """
            host方分箱详情 host方可能有多个
            """
            hostResults = fate_data.hostResults
            for result in hostResults:
                # 其中的一个host
                r = result["binningResult"]
                for hostdatafeature in r.keys():
                    feature = hostdatafeature
                    value = r[feature]
                    binNums = int(value["binNums"])
                    """
                    分割点区间信息
                    """
                    binning = ["_".join(["bin",str(i)]) for i in range(binNums)]
                    ivArray = value["ivArray"]
                    woeArray = value["woeArray"]
                    eventCountArray = [int(v) for v in value["eventCountArray"]]
                    eventRateArray = ["".join([str(round(v*100,8)), "%"]) for v in value["eventRateArray"]]
                    nonEventCountArray = [int(v) for v in value["nonEventCountArray"]]
                    nonEventRateArray = ["".join([str(round(v*100,8)), "%"]) for v in value["nonEventRateArray"]]
                    temp = []
                    #同一个feature信息放在一个list中
                    for i in range(binNums):
                        temp.append([binning[i], round(ivArray[i],8), round(woeArray[i],8), eventCountArray[i], eventRateArray[i],
                                         nonEventCountArray[i], nonEventRateArray[i]])
                    fl_data.data.append(temp)
        # elif self.block_info.module in Homo_Binning:
        #     # 横向分箱
        #     self._init_fl_data(fl_data)
        #     """
        #     guest方分箱子详情
        #     """
        #     guestbinningresult = fate_data.binningResult["binningResult"]
        #     for guestdatafeature in guestbinningresult.keys():
        #         feature = guestdatafeature
        #         value = guestbinningresult[feature]
        #         binNums = len(value["binAnonymous"])
        #         splitPoints = value["splitPoints"]
        #         """
        #         分割点区间信息
        #         """
        #         binning = []
        #         for i in range(binNums):
        #             if i == 0:
        #                 binning.append(" ".join([feature, "<=", str(splitPoints[i])]))
        #             elif i < binNums - 1:
        #                 binning.append(" ".join([str(splitPoints[i - 1]), "<", feature, "<=", str(splitPoints[i])]))
        #             else:
        #                 binning.append(" ".join([feature, ">", str(splitPoints[i - 1])]))
        #         temp = []
        #         # 同一个feature信息放在一个list中
        #         for i in range(binNums):
        #             temp.append([binning[i]])
        #         fl_data.data.append(temp)
        #     fl_data.header = ["binning"]


    @property
    def fate_items(self):
        return ["binningResult","hostResults"]

    @property
    def fl_items(self):
        return ["data","header"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data.data = []
        fl_data.header = ["binning","iv","woe","event_count","event_ratio","non_event_count",
                          "non_event_ratio"]


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.sample_distribution_chart)
class SampleDistributionChart(Converter):

    """
    sample distribution chart 分箱样本分布直方图
    """

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        # 只有纵向分箱才有分布直方图
        if self.block_info.module  in Hetero_Binning:
            self._init_fl_data(fl_data)
            """
            guest方分箱详情 等频分箱 ok
            """
            guestbinningresult = fate_data.binningResult["binningResult"]
            for guestdatafeature in guestbinningresult.keys():
                feature = guestdatafeature
                value = guestbinningresult[feature]
                binNums = int(value["binNums"])
                splitPoints = value["splitPoints"]
                """
                分割点区间信息
                """
                binning = []
                for i in range(binNums):
                    if i == 0:
                        binning.append(" ".join([feature, "<=", str(splitPoints[i])]))
                    elif i < binNums - 1:
                        binning.append(" ".join([str(splitPoints[i - 1]), "<", feature, "<=", str(splitPoints[i])]))
                    else:
                        binning.append(" ".join([feature, ">", str(splitPoints[i - 1])]))
                woeArray = value["woeArray"]
                eventCountArray = [int(v) for v in value["eventCountArray"]]
                nonEventCountArray = [int(v) for v in value["nonEventCountArray"]]
                # 每一个区间对应的样本数量，正样本+负样本
                count = [eventCountArray[i] + nonEventCountArray[i] for i in range(binNums)]
                fl_data.features.append(feature)
                fl_data.xAxis["data"][feature] = binning
                fl_data.yAxis["data"][feature+"_count"] = count
                fl_data.yAxis["data"][feature+"_woe"] = woeArray

            """
            host方分箱详情 host方可能有多个
            """
            hostResults = fate_data.hostResults
            for result in hostResults:
                # 其中的一个host
                r = result["binningResult"]
                for hostdatafeature in r.keys():
                    feature = hostdatafeature
                    value = r[feature]
                    binNums = int(value["binNums"])
                    """
                    分割点区间信息
                    """
                    binning = ["_".join(["bin", str(i)]) for i in range(binNums)]
                    woeArray = value["woeArray"]
                    eventCountArray = [int(v) for v in value["eventCountArray"]]
                    nonEventCountArray = [int(v) for v in value["nonEventCountArray"]]
                    # 每一个区间对应的样本数量，正样本+负样本
                    count = [eventCountArray[i]+nonEventCountArray[i] for i in range(binNums)]
                    fl_data.features.append(feature)
                    fl_data.xAxis["data"][feature] = binning
                    fl_data.yAxis["data"][feature + "_count"] = count
                    fl_data.yAxis["data"][feature + "_woe"] = woeArray



    @property
    def fl_items(self):
        if self.block_info.module in Hetero_Binning:
            return ["features","xAxis","yAxis"]
        # elif self.block_info.module in Homo_Binning:
        #     return []
        else:
            # 其他情况也没有直方图返回
            return []

    @property
    def fate_items(self):
        return ["binningResult","hostResults"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data.features = []
        fl_data.xAxis = {}
        fl_data.yAxis = {}
        fl_data.xAxis["name"]=f"区间"
        fl_data.xAxis["data"] = {}
        fl_data.yAxis["name"] = {}
        fl_data.yAxis["name"]["count"] = "bar"
        fl_data.yAxis["name"]["woe"] = "curve"
        fl_data.yAxis["data"] = {}







