import typing

from ..consts import CollectorEnum,LoaderEnum
from ..common import DictObj
from ..converter import Converter
from ..content import Content
import pandas as pd
import numpy as np
import math

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.data1)
@Converter.register(Content.sample_distribution_chart1)
class SampleDistributionChart1(Converter):
    """
    样本分析报告中样本分布直方图 add by tjx 20220819
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self.__init_fl_data(fl_data)
        temp = fate_data.data["distribution"]

        for key in temp.keys():
            fl_data.data["features"].append(key)
            xAxis = temp[key]["xAxis"]
            yAxis = temp[key]["yAxis"]
            fl_data.data["xAxis"]["data"].update({key:xAxis})
            fl_data.data["yAxis"]["data"].update({key:yAxis})




    @property
    def fate_items(self):
        return ["data"]

    @property
    def fl_items(self):
        return ["data"]

    @staticmethod
    def __init_fl_data(fl_data:DictObj):
        fl_data.data = {}
        fl_data.data["features"]=[]
        fl_data.data["xAxis"]={}
        fl_data.data["xAxis"]["name"]="interval"
        fl_data.data["xAxis"]["data"]={}
        fl_data.data["yAxis"]={}
        fl_data.data["yAxis"]["name"]={}
        # fl_data.data["yAxis"]["name"]["count"]="bar"
        fl_data.data["yAxis"]["name"].update({"count":"bar"})
        fl_data.data["yAxis"]["data"]={}

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.statistics)
class DataStatistics(Converter):

    """
    样本分析报告内容
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        """
        归一化操作/标准化操作 ok
        """
        temp = fate_data.colScaleParam
        temp = None
        if temp:
            featurelist = []
            for key in temp.keys():
                featurelist.append(key)
                value = temp[key]
                min = value["columnLower"]
                max = value["columnUpper"]
                mean = value["mean"]
                std = value["std"]
                # fl_data.data.append([key,None,None,None,None,mean,None,max,min,None,std])
                fl_data.data.append([key,mean,max,min,std])
            fl_data.header = ["feature","mean","max","min","standard_deviation"]
            fl_data.range["feature"] = featurelist


        """
        缺失值组件，后端返回的数据ok，前端页面需要修改
        """
        temp = fate_data.imputerParam
        temp = None
        if temp:
            data2 = pd.DataFrame(columns=["feature","colsReplaceMethod","missingReplaceValue",
                                          "missingReplaceValueType","missingValueRatio","skipCols"])
            colsReplaceMethod = temp["colsReplaceMethod"]
            missingReplaceValue= temp["missingReplaceValue"]
            missingReplaceValueType = temp["missingReplaceValueType"]
            missingValueRatio = temp["missingValueRatio"]
            skipCols = temp["skipCols"]
            features = colsReplaceMethod.keys()
            data2["feature"] = features
            for f in features:
                data2.loc[data2["feature"]==f,"colsReplaceMethod"] = colsReplaceMethod[f]
                if f in missingReplaceValue:
                    data2.loc[data2["feature"]==f,"missingReplaceValue"] = missingReplaceValue[f]
                if f in missingReplaceValueType:
                    data2.loc[data2["feature"]==f,"missingReplaceValueType"] = missingReplaceValueType[f]
                data2.loc[data2["feature"]==f,"missingValueRatio"] = missingValueRatio[f]
                if f in skipCols:
                    data2.loc[data2["feature"]==f,"skipCols"] = True
                else:
                    data2.loc[data2["feature"]==f,"skipCols"] = False
            data2.fillna("-",inplace=True)
            fl_data.data = [d for d in data2.values.tolist()]
            fl_data.header = ["feature","colsReplaceMethod","missingReplaceValue",
                                          "missingReplaceValueType","missingValueRatio","skipCols"]
            fl_data.range["feature"] = list(data2["feature"].unique())

        """
        样本分析报告 ok fate后端可以返回其他的指标
        """

        temp = fate_data.selfValues
        if temp:
            if self.block_info.module in ["StandardScale"]:
                data2 = pd.DataFrame(columns=["feature","party","type","distribution","missing_count","mean","median",
                                          "max","min","sum","standard_deviation","skewness","kurtosis"])
                fl_data.header = ["feature","party","type","distribution","missing_count","mean","median",
                                          "max","min","sum","standard_deviation","skewness","kurtosis"]
            else:
                data2 = pd.DataFrame(
                    columns=["feature", "party", "type", "distribution", "missing_count", "mean", "median",
                             "max", "min", "sum", "standard_deviation"])
                fl_data.header = ["feature", "party", "type", "distribution", "missing_count", "mean", "median",
                                  "max", "min", "sum", "standard_deviation"]
            res = temp["results"]

            for r in res:
                data2["feature"] = r["colNames"]
                valuename = r["valueName"]
                value = r["values"]
                if self.block_info.module in ["StandardScale"]:
                    if valuename in ["coefficient_of_variance","95%","missing_ratio"]:
                        continue
                else:
                    if valuename in ["skewness","kurtosis","coefficient_of_variance","95%","missing_ratio"]:
                        continue
                # update by tjx 20220819
                if valuename != 'stddev':
                    data2[valuename] = [round(v,8) if v not in ['NaN','Infinity',"-Infinity"] and not math.isnan(v) else "-" for v in value]
                elif valuename == "stddev":
                    data2["standard_deviation"] = [round(v,8) if v not in ['NaN','Infinity',"-Infinity"] and not math.isnan(v) else "-" for v in value]

            data2.loc[:,"party"]=["-" for _ in range(len(data2))]
            data2.loc[:,"type"]=["-" for _ in range(len(data2))]
            data2.loc[:,"distribution"]=["-" for _ in range(len(data2))]
            data2.to_csv("2253.csv",index=False)

            fl_data.data = data2.values.tolist()
            fl_data.range["feature"] = list(data2["feature"].unique())

        """
        编码与哑变量
        """
        temp = fate_data.colMap
        temp = None
        if temp:
            featurelist = []
            for k in temp.keys():
                feature = k
                value = temp[feature]
                transformedHeaders = value["transformedHeaders"]
                values = value["values"]
                featurelist.append(feature)
                temp1 = []
                for i in range(len(values)):
                    temp1.append([values[i],transformedHeaders[i]])
                fl_data.data.append(temp1)
            fl_data.header = ["value","encoded_vector"]
            fl_data.range = {}
            fl_data.range["feature"] = featurelist

    @property
    def fate_items(self):
        return ["colScaleParam","selfValues","imputerParam","colMap"]

    @property
    def fl_items(self):
        return ["data","header","range"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data.data = []
        # fl_data.header =["feature", "party", "type", "distribution",
        #            #    缺失数        平均数    中位数    最大值  最小值   求和          标准差
        #            'missing_count', 'mean', 'median', 'max', 'min', 'sum', 'standard_deviation']
        fl_data.header = []
        # 每列取值范围，用于下拉菜单
        fl_data.range ={
            # "feature": ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"],
            "feature":[],
            "party": ["party_1", "party_2"],
            "type": ["int", "float", "str"],
            "distribution": [f"离散", f"连续"],
            "attribute": ["标签", "特征"]
        }

