
import random

from .content import Content
import pandas as pd
import math
from fate_flow.web_server.fl_config import config

# 样本信息报告内容项（执行任务前查看）
SampleInfoContent = [
    Content.dataset_shape.name,
    Content.dataset_glance.name,
    Content.dataset_meta.name,
]

# 样本信息报告数据（执行任务前查看）
SampleInfoDetail = {
    Content.dataset_shape.name: {},
    Content.dataset_glance.name: {},
    Content.dataset_meta.name: {},
}


def gen_random_categorical_statistics():
    """
    离散变量的统计信息
    """
    count = random.randint(200, 1000)
    missing_ratio = random.randint(10, 20) / 100
    outlier_ratio = random.randint(10, 20) / 100
    missing_count = int(count * missing_ratio)
    outlier_count = int(count * outlier_ratio)
    return {
        "count": count,
        "missing_count": missing_count,
        "missing_ratio": missing_ratio,
        "outlier_count": outlier_count,
        "outlier_ratio": outlier_ratio,
    }


def gen_random_continual_statistics(is_int: bool):
    """
    连续型变量的统计信息
    """
    limit = int if is_int else float
    count_info = gen_random_categorical_statistics()
    mean = random.randint(300, 600) / 100
    median = mean + random.randint(-10, 10)
    min_ = random.randint(0, 300) / 100
    max_ = random.randint(600, 1000) / 100
    count = count_info['count']
    sum = mean * count
    variance = mean - min_
    c_o_v = variance + random.randint(0, 6)
    result = {
        "sum": limit(sum),
        "mean": limit(mean),
        "standard_deviation": float,
        "median": limit(median),
        "min": limit(min_),
        "max": limit(max_),
        "variance": variance,
        "coefficient_of_variation": c_o_v,
        "skewness": random.random() * 10,
        "kurtosis": random.random() * 10,
    }
    result.update(count_info)
    return min_, max_, result

def gen_distribution(bin_num,bin_num_count,is_label):
    # 分布直方图
    if is_label:
        x_axis = [f'标签{i}' for i in bin_num]
    else:
        x_axis = [i for i in bin_num]
    return {'xAxis':x_axis,'yAxis':bin_num_count}



def gen_random_distribution(bin_num: int, is_label: bool):
    """
    # 样本分布直方图
    'x': {
        'xAxis': ['0', '1', '2', '3', '4'],
        'yAxis': [40, 80, 60, 70, 30],
    },
    'y': {
        'xAxis': ['标签1', '标签2'],
        'yAxis': [0.6, 0.8],
    }
    """
    if is_label:
        x_axis = [f'标签{i}' for i in range(bin_num)]
    else:
        x_axis = [str(i) for i in range(bin_num)]
    counts = [random.randint(100, 500) for _ in range(bin_num)]
    if is_label:
        total = sum(counts)
        counts = [count / total for count in counts]
    return {
        'xAxis': x_axis,
        'yAxis': counts
    }

def gen_boxplot(res,data,name):
    # 特征箱线图
    min = res["min"]
    max = res["max"]
    q1 = res["25%"]
    q2 = res["50%"]
    q3 = res["75%"]
    upper = q3 + 1.5*(q3-q1)
    lower = q1 - 1.5*(q3-q1)

    temp = [data.loc[(data[name] > upper) | (data[name] < lower), name].values]
    outlier = [str(v) for v in temp[0]]
    return {"min":round(min,8) if not math.isnan(min) else "-",
            "max":round(max,8) if not math.isnan(max) else "-",
            "q1":round(q1,8) if not math.isnan(q1) else "-",
            "q2":round(q2,8)if not math.isnan(q2) else "-",
            "q3":round(q3,8) if not math.isnan(q3) else "-","outlier":outlier}

def gen_random_boxplot(min_, max_, is_int: bool):
    """
    # 特征箱线图
    {
        'min':  # 下限
        'max':  # 上限
        'q1':  # 下四分位
        'q2':  # 中位数
        'q3':  # 上四分位
        'outlier':  # 异常值
    }
    """
    limit = int if is_int else float
    q1 = min_ + (max_ - min_) * 0.25
    q2 = min_ + (max_ - min_) * 0.5
    q3 = min_ + (max_ - min_) * 0.75
    outlier = [
        limit(max_ + 8),
        limit(min_ - 3),
        limit(min_ - 7),
        limit(max_ + 11),
    ]
    return {
        'min': limit(min_),
        'max': limit(max_),
        'q1': limit(q1),
        'q2': limit(q2),
        'q3': limit(q3),
        'outlier': outlier  # 异常值
    }

#计算数据的样本分布直方图
def sample_analysis1(sample_list,path) ->dict:
    distribution = {}
    data = pd.read_csv(path)
    colnum = data.shape[1]
    columns = [sample_list[i]["field_name"] for i in range(colnum)]
    data.columns = columns
    desc = data.describe()
    for i in range(colnum):
        feature = sample_list[i]
        if feature["data_type"] != "特征" or feature["party_name"] != "本地节点":
            continue
        name = feature["field_name"]
        if feature["distribution_type"] == "连续型":
            res = desc.loc[:, name]

            # 直方图
            # 先确定唯一值个数
            l = len(data[name].unique())
            if l == 1:  # 常量指标不参与模型
                # distribution[name] = {}
                continue
            if l < 5:  # 离散性指标
                # bin_num = list(data[name].unique())
                # is_label = feature["data_type"] == "Y"
                # b = data.groupby(name).agg({name: "count"})[name]
                # bin_num_count = [float(a) for a in b.values]
                # dist = gen_distribution(bin_num, bin_num_count, is_label)
                # distribution[name] = dist
                continue

            temp = pd.cut(data[name], 5)
            t = temp.value_counts()
            values = t.values
            index = t.index
            bin_num_count = [float(v) for v in values]

            bin_num = [("".join(['(', str(bin.left), ',', str(bin.right), "]"])) for bin in index]

            dist = gen_distribution(bin_num, bin_num_count, False)
            distribution[name] = dist


        elif feature["distribution_type"] == "离散型":
            bin_num = list(data[name].unique())
            bin_num = [str(b) for b in bin_num]
            is_label = feature["data_type"] == "Y"
            b = data.groupby(name).agg({name: "count"})[name]
            bin_num_count = [float(a) for a in b.values]
            dist = gen_distribution(bin_num, bin_num_count, is_label)
            distribution[name] = dist

    return {"distribution": distribution}

#样本分析(对应数据预处理操作页面的按钮)
def sample_analysis(sample_list,path,party_id,component_name=None) -> dict:
    """
    add by tjx 20220810
    :param sample_list: sample base info
    :param path: data path
    :param component_name data preprocess component name type
    :return: sample analysis result
    待测试
    """
    statistics = []
    distribution={}
    boxplot = {}

    data = pd.read_csv(path)
    colnum = data.shape[1]
    data.columns = [sample_list[i]["field_name"] for i in range(colnum)]
    # data.to_csv("/data/1842.csv",index=False)
    desc = data.describe()
    label = None
    party_id = None

    for s in sample_list:
        if s["data_type"] == "Y":
            label = s["field_name"]
            party_id = s["party_id"]
            break

    for i in range(colnum):
        feature = sample_list[i]
        if feature["data_type"] == "ID" or feature["party_name"] != "本地节点":
            continue
        name = feature["field_name"]

        if feature["distribution_type"] == "连续型":
            res = desc.loc[:,name]
            missing_count = float(data[name].isna().sum())
            missing_rate = round(missing_count/len(data),8)
            sum = float(data[name].sum())
            skew = pd.Series(data[name]).skew()
            kurt = pd.Series(data[name]).kurt()
            feature.update({"skewness": round(skew,8) if not math.isnan(skew) else "-", "kurtosis": round(kurt,8) if not math.isnan(kurt) else "-"})
            feature.update({"mean":round(res["mean"],8) if not math.isnan(res["mean"]) else "-",
                            "median":round(res["50%"],8) if not math.isnan(res['50%']) else "-",
                            "max":round(res["max"],8) if not math.isnan(res["max"]) else "-",
                            "min":round(res["min"],8) if not math.isnan(res['min']) else "-",
                            "standard_deviation":round(res["std"],8) if not math.isnan(res['std']) else "-",
                            "missing_count":missing_count,"sum":round(sum,8),"missing_rate":round(missing_rate,8)})
            # 生成箱线图
            box = gen_boxplot(res, data, name)
            # b = open(name+"_box.txt",'w')
            # b.write(str(box))
            # b.close()
            boxplot[name+"_"+party_id] = box
            #异常数和异常值比例
            min = res["min"]
            max = res["max"]
            q1 = res["25%"]
            q2 = res["50%"]
            q3 = res["75%"]
            upper = q3 + 1.5 * (q3 - q1)
            lower = q1 - 1.5 * (q3 - q1)
            temp = [data.loc[(data[name] > upper) | (data[name] < lower), name].values]
            outlier = [v for v in temp[0]]
            outliernum = float(len(outlier))
            outlierrate = outliernum/len(data)
            feature.update({"outlier_count":outliernum,"outlier_ratio":round(outlierrate,8)})

            if feature["data_type"]=="特征":
                statistics.append(feature)

            # 直方图
            # 先确定唯一值个数
            l = len(data[name].unique())
            if l == 1:#常量指标不参与模型
                # distribution[name] = {}
                continue
            if l<5:#离散性指标
                bin_num = list(data[name].unique())
                bin_num = [str(b) for b in bin_num]
                is_label = feature["data_type"] == "Y"
                b = data.groupby(name).agg({name: "count"})[name]
                bin_num_count = [float(a) for a in b.values]

                dist = gen_distribution(bin_num, bin_num_count, is_label)

                distribution[name + "_" + party_id] = dist
                continue

            temp = pd.cut(data[name],5)
            t = temp.value_counts()
            values = t.values
            index = t.index
            bin_num_count = [float(v) for v in values]

            bin_num = [("".join(['(',str(bin.left),',',str(bin.right),"]"])) for bin in index]

            dist = gen_distribution(bin_num,bin_num_count,False)
            distribution[name+"_"+party_id] = dist



        elif feature["distribution_type"] == "离散型":
            bin_num = list(data[name].unique())
            bin_num = [str(b) for b in bin_num]
            is_label = feature["data_type"] == "Y"
            b = data.groupby(name).agg({name:"count"})[name]
            bin_num_count = [float(a) for a in b.values]

            dist = gen_distribution(bin_num,bin_num_count,is_label)


            distribution[name+"_"+party_id] = dist
    # b1 = open("statistics1514.txt",'w')
    # b1.write(str(boxplot))
    # b1.close()
    if label:
        return {"statistics":statistics,"distribution":distribution,"boxplot":boxplot,"label":label+"_"+party_id}
    else:
        return {"statistics": statistics, "distribution": distribution, "boxplot": boxplot}
    # return {"boxplot":boxplot}


# 样本分析（对应数据预处理操作页面的按钮）
def gen_random_analysis(sample_list: list) -> dict:
    """
    sample_list = [
        {
            "data_type": "特征",
            "distribution_type": "分布类型",
            "field_description": "特征描述",
            "field_examples": "特征值示例",
            "field_name": "特征名称",
            "field_type": "特征类型",
            "party_id": "所属节点",
            "positive_value": "正例值",
        },
        ...
    ]
    """
    statistics = []
    distribution = {}
    boxplot = {}
    for feature in sample_list:
        name = feature['field_name']
        if feature['distribution_type'] == '离散型':
            bin_num = random.randint(2, 7)
            is_label = feature['data_type'] == 'Y'
            dist = gen_random_distribution(bin_num, is_label)
            stat = gen_random_categorical_statistics()
            feature.update(stat)
            distribution[name] = dist
        else:
            is_int = feature['field_type'] == 'int'
            min_, max_, stat = gen_random_continual_statistics(is_int)
            box = gen_random_boxplot(min_, max_, is_int)
            feature.update(stat)
            boxplot[name] = box
        statistics.append(feature)
    return {
        'statistics': statistics,
        'distribution': distribution,
        'boxplot': boxplot
    }
