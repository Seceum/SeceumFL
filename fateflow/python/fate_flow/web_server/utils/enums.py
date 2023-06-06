from enum import Enum

from fate_flow.entity.types import CustomEnum


class SampleDataEnum(Enum):
    MYSQL = "MYSQL"
    HDFS = "HDFS"
    ORACLE = "ORACLE"
    LOCAL = "本地文件"
    HBASE = "HBASE"
    FLHIVE = "FLHIVE"
    POSTGRESQL = "POSTGRESQL"


class OwnerEnum(Enum):
    OWN = "0"  # 自有
    OTHER = "1"  # 外部







class PartyPingStatusEnum(Enum):
    # 样本可用状态
    CONNECT = "正常"  # 可用
    LOSS_CONNECT = "异常"  # 不可用


class SampleTypeEnum(Enum):
    ORIGIN = "0"  # 原始样本
    FUSION = "1"  # 融合样本


class StatusChineseEnum(Enum):
    # 样本可用状态
    VALID = "可用"
    IN_VALID = "不可用"
    IMMUTABLE = "不可变动"

class NodeStatusEnum(Enum):
    IN_VALID="0" # 不可用

class StatusEnum(Enum):
    # 样本可用状态
    VALID = "1"  # 可用
    IN_VALID = "0"  # 不可用

class SampleStatusEnum(Enum):
    IN_VALID="0"
    VALID = "1"  # 可用
    OFF_LINE="2"
    DELETE="3"
    EXPIRE_OR_OUT_OF_RANGE="4"
    NOT_APPLY = "5"
    APPLY="6"
    REJECT="7"
    CANCEL_AUTH="8"
    NOT_FIND = "9"
    IMMUTABLE = "-1"  # 不可变动

class SampleStatusChineseEnum(Enum):
    # 样本可用状态
    VALID = "可用"
    IN_VALID = "不可用"
    OFF_LINE = "已下线"
    DELETE = "已删除"
    EXPIRE_OR_OUT_OF_RANGE = "已过期"
    APPLY = "申请中"
    IMMUTABLE = "不可变动"
    CANCEL_AUTH = "已取消"
    NOT_APPLY = "未申请"
    REJECT = "未授权"
    NOT_FIND = "不存在"

class SamplePublishStatusEnum(Enum):
    UNPUBLISHED = "0"
    PUBLISHED = "1"
    OFF_LINE = "2"
    DELETE = "3"
    EXPIRE_OR_OUT_OF_RANGE = "4"
class SamplePublishChineseStatusEnum(Enum):
    UNPUBLISHED = "未上线"
    PUBLISHED = "已上线"
    OFF_LINE = "已下线"
    # DELETE = "3"
    # EXPIRE_OR_OUT_OF_RANGE = "4"


class PublishStatusChineseEnum(Enum):
    UNPUBLISHED = "未发布"
    PUBLISHED = "已发布"
    RUNNING = "发布中"
    FAILD = "发布失败"

class ApproveStatusChineseEnum(Enum):
    # 申请状态
    APPLY = "申请中"
    AGREE = "已同意"
    REJECT = "已拒绝"
    CANCEL_AUTH = "已取消"
    # CANCEL_AUTH = "取消授权"
    NOT_APPLY = "未申请"


class ApproveOutStatusChineseEnum(Enum):
    # 外部申请状态
    APPLY = "申请中"
    AGREE = "已授权"
    REJECT = "未授权"
    # CANCEL_AUTH = "取消授权"
    CANCEL_AUTH = "已取消"
    NOT_APPLY = "未申请"


class ApproveStatusEnum(Enum):
    # 外部申请状态
    APPLY = "0"
    AGREE = "1"
    REJECT = "2"
    CANCEL_AUTH = "3"
    NOT_APPLY = "4"


class PartyStatusEnum(Enum):
    # 外部申请状态
    SUCCESS = "1"
    ERROR = "0"


class UserAuthEnum(Enum):
    # PROJECT = "0100"  # 项目管理
    # MODULE = "0200"  # 模型管理
    # PREDICT = "0300"  # 预测服务
    # SYSTEM = "0400"  # 系统管理
    # USER_MANAGER = "0401"  # 用户管理
    # AUTH_MANAGER = "0402"  # 授权管理
    # NODE = "0500"  # 节点管理
    # DATA_ASSET = "0600"  # 数据资产
    # OWN = "0601"  # 自有数据
    # EXTERNAL = "0602"  # 外部数据
    # APPROVE = "0603"  # 授权审批
    INDEX = "01000000"
    PROJECT="02000000"
    PROJECT_GUEST="02010000"
    PROJECT_GUEST_CREATE="02010100"
    PROJECT_GUEST_UPDATE="02010200"
    PROJECT_GUEST_DELETE="02010300"
    PROJECT_HOST="02020000"
    MODEL="03000000"
    MODEL_GUEST="03010000"
    MODEL_GUEST_IMPORT="03010100"
    MODEL_GUEST_PUBLISH="03010200"
    MODEL_GUEST_PREDICT="03020300"
    MODEL_GUEST_DETAIL="03010400"
    MODEL_GUEST_EXPORT="03010500"
    MODEL_GUEST_DELETE="03010600"
    MODEL_HOST="03020000"
    MODEL_HOST_EXPORT="03020100"
    MODEL_HOST_APPROVE="03020200"
    MODEL_HOST_IMPORT="03020300"
    SERVICE="04000000"
    DATA="05000000"
    DATA_GUEST="05010000"
    DATA_GUEST_CREATE="05010100"
    DATA_GUEST_ONLINE_OFFLINE="05010200"
    DATA_GUEST_DELETE="05010300"
    DATA_HOST="05020000"
    DATA_HOST_APPLY="05020100"
    DATA_APPROVE = "05030000"
    DATA_APPROVE_GUEST = "05030000"
    DATA_APPROVE_GUEST_APPLY = "05030000"
    DATA_APPROVE_APPROVE = "05030000"
    SYSTEM ="06000000"
    # SYSTEM_USER ="06010000"
    SYSTEM_USER_NODE ="06010100"
    SYSTEM_USER_NODE_CREATE ="06010101"
    SYSTEM_USER_NODE_PING ="06010102"
    SYSTEM_USER_NODE_UPDATE ="06010103"
    SYSTEM_USER_NODE_DELETE ="06010104"




class RoleTypeEnum(Enum):
    GUEST = "guest"
    HOST = "host"
    ARBITER = "arbiter"
    INITIATOR = "initiator"


class JobStatusEnum(Enum):
    WAITING = 'waiting'
    READY = 'ready'
    RUNNING = "running"
    CANCELED = "canceled"
    TIMEOUT = "timeout"
    FAILED = "failed"
    PASS = "pass"
    SUCCESS = "success"


class JobStatusChineseEnum(Enum):
    WAITING = "等待中"
    READY = "等待中"
    RUNNING = "执行中"
    CANCELED = "终止"
    TIMEOUT = "执行超时"
    FAILED = "执行失败"
    PASS = "未执行"
    SUCCESS = "执行成功"


class InitiatorEnum(Enum):
    INITIATOR = "1"  # 发起方
    NON_INITIATOR = "0"  # 非发起方


class JobStatusKey:
    waiting = "等待中"
    ready = "等待中"
    running = "执行中"
    canceled = "终止"
    timeout = "执行超时"
    failed = "执行失败"
    success = "执行成功"


class RoleEnum(Enum):
    administrator = "管理员"
    modeler = "建模人员"


class LogType:
    partyInfo = "INFO.log"
    partyDebug = "DEBUG.log"
    partyError = "ERROR.log"
    partyWarning = "WARNING.log"


class MixTypeEnum(Enum):
    intersection = "0"  # 求交
    union = "1"  # 求并




class APPROVEChineseEnum(Enum):
    APPROVE_running = "审批中"
    APPROVE_WAITING = "待审批"
    APPROVE_TRUE = "已同意"
    APPROVE_FALSE = "已拒绝"


class SampleUsedEnum(Enum):
    NOT_USED = "0"
    USED = "1"

class MixTypeEnumCopy(Enum):
    intersection = "intersection"  # 求交
    union = "union"  # 求并


class MixTypeChineseEnum(Enum):
    intersection = "纵向建模"
    union = "横向建模"
    stealth = "隐匿查询"
    predict = "预测服务"
    off_predict = "离线预测"


class FieldTypeChinese:
    continuity = "连续型"
    dispersed = "离散型"


class FusionFieldControl:
    Sampling = "all"
    FillMissing = "all"
    FillOutlier = "all"
    StandardScale = "continuity"
    MinMaxScale = "continuity"
    HeteroOneHotEncoder = "dispersed"
    Statistics = "all"
    HeteroQuantile = "continuity"
    HomoQuantile = "continuity"
    HeteroBucket = "continuity"
    HomoBucket = "continuity"
    HeteroChi2 = "continuity"
    HomoChi2 = "continuity"
    SecureInformationRetrieval = "all"

class SiteKeyName(CustomEnum):
    PRIVATE = "private"
    PUBLIC = "public"