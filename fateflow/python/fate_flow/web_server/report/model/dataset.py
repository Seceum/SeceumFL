import typing

from ..consts import CollectorEnum,LoaderEnum
from ..common import DictObj
from ..converter import Converter
from ..content import Content
from fate_flow.utils.log_utils import getLogger
datasetlogger = getLogger()
import numpy as np
from fate_flow.web_server.fl_config import config

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.data)
@Converter.register(Content.dataset_glance)
class DatasetGlance(Converter):
    """
    前100条数据
    """

    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        fl_data.data = fate_data.data[0]
        fl_data.header = fate_data.meta["header"][0]
        fl_data.total = fate_data.meta["total"][0]
        fl_data.feature = len([f for f in fl_data.header if f != 'id' and f != 'y'])


    @property
    def fate_items(self):
        return ["data","meta"]

    @property
    def fl_items(self):
        return ["header","data","total","feature"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data.data = []

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.db_data3)
@Converter.register(Content.dataset_meta_fusion)
class DatasetMetaFusion(Converter):
    """
    融合样本元数据信息
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self.__init_fl_data(fl_data)
        # dataset_meta = fate_data.data
        # fl_data.data.append([dataset_meta,1,1,1,1,1])
        import json
        b = json.dumps(fate_data.data)
        f2 = open("1703add.json", "w")
        f2.write(b)
        f2.close()

        p_id = []
        att = []
        dist = []
        t = []
        # if "feature_info" not in fate_data.data :
        #     fl_data.data.append([None,None,None,None,None,None])
        #     fl_data.range["party"] = []
        #     fl_data.range["attribute"] = []
        #     fl_data.range["distribution"] =[]
        #     fl_data.range["type"] = []
        #     return

        # dataset_meta = fate_data.data["feature_info"]["data"]
        dataset_meta = fate_data.data
        for f in dataset_meta:
            attribute = f["data_type"]
            if attribute == "ID" or attribute == "Y":
                continue
            feature = f["field_name"]
            type = f["field_type"]
            t.append(type)
            party_id = f"本地节点" if f["party_id"]==config.local_party_id else f["party_id"]
            p_id.append(party_id)
            distribution = f["distribution_type"]
            dist.append(distribution)

            att.append(attribute)
            desc = f["field_description"]
            if self.block_info.module not in ["Union"]:
                fl_data.data.append([feature,party_id,type,distribution,attribute,desc])
            else:
                fl_data.data.append([feature, type, distribution, attribute, desc])
        # add by tjx 2022819
        fl_data.range["party"] = list(set(p_id))
        fl_data.range["attribute"] = list(set(att))
        fl_data.range["distribution"] = list(set(dist))
        fl_data.range["type"] = list(set(t))
        if self.block_info.module not in ["Union"]:
            fl_data.header = ["feature", "party", "type", "distribution", "attribute", "description"]
        else:
            fl_data.header = ["feature", "type", "distribution", "attribute", "description"]

    @property
    def fl_items(self):
        return ["data","header","range"]


    @property
    def fate_items(self):
        return ["data"]


    @staticmethod
    def __init_fl_data(fl_data:DictObj):
        fl_data.data = []

        fl_data.header = ["feature", "party","type", "distribution", "attribute", "description"]
        fl_data.range = {"attribute": ["标签", "特征"],
                         "distribution": ["离散", "连续"],
                         "type": ["int", "float", "str", "bool"],
                         "party":["party1","party2"]}

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.db_data2)
@Converter.register(Content.dataset_meta_sample)
class DatasetMetaSample(Converter):
    """
    样本meta数据转换
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self.__init_fl_data(fl_data)
        feature_infos = fate_data.data["feature_info"]
        for f in feature_infos:
            feature = f["field_name"]
            type = f["field_type"]
            distribution = f["distribution_type"]
            attribute = f["data_type"]
            desc = f["field_description"]
            fl_data.data.append([feature,type,distribution,attribute,desc])


    @property
    def fl_items(self):
        return ["data","header","range"]

    @property
    def fate_items(self):
        return ["data"]

    @staticmethod
    def __init_fl_data(fl_data:DictObj):
        fl_data.data = []
        fl_data.header = ["feature","type","distribution","attribute","description"]
        fl_data.range = {"attribute": ["标签", "特征"],
                         "distribution": ["离散", "连续"],
                         "type": ["int", "float", "str", "bool"]}

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.db_data)
@Converter.register(Content.dataset_meta)
class DatasetMeta(Converter):
    """
    样本融合报告meta数据转换
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        party_id_list = []
        self._init_fl_data(fl_data)
        for d in fate_data.data:
            feature = d["field_name"]
            type = d["field_type"]
            party_id = d["party_id"]
            party_id_list.append(party_id)
            distribution = d["distribution_type"]
            attribute = d["data_type"]
            descri = d["field_description"]
            sample = d["field_examples"]
            # feature = 0
            # type = None
            # party_id = None
            # distribution = None
            # attribute = None
            # descri = None
            # sample = None
            if self.block_info.module == "OwnerSample" :
                fl_data.data.append([feature,type,distribution,attribute,descri,sample])
            elif self.block_info.module == "Intersection" or self.block_info.module == "FusionSample":
                fl_data.data.append([feature,party_id,type, distribution, attribute, descri, sample])

        if self.block_info.module == "OwnerSample" :
            fl_data.header = ["feature","type", "distribution", "attribute", "description", "sample"]
        if self.block_info.module == "Intersection" or self.block_info.module == "FusionSample":
            fl_data.range["party"] = np.unique(party_id_list).tolist()

    @property
    def fate_items(self):
        return ["data"]


    @property
    def fl_items(self):
        return ["data","header","range"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data.data = []
        fl_data.header = ["feature","party","type","distribution","attribute","description","sample"]
        fl_data.range = {"attribute":["标签","特征"],
                         "distribution":["离散","连续"],
                         "type":["int","float","str","bool"]}

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.dataset_shape_wrapper)
class DatasetShapeFeatureSelectWrapper(Converter):
    """
    特征选择包装法 data shape基本信息 wrapper_lr,wrapper_linr,wrapper_poisson
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self.__init_fl_data(fl_data)
        item_len = len(fate_data.train)
        meta = fate_data.train["stepwise_"+str(item_len-1)]["meta"]
        guestallfeature = meta["all_features"]
        guest_mask = meta["guest_mask"]
        hostallfeature = meta["host_features_anonym"]
        host_mask = meta["host_mask"]
        n_count = meta["n_count"]
        fl_data.sample = n_count
        fl_data.feature = len(guestallfeature) + len(hostallfeature)
        reducefeature = 0
        for i in guest_mask:
            if i == False:
                reducefeature = reducefeature + 1
        for i in host_mask:
            if i == False:
                reducefeature = reducefeature + 1
        fl_data.reducefeature = reducefeature


    @property
    def fate_items(self):
        return ["train"]

    @property
    def fl_items(self):
        return {"feature": None, "sample": None, "reducefeature": None}

    @staticmethod
    def __init_fl_data(fl_data:DictObj):
        fl_data = {}
        fl_data["feature"] = None
        fl_data["sample"] = None
        fl_data["reducefeature"] = None


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.dataset_shape_feature_select)
class DatasetShapeFeatureSelect(Converter):
    """

    Content.dataset_shape_pearson,Content.dataset_shape_iv,Content.dataset_shape_vif,
                     Content.dataset_shape_variance,Content.dataset_shape_embedded_xgboost,
                     Content.dataset_shape_embedded_lightgbm
    """
    """
    特征选择pearson基本信息
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        if self.block_info.module in ["HeteroPearson", "HeteroIVFilter", "HeteroVIFFilter",
                                      "HeteroVarianceFilter","HeteroEmbedded","HeteroEmbedded1"]:
            leftCols = fate_data.results[0]["leftCols"]
            leftColsnum = len(leftCols["leftCols"])
            originnum = len(leftCols["originalCols"])
            fl_data.feature = originnum
            fl_data.reducefeature = originnum - leftColsnum
            """
            样本数量从哪里来？待优化
            """
            fl_data.sample = None




    @property
    def fl_items(self):
        return {"feature": None, "sample": None,"reducefeature":None}

    @property
    def fate_items(self):
        return ["results","finalLeftCols","featureImportances", "featureNameFidMapping", "weight", "intercept"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data = {}
        fl_data["feature"] = None
        fl_data["sample"] = None
        fl_data["reducefeature"] = None


@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.model)
@Converter.register(Content.dataset_shape_data_preprocess)
class DatasetShapeDataPreprocess(Converter):
    """
    register不能用list
    Content.dataset_shape_fill_missing,Content.dataset_shape_outlier,Content.dataset_shape_standard,Content.dataset_shape_minmax,
                     Content.dataset_shape_onehot,Content.dataset_shape_sampling,Content.dataset_shape_statistics
    """
    """
    缺失值组件基本信息
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        """
        TODO sample样本数量怎么拿？待优化
        """
        temp = fate_data.selfValues
        if temp:
            res = temp["results"]
            # fl_data["feature"] = len(res)
            fl_data.feature = len(res)
            fl_data.sample = 0

    @property
    def fl_items(self):
        return {"feature": None, "sample": None}

    @property
    def fate_items(self):
        return ["selfValues"]

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data = {}
        fl_data["feature"] = None
        fl_data["sample"] = None

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.db_data3)
@Converter.register(Content.fusion_info)
class FusionInfo(Converter):
    """
    融合样本融合信息
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self.__init_fl_data(fl_data)
        fusion_info = fate_data.data["fusion_info"]
        for item in fusion_info:
            # key = item.keys()
            # value = item.values()
            fl_data.data.append(item)

    @property
    def fate_items(self):
        return ["data"]

    @property
    def fl_items(self):
        return ["data","header"]

    @staticmethod
    def __init_fl_data(fl_data:DictObj):
        fl_data.data = []
        # fl_data.data = [{"party_name":None,"sample_name":None}]
        fl_data.header = ["party_name","sample_name"]

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.db_data3)
@Converter.register(Content.dataset_shape_fusion)
class DatasetShapeFusion(Converter):
    """
    融合样本基本信息
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self.__init_fl_data(fl_data)
        base_info = fate_data.data["base_info"]
        count = base_info["sample_count"]
        feature = base_info["feature_count"]
        fl_data.feature = feature
        fl_data.count = count

    @property
    def fate_items(self):
        return ["data"]

    @property
    def fl_items(self):
        return {"feature":None,"count":None}

    @staticmethod
    def __init_fl_data(fl_data:DictObj):
        fl_data = {}
        fl_data["feature"] = None
        fl_data["count"] = None

@Converter.bind_loader(LoaderEnum.normal)
@Converter.bind_collector(CollectorEnum.db_data2)
@Converter.register(Content.dataset_shape_sample)
class DatasetShapeSample(Converter):
    """
    样本基本信息
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        base_info = fate_data.data["base_info"]
        sample_count = base_info["sample_count"]
        party = base_info["party_name"]
        feature = base_info["feature_count"]
        describe = base_info["comments"]
        fl_data.party = party
        fl_data.feature = feature
        fl_data.count = sample_count
        fl_data.describe = describe


    @property
    def fate_items(self):
        return ["data"]

    @property
    def fl_items(self):
        return {"party":None,"feature":None,"count":None,"describe":None}

    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data = {}
        fl_data["party"] = None
        fl_data["feature"] = None
        fl_data["count"] = None
        fl_data["describe"] = None

@Converter.bind_loader(LoaderEnum.metric)
@Converter.bind_collector(CollectorEnum.metric)
@Converter.register(Content.dataset_shape)
class DatasetShape(Converter):
    """
    样本融合报告shape信息转换
    """
    def convert(self, fate_data: DictObj, fl_data: DictObj):
        self._init_fl_data(fl_data)
        #样本融合基本信息
        if self.block_info.module == "Intersection":
            intersect_data = fate_data.train["intersection"]["data"]
            fl_data.match = intersect_data[1][1]
            fl_data.sample = intersect_data[0][1]
            fl_data.feature = None
        else:
            fl_data.match = None
            fl_data.sample = None
            fl_data.feature = None

    @property
    def fate_items(self):
        return ["train"]

    @property
    def fl_items(self):
        return {"feature":None,"match":None,"sample":None}
    
    @staticmethod
    def _init_fl_data(fl_data:DictObj):
        fl_data = {}
        fl_data["feature"] = None
        fl_data["match"] = None
        fl_data["sample"] = None


