import json
from fate_flow.web_server.fl_config import config
import peewee
from fate_flow.web_server.blocks import BlockParser

from fate_flow.web_server.db_service.job_service import JobContentService
from .common import  BlockInfo
from fate_flow.web_server.utils.sample_util import get_fusion_fields
from fate_flow.web_server.db_service.project_service import ProjectCanvasService,ProjectUsedSampleService
from fate_flow.web_server.db_service.sample_service import SampleFieldsService, SampleService, VSampleInfoService
import pandas as pd
from fate_flow.web_server.fl_config import config
from fate_flow.utils.api_utils import federated_api, local_api
import os

def get_sample_count(job_id):
    dir = "/data/"
    path = dir + job_id + ".json"
    # 求交的时候已经保存过，之前读取前面的文件数据
    if os.path.exists(path):
        d = json.load(open(path,'r'))
        if "sample" in d.keys():
            return d["sample"]
        else:
            pass
    else:
        pass


    """基于job_id找到对应的样本数据"""
    content_obj = ProjectUsedSampleService.get_or_none(job_id=job_id)
    sample_id = content_obj.sample_id
    sample_cols = [SampleService.model.id.alias("sample_id"), SampleService.model.name.alias("sample_name"),
                       SampleService.model.party_name, SampleService.model.sample_type,
                       SampleService.model.sample_count,
                       SampleService.model.comments]
    sample_objs = SampleService.query(id=sample_id, cols=sample_cols)

    data = {
            "base_info": {},
            "feature_info": {},
            "fusion_info": {}
    }
    feature_cols = [SampleFieldsService.model.id, SampleFieldsService.model.sample_id,
                        SampleFieldsService.model.field_name,
                        SampleFieldsService.model.field_type, SampleFieldsService.model.distribution_type,
                        SampleFieldsService.model.data_type, SampleFieldsService.model.field_description]
    data["base_info"] = sample_objs[0].to_dict()
    feature_info = list(SampleFieldsService.query(sample_id=sample_id, cols=feature_cols).dicts())
    data["base_info"]["feature_count"] = len(list(filter(lambda x: x["data_type"] == "特征", feature_info)))

    count = data["base_info"]["sample_count"]

    #保存样本记录数
    if not os.path.exists(dir):
        os.makedirs(dir)
    path = dir + job_id + ".json"
    if not os.path.exists(path):
        b = open(path, 'w')
        b.write(json.dumps({"sample": count}))
        b.close()
    else:
        originalinfo = json.load(open(path,'r'))
        originalinfo.update({"sample":count})
        b = open(path,'w')
        b.write(json.dumps(originalinfo))
        b.close()
    return count

# 保存缓存数据，方便后面报告数据加载，guest只能保存自己的
def save_cache_data(report_data,block_info,job_id):
    dir = "/data/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    # 保存求交后的融合样本数 add by tjx 20220912
    if block_info.module in ["Intersection"]:
        path = dir + job_id + ".json"
        if not os.path.exists(path):
            sample = report_data["dataset_shape"]["sample"]
            b = open(path, 'w')
            b.write(json.dumps({"sample": sample}))
            b.close()

    # 存在采样统计数据，提前进行保存
    path = dir+"samplerinfo.json"
    if os.path.exists(path):
        # 存在其他的数据
        if os.path.exists(dir + job_id + ".json"):
            originalinfo = json.load(open(dir + job_id + ".json",'r'))
            samplerinfo = json.load(open(path,'r'))
            originalinfo.update(samplerinfo)
            b = open(dir + job_id + ".json",'w')
            b.write(json.dumps(originalinfo))
            b.close()
        else:
            samplerinfo = json.load(open(path, 'r'))
            b = open(dir + job_id + ".json", 'w')
            b.write(json.dumps(samplerinfo))
            b.close()
    path = dir+"onehotencode.json"
    if os.path.exists(path):
        if os.path.exists(dir + job_id + ".json"):
            originalinfo = json.load(open(dir + job_id + ".json",'r'))
            onehotencode = json.load(open(path,'r'))
            originalinfo.update({"distribution":onehotencode})
            b = open(dir + job_id + ".json",'w')
            b.write(json.dumps(originalinfo))
            b.close()
        else:
            onehotencode = json.load(open(path, 'r'))
            b = open(dir + job_id + ".json", 'w')
            b.write(json.dumps({"distribution":onehotencode}))
            b.close()

"""
合并data report 和info信息
"""
def merge_report_data_info(block_info:BlockInfo,report_data,feature_info,job_id=None):
    feature_info = pd.DataFrame(feature_info)
    feature_info.to_csv("/data/1738.csv",index=False)
    if block_info.module in ["FillMissing","StandardScale","MinMaxScale",
                             "Sampling","HeteroOneHotEncoder","Statistics","FillOutlier"]:
        for i in range(len(report_data["statistics"]["data"])):
            feature = report_data["statistics"]["data"][i][0]
            party_id = feature_info.loc[feature_info["field_name"]==feature,"party_id"].values[0] \
                if len(feature_info.loc[feature_info["field_name"]==feature,"party_id"])>0 else None
            if party_id:
                report_data["statistics"]["data"][i][1] = f"本地节点" if party_id == config.local_party_id else party_id
                report_data["statistics"]["data"][i][2] = \
                feature_info.loc[feature_info["field_name"] == feature, "field_type"].values[0] if len(
                    feature_info.loc[feature_info["field_name"] == feature, "field_type"]) > 0 else None

                report_data["statistics"]["data"][i][3] = \
                feature_info.loc[feature_info["field_name"] == feature, "distribution_type"].values[0] if len(
                    feature_info.loc[feature_info["field_name"] == feature, "distribution_type"]) > 0 else None

            elif party_id is None:
                if feature.find("_")>=0:
                    feature = feature.split("_")[0]
                    party_id = feature_info.loc[feature_info["field_name"] == feature, "party_id"].values[0] \
                        if len(feature_info.loc[feature_info["field_name"] == feature, "party_id"]) > 0 else None
                    report_data["statistics"]["data"][i][1] = f"本地节点" if party_id == config.local_party_id else party_id
                    report_data["statistics"]["data"][i][2] = feature_info.loc[feature_info["field_name"]==feature,"field_type"].values[0] if len(feature_info.loc[feature_info["field_name"]==feature,"field_type"])>0 else None

                    report_data["statistics"]["data"][i][3] = f'离散型'

        report_data["dataset_shape_data_preprocess"].update({"feature":len(set([data[0] for data in report_data["statistics"]["data"] if data[0]]))})
        report_data["statistics"]["range"].update({"party":set([data[1] for data in report_data["statistics"]["data"] if data[1]])})
        # report_data["statistics"]["range"].update({"attribute":["标签","特征"]})
        report_data["statistics"]["range"].update({"distribution":set([data[3] for data in report_data["statistics"]["data"] if data[3]])})
        report_data["statistics"]["range"].update({"type":set([data[2] for data in report_data["statistics"]["data"] if data[2]])})
        count = get_sample_count(job_id)
        report_data["dataset_shape_data_preprocess"].update({"sample":count})
        if block_info.module == "HeteroOneHotEncoder":
            dir = "/data/"
            path = dir +job_id +".json"
            distribution = json.load(open(path,'r'))
            report_data["distribution"] = distribution["distribution"]

        if block_info.module == "Sampling":
            dir = "/data/"
            path = dir + job_id + ".json"
            samplerdata = json.load(open(path,'r'))
            feature = samplerdata["label_name"]
            unsamplelabelx = samplerdata["unsamplelabel"]["xAxis"]
            unsamplelabely = samplerdata["unsamplelabel"]["yAxis"]
            samplelabelx = samplerdata["samplelabel"]["xAxis"]
            samplelabely = samplerdata["samplelabel"]["yAxis"]
            report_data["sample_distribution_chart_unsampled"]["features"]=[feature]
            report_data["sample_distribution_chart_unsampled"]["xAxis"]["data"]=unsamplelabelx
            report_data["sample_distribution_chart_unsampled"]["yAxis"]["data"]=unsamplelabely
            report_data["sample_distribution_chart2"]["features"]=[feature]
            report_data["sample_distribution_chart2"]["xAxis"]["data"]=samplelabelx
            report_data["sample_distribution_chart2"]["yAxis"]["data"]=samplelabely



    elif block_info.module in ["HeteroPearson","HeteroIVFilter","HeteroVIFFilter","HeteroVarianceFilter",
                               "HeteroEmbedded","HeteroEmbedded1",
                             "HeteroWrapper","HeteroWrapper1","HeteroWrapper2"]:
        for i in range(len(report_data["feature_select"]["data"])):
            feature = report_data["feature_select"]["data"][i][0]
            party_id = feature_info.loc[feature_info["field_name"] == feature, "party_id"].values[0] if \
                len(feature_info.loc[feature_info["field_name"] == feature, "party_id"])>0 else None

            report_data["feature_select"]["data"][i][1] = f"本地节点" if party_id == config.local_party_id else party_id
            if feature.find("_")>=0:
                report_data["feature_select"]["data"][i][1] = feature.split("_")[1]
            report_data["feature_select"]["data"][i][2] = feature_info.loc[feature_info["field_name"] == feature, "field_type"].values[0] if len(feature_info.loc[feature_info["field_name"] == feature, "field_type"])>0 else None
            report_data["feature_select"]["data"][i][3] = feature_info.loc[feature_info["field_name"] == feature, "distribution_type"].values[0] if len(feature_info.loc[feature_info["field_name"] == feature, "distribution_type"])>0 else None

        report_data["feature_select"]["range"]["party"]=set([data[1] for data in report_data["feature_select"]["data"] if data[1]])
        report_data["feature_select"]["range"]["type"] = set([data[2] for data in report_data["feature_select"]["data"] if data[2]])
        report_data["feature_select"]["range"]["distribution"] = set([data[3] for data in report_data["feature_select"]["data"] if data[3]])

        count = get_sample_count(job_id)
        if "dataset_shape_feature_select" in report_data.keys():

            report_data["dataset_shape_feature_select"].update({"sample": count})
        if block_info.module in ["HeteroWrapper","HeteroWrapper1","HeteroWrapper2"]:
            data = report_data["feature_select"]["data"]
            f = 0
            for d in data:
                if d[1]=="本地节点":
                    f = f+1
            report_data["dataset_shape_wrapper"]["feature"]=f
    elif block_info.module in ["Union"]:
        count = 0
        for v in report_data["dataset_meta_fusion"]["data"]:
            if v[3]=="特征":
                count = count + 1
        report_data["dataset_shape"].update({"feature":count})
        count = get_sample_count(job_id)
        report_data["dataset_shape"].update({"sample":count})

    return report_data


"""
获取指标所属节点，分布类型，数据属性三个字段信息 ok
"""
def get_feature_info(job_id):
    content_obj = ProjectUsedSampleService.get_or_none(job_id=job_id)
    sample_id = content_obj.sample_id
    # 元数据信息
    data = {
        "base_info": {},
        "feature_info": {},
        "fusion_info": {}
    }
    feature_cols = [SampleFieldsService.model.id, SampleFieldsService.model.sample_id,
                    SampleFieldsService.model.field_name,
                    SampleFieldsService.model.field_type, SampleFieldsService.model.distribution_type,
                    SampleFieldsService.model.data_type, SampleFieldsService.model.field_description]
    sample_cols = [SampleService.model.id.alias("sample_id"), SampleService.model.name.alias("sample_name"),
                   SampleService.model.party_name, SampleService.model.sample_type,
                   SampleService.model.sample_count,
                   SampleService.model.comments]
    sample_objs = SampleService.query(id=sample_id, cols=sample_cols)
    if not sample_objs:
        temp1 = {"data": {"job_id": job_id, "sample_id": sample_id, "len": len(sample_cols)}}
    data["base_info"] = sample_objs[0].to_dict()
    feature_info1 = list(SampleFieldsService.query(sample_id=sample_id, cols=feature_cols).dicts())
    for i in range(len(feature_info1)):
        feature_info1[i]["party_id"] = config.local_party_id

    # # 融合后的特征列表 只有保存了融合样本才有此信息
    sample_cols = [VSampleInfoService.model.id.alias("sample_id"), VSampleInfoService.model.v_name.alias(
        "sample_name"), VSampleInfoService.model.party_info, VSampleInfoService.model.mix_type]
    # update by tjx 20220818
    v_sample_objs = VSampleInfoService.query(job_id=job_id, cols=sample_cols)
    # v_sample_objs = VSampleInfoService.query(id=sample_id, cols=sample_cols)
    if not v_sample_objs:
        # 如果没有融合返回本方特征信息
        return {"data":feature_info1}
    v_sample_obj = v_sample_objs[0]
    party_info = v_sample_obj.party_info
    feature_info = get_fusion_fields(party_info, v_sample_obj.mix_type)
    return {"data":feature_info}

"""
将返回的结果中部分数据进行转换处理
"""
def result_convert(report_data):
    """
    查看样本信息报告 dataset_shape信息提取
    后面可能需要优化处理
    :param report_data:
    :return:

    """
    if "binary_metric" in report_data.keys() and "confusion_matrix" in report_data.keys():
        """
        补充lift，precision,recalld等指标
        """
        confusion_matrix = report_data["confusion_matrix"]["data"]
        tp = confusion_matrix[0][1]
        fn = confusion_matrix[0][2]
        fp = confusion_matrix[1][1]
        tn = confusion_matrix[1][2]
        accuracy = (tp+tn)/(tp+fn+fp+tn)
        precision = tp/(tp+fp)
        recall = tp/(tp+fn)
        f1_score = 2*precision*recall/(precision+recall)
        lift = max(report_data["lift_graph"]["yAxis"]["validate"]["fold_0_lift"])
        # ks = max(report_data["ks_curve"]["yAxis"]["validate"]["fold_0_ks"])
        binary_metric = report_data["binary_metric"]
        data = binary_metric["data"]
        # data[1] = round(ks,8)
        data[2] = round(lift,8)
        data[3] = round(precision,8)
        data[4] = round(recall,8)
        data[5] = round(f1_score,8)
        data[6] = round(accuracy,8)
        report_data["binary_metric"].update({"data":data})

    if "metric_iter_curve" in report_data.keys():
        metric_iter_curve = report_data["metric_iter_curve"]
        yAxis = metric_iter_curve["yAxis"]
        range = {}
        range["fold"] = metric_iter_curve["fold"]
        type = []
        for k in yAxis.keys():
            if k == "train" or k=="validate":
                type.append(k)
        range["type"]=type
        range["label"] = []
        report_data["metric_iter_curve"].update({"range":range})


    if "ks_curve" in report_data.keys():
        ks_curve = report_data["ks_curve"]
        d = ks_curve["yAxis"].keys()
        range = []
        for d1 in d:
            if d1=="train" or d1=="validate":
                range.append(d1)
        report_data["ks_curve"].update({"range":range})

    if "trees" in report_data.keys():
        need_cv = report_data["need_cv"]
        task_type = report_data["task_type"]
        report_data["trees"].update({"need_cv":need_cv})
        report_data["trees"].update({"task_type":task_type})

    if "dataset_shape" in report_data.keys() and "dataset_meta" in report_data.keys() and "dataset_glance" in report_data.keys()\
            and len(report_data.keys())==3:
        """
        此种情况为查看样本信息报告，dataset_shape信息提取,
        后面待优化
        """
        dataset_glance = report_data["dataset_glance"]
        total = dataset_glance["total"]
        feature = dataset_glance["feature"]
        report_data["dataset_shape"]["feature"]=feature
        report_data["dataset_shape"]["sample"]= total
    elif "dataset_shape" in report_data.keys() and "dataset_meta_fusion" in report_data.keys() and len(report_data.keys())==2:
        """
        此种情况为样本融合报告 dataset_shape信息提取
        后面待优化
        """
        local_party_id = config.local_party_id
        dataset_meta = report_data["dataset_meta_fusion"]["data"]
        feature = 0
        for v in dataset_meta:
            if len(v)==6 and v[4]=='特征' :
                feature = feature + 1
            elif len(v)==5 and v[3] =="特征":
                feature = feature + 1
        report_data["dataset_shape"]["feature"] = feature

    return report_data