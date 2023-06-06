from enum import Enum

class StoreType(Enum):
    PARTY = "企业信息"
    TASK_PROJECT = "任务项目"
    TASK_CANVAS = "任务画布"
    # TASK_JOB = "任务job"
    # MODEL = "模型在线预测和离线预测"
    DATA_USER = "数据，用户数据"
    DATA_MODEL = "数据，模型"
    DATA_SAMPLE = "数据，样本"
    # DATA_AUTH = "数据权限"