import datetime

import pandas as pd

from fate_flow.web_server.utils.common_util import get_format_time
from fate_flow.web_server.utils.enums import ApproveStatusChineseEnum, ApproveOutStatusChineseEnum, StatusEnum, \
    StatusChineseEnum, JobStatusKey, MixTypeChineseEnum, ApproveStatusEnum, SampleStatusEnum, SamplePublishStatusEnum, \
    SampleStatusChineseEnum, SamplePublishChineseStatusEnum


def own_approve_result_apply(val):
    if val == "0":
        val = ApproveStatusChineseEnum.APPLY.value
    elif val == "1":
        val = ApproveStatusChineseEnum.AGREE.value
    elif val == "2":
        val = ApproveStatusChineseEnum.REJECT.value
    elif val == "3":
        val = ApproveStatusChineseEnum.CANCEL_AUTH.value
    return val


def out_approve_result_apply(val):
    if val == "0":
        val = ApproveOutStatusChineseEnum.APPLY.value
    elif val == "1":
        val = ApproveOutStatusChineseEnum.AGREE.value
    elif val == "2":
        val = ApproveOutStatusChineseEnum.REJECT.value
    elif val == "3":
        val = ApproveOutStatusChineseEnum.CANCEL_AUTH.value
    else:
        val = ApproveOutStatusChineseEnum.NOT_APPLY.value
    return val

def approve_result_to_sample_status(val):
    if val == SamplePublishStatusEnum.UNPUBLISHED.value:
        val = SampleStatusEnum.APPLY.value
    elif val ==SamplePublishStatusEnum.PUBLISHED.value:
        val= SampleStatusEnum.VALID.value
    elif val == SamplePublishStatusEnum.OFF_LINE.value:
        val = SampleStatusEnum.REJECT.value
    elif val ==  SamplePublishStatusEnum.DELETE.value:
        val = SampleStatusEnum.CANCEL_AUTH.value
    elif val == SamplePublishStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value:
        val =  SampleStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value
    else:
        val = SampleStatusEnum.NOT_APPLY.value
    return val

def external_status(publish_status):
    # if status == StatusEnum.IN_VALID.value or publish_status == StatusEnum.IN_VALID.value:
    #     return StatusChineseEnum.IN_VALID.value
    # else:
    #     return StatusChineseEnum.VALID.value
    if publish_status == SamplePublishStatusEnum.DELETE.value:
        return SampleStatusChineseEnum.DELETE.value
    elif publish_status == SamplePublishStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value:
        return SampleStatusChineseEnum.EXPIRE_OR_OUT_OF_RANGE.value
    elif publish_status == SamplePublishStatusEnum.OFF_LINE.value:
        return SampleStatusChineseEnum.OFF_LINE.value
    elif publish_status == SamplePublishStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value:
        return SampleStatusChineseEnum.EXPIRE_OR_OUT_OF_RANGE.value
    else:
        return SampleStatusChineseEnum.VALID.value
def sample_chinese_status(status):
    if status == SampleStatusEnum.IN_VALID.value:
        return SampleStatusChineseEnum.IN_VALID.value
    elif status == SampleStatusEnum.VALID.value:
        return SampleStatusChineseEnum.VALID.value
    elif status == SampleStatusEnum.OFF_LINE.value:
        return SampleStatusChineseEnum.OFF_LINE.value
    elif status == SampleStatusEnum.DELETE.value:
        return SampleStatusChineseEnum.DELETE.value
    elif status == SampleStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value:
        return SampleStatusChineseEnum.EXPIRE_OR_OUT_OF_RANGE.value
    elif status == SampleStatusEnum.NOT_APPLY.value:
        return SampleStatusChineseEnum.NOT_APPLY.value
    elif status == SampleStatusEnum.APPLY.value:
        return SampleStatusChineseEnum.APPLY.value
    elif status == SampleStatusEnum.REJECT.value:
        return SampleStatusChineseEnum.REJECT.value
    elif status == SampleStatusEnum.CANCEL_AUTH.value:
        return SampleStatusChineseEnum.CANCEL_AUTH.value
    elif status == SampleStatusEnum.NOT_FIND.value:
        return SampleStatusChineseEnum.NOT_FIND.value
    elif status == SampleStatusEnum.IMMUTABLE.value:
        return SampleStatusChineseEnum.IMMUTABLE.value

def status_and_publish_status(ser):

    if ser["status"]=="可用" and ser["publish_status"]=="可用":
        return "可用"
    elif ser["status"]=="可用" and ser["publish_status"]!="可用":
        return ser["publish_status"]
    return ser["status"]
    # if ser["approve_result"] in [ApproveStatusEnum.AGREE.value, ApproveStatusEnum.APPLY.value]:
    #     if ser["fusion_limit"] is True:
    #         res = ser["fusion_times_limits"]
    #     elif ser["fusion_limit"] is False:
    #         res = "不限"
    #     else:
    #         res = ""
    # else:
    #     res = ""
    # return res



def concat_col(df):
    col_dict = {col_name: ",".join(df[col_name].dropna().astype(str).unique()) for col_name in df.columns}
    return pd.Series(col_dict)


def job_status_apply(val):
    if hasattr(JobStatusKey, val):
        return getattr(JobStatusKey, val)
    return val


def status_chinese_apply(val):
    if val == SampleStatusEnum.VALID.value:
        return SampleStatusChineseEnum.VALID.value
    elif val == SampleStatusEnum.OFF_LINE.value:
        return SampleStatusChineseEnum.OFF_LINE.value
    elif val == SampleStatusEnum.DELETE.value:
        return SampleStatusChineseEnum.DELETE.value
    elif val == SampleStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value:
        return SampleStatusChineseEnum.EXPIRE_OR_OUT_OF_RANGE.value
    elif val == SampleStatusEnum.NOT_APPLY.value:
        return SampleStatusChineseEnum.NOT_APPLY.value
    elif val == SampleStatusEnum.APPLY.value:
        return SampleStatusChineseEnum.APPLY.value
    elif val == SampleStatusEnum.REJECT.value:
        return SampleStatusChineseEnum.REJECT.value
    elif val == SampleStatusEnum.CANCEL_AUTH.value:
        return SampleStatusChineseEnum.CANCEL_AUTH.value
    elif val == SampleStatusEnum.IMMUTABLE.value:
        return SampleStatusChineseEnum.IMMUTABLE.value
    else:
        return SampleStatusChineseEnum.NOT_FIND.value

def mix_type_apply(val):
    if val == "0":
        val = MixTypeChineseEnum.intersection.value
    elif val == "1":
        val = MixTypeChineseEnum.union.value
    elif val == "2":
        val = MixTypeChineseEnum.stealth.value
    elif val == "3":
        val = MixTypeChineseEnum.predict.value
    return val


def format_time(create_time):
    end = datetime.datetime.now()
    if not create_time:
        return "job未创建"
    timedelta = (end - create_time).total_seconds()
    if 0 < timedelta <= 60:
        format_time_str = "刚刚"
    elif 60 < timedelta <= 600:
        format_time_str = "1分钟前"
    elif 600 < timedelta <= 1800:
        format_time_str = "10分钟前"
    elif 1800 < timedelta <= 3600:
        format_time_str = "半小时前"
    elif 3600 < timedelta <= 10200:
        format_time_str = "1小时前"
    elif 10200 < timedelta <= 21600:
        format_time_str = "3小时前"
    elif 21600 < timedelta <= 43200:
        format_time_str = "6小时前"
    elif 43200 < timedelta <= 86400:
        format_time_str = "12小时前"
    elif 86400 < timedelta <= 172800:
        format_time_str = "1天前"
    elif 172800 < timedelta <= 259200:
        format_time_str = "2天前"
    elif 259200 < timedelta <= 345600:
        format_time_str = "3天前"
    else:
        format_time_str = str(create_time)
    return format_time_str


def approve_times_limits(ser):
    if ser["approve_result"] in [ApproveStatusEnum.AGREE.value, ApproveStatusEnum.APPLY.value]:
        if ser["fusion_limit"] is True:
            res = ser["fusion_times_limits"]
        elif ser["fusion_limit"] is False:
            res = "不限"
        else:
            res = ""
    else:
        res = ""
    return res


def approve_fusion_count_bak(ser):
    if ser["fusion_times_limits"] in [ApproveStatusEnum.AGREE.value, ApproveStatusEnum.APPLY.value]:
        if ser["fusion_limit"]:
            return ser["current_fusion_count"]
        else:
            return ser["total_fusion_count"]
    else:
        return ""


def approve_fusion_count(ser):
    if ser["fusion_times_limits"] == "":
        return ""
    if ser["fusion_limit"]:
        return ser["current_fusion_count"]
    else:
        return ser["total_fusion_count"]


def sample_can_remove(ser):
    # 样本状态，审批状态、日期、使用次数
    # 判断申请中是否能使用
    if ser.get("status") and ser["status"] != StatusEnum.VALID.value:
        return ser.get("status")
    if ser["approve_result"] in [ApproveStatusEnum.AGREE.value,ApproveStatusEnum.APPLY.value]:
        if ser["approve_result"] ==ApproveStatusEnum.APPLY.value and not ser["fusion_deadline"]:
            return SampleStatusEnum.APPLY.value
        fusion_times_limits = ser["fusion_times_limits"] if ser["fusion_times_limits"] else 0
        if ser["fusion_deadline"] < get_format_time().date():
            return  SampleStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value
        if ser["fusion_limit"] and (ser["current_fusion_count"] >= fusion_times_limits):
            return SampleStatusEnum.EXPIRE_OR_OUT_OF_RANGE.value
        return SampleStatusEnum.VALID.value
    elif ser["approve_result"] in [ApproveStatusEnum.REJECT.value]:
        return SampleStatusEnum.REJECT.value
    elif ser["approve_result"] in [ApproveStatusEnum.CANCEL_AUTH.value]:
        return SampleStatusEnum.CANCEL_AUTH.value
    elif ser["approve_result"] in [ApproveStatusEnum.NOT_APPLY.value]:
        return SampleStatusEnum.NOT_APPLY.value
    else:
        return SampleStatusEnum.NOT_APPLY.value

def sample_on_off_chinese_status(status):
    if status == SamplePublishStatusEnum.UNPUBLISHED.value:
        return SamplePublishChineseStatusEnum.UNPUBLISHED.value
    elif status == SamplePublishStatusEnum.PUBLISHED.value:
        return SamplePublishChineseStatusEnum.PUBLISHED.value
    elif status == SamplePublishStatusEnum.OFF_LINE.value:
        return SamplePublishChineseStatusEnum.OFF_LINE.value
    return "none"

