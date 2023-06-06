import inspect
import operator
import sys
from flask_login import UserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer
from peewee import CharField, IntegerField, CompositeKey, Model, Metadata, TextField, BigIntegerField, DateField, \
    BooleanField, JOIN, Entity, SQL, NodeList, ForeignKeyField
from datetime import datetime

from playhouse.migrate import MySQLMigrator

from fate_flow.db.db_models import DB, LOGGER, DataBaseModel
from fate_arch.metastore.base_model import DateTimeField, is_continuous_field, LongTextField
from fate_arch.metastore.base_model import JSONField
from fate_flow.settings import IS_STANDALONE
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.utils.common_util import datetime_format
from fate_flow.web_server.utils.enums import StatusEnum, RoleTypeEnum


def ddl(self, ctx):
    accum = [Entity(self.column_name)]
    data_type = self.ddl_datatype(ctx)
    if data_type:
        accum.append(data_type)
    if self.unindexed:
        accum.append(SQL('UNINDEXED'))
    if not self.null:
        accum.append(SQL('NOT NULL'))
    if self.primary_key:
        accum.append(SQL('PRIMARY KEY'))
    if self.sequence:
        accum.append(SQL("DEFAULT NEXTVAL('%s')" % self.sequence))
    if self.constraints:
        accum.extend(self.constraints)
    if self.collation:
        accum.append(SQL('COLLATE %s' % self.collation))
    if self.help_text:
        accum.append(SQL('comment "%s"' % self.help_text))
    return NodeList(accum)

# print("IS_STANDALONE",IS_STANDALONE)
if not IS_STANDALONE:
    CharField.ddl = ddl
    IntegerField.ddl = ddl
    TextField.ddl = ddl
    BigIntegerField.ddl = ddl
    DateField.ddl = ddl
    BooleanField.ddl = ddl
    DateTimeField.ddl = ddl
    JSONField.ddl = ddl


class WebBaseModel(Model):
    creator = CharField(max_length=100, null=True, help_text="创建者")
    updator = CharField(max_length=100, null=True, help_text="修改者")
    create_time = DateTimeField(null=True, help_text="创建时间")
    update_time = DateTimeField(null=True, help_text="修改时间")

    def to_json(self):
        return self.to_dict()

    def to_dict(self):
        return self.__dict__['__data__']

    @property
    def meta(self) -> Metadata:
        return self._meta

    @classmethod
    def get_primary_keys_name(cls):
        return cls._meta.primary_key.field_names if isinstance(cls._meta.primary_key, CompositeKey) else [
            cls._meta.primary_key.name]

    @classmethod
    def getter_by(cls, attr):
        return operator.attrgetter(attr)(cls)

    @classmethod
    def query(cls, cols=None, reverse=None, order_by=None, **kwargs):
        filters = kwargs.get("filters", [])
        for f_n, f_v in kwargs.items():
            if not hasattr(cls, f_n) or f_v is None:
                continue
            if type(f_v) in {list, set}:
                f_v = list(f_v)
                if is_continuous_field(type(getattr(cls, f_n))):
                    if len(f_v) == 2:
                        lt_value = f_v[0]
                        gt_value = f_v[1]
                        if lt_value is not None and gt_value is not None:
                            filters.append(cls.getter_by(f_n).between(lt_value, gt_value))
                        elif lt_value is not None:
                            filters.append(operator.attrgetter(f_n)(cls) >= lt_value)
                        elif gt_value is not None:
                            filters.append(operator.attrgetter(f_n)(cls) <= gt_value)
                else:
                    filters.append(operator.attrgetter(f_n)(cls) << f_v)
            else:
                filters.append(operator.attrgetter(f_n)(cls) == f_v)
        if filters:
            if cols:
                query_records = cls.select(*cols).where(*filters)
            else:
                query_records = cls.select().where(*filters)
            if reverse is not None:
                if not order_by or not hasattr(cls, order_by):
                    order_by = "create_time"
                if reverse is True:
                    query_records = query_records.order_by(cls.getter_by(order_by).desc())
                elif reverse is False:
                    query_records = query_records.order_by(cls.getter_by(order_by).asc())
            return query_records
        else:
            return None

    def save(self, *args, **kwargs):
        if not self.create_time:
            self.create_time = datetime_format(datetime.now())
        return super(WebBaseModel, self).save(*args, **kwargs)


class WebDataBaseModel(WebBaseModel):
    class Meta:
        database = DB


class StudioModelInfoExtend(WebDataBaseModel):
    id = CharField(max_length=100, help_text="模型编号")
    name = CharField(max_length=64, null=True, help_text="模型名称")
    project_id = CharField(max_length=32, null=True, help_text="项目序号")
    project_name = CharField(max_length=64, null=True, help_text="项目名称")
    job_id = CharField(max_length=25, null=True, help_text="任务序号")
    job_name = CharField(max_length=64, null=True, help_text="任务名称")
    job_content = TextField(null=True, help_text="任务编排内容")
    version = CharField(max_length=100, help_text="模型版本")
    role_type = CharField(max_length=50, help_text="项目中扮演角色guest、host、arbiter、initiator")
    sample_id = CharField(max_length=32, null=True, help_text="本方参与样本id")
    sample_name = CharField(max_length=256, null=True, help_text="本方参与样本名称")
    party_id = CharField(max_length=10, help_text="参与方编码")
    initiator_party_id = CharField(max_length=10, help_text="发起方编码")
    initiator_party_name = CharField(max_length=64, help_text="发起方名称")
    status = CharField(max_length=10, null=True, help_text="发布状态：未发布，发布中,发布失败,发布成功")
    approve_status = CharField(max_length=10, null=True, help_text="审批状态:待审批，审批中，已同意，已拒绝")
    publish_result = TextField(null=True, help_text="模型发布结果 成功或失败原因")
    approve_progress = IntegerField(null=True, help_text="模型发布审批进度条", default=0)
    approve_result = TextField(null=True, help_text="模型发布,各方反馈结果")
    service_name = CharField(null=True, max_length=100, help_text="服务名称")
    service_reason = CharField(null=True, max_length=128, help_text="服务申请理由")
    service_start_time = DateTimeField(null=True, help_text="申请时间")
    service_end_time = DateTimeField(null=True, help_text="审批时间")
    mix_type = CharField(max_length=10, null=True, help_text="融合方式")
    operate_advise = CharField(max_length=1024, null=True, help_text="审批意见")
    file_name = CharField(max_length=64, null=True, help_text="模型预测 上传的文件名")

    # UNPUBLISHED = "未发布"
    # SUCCESS = "发布成功"
    # APPROVE_WAITING = "待审批"
    # APPROVE_TRUE = "审批通过"
    # APPROVE_RUNNING = "发布中"
    # APPROVE_FALSE = "审批拒绝"
    # FAILD = "发布失败"

    def __str__(self):
        return self.version

    class Meta:
        db_table = "studio_model_info_extend"
        primary_key = CompositeKey("id", "version", "role_type", "party_id", "sample_id")


class StudioPartyInfo(WebDataBaseModel):
    id = CharField(max_length=10, primary_key=True, help_text="合作方编号")
    party_name = CharField(max_length=64, null=True, help_text="合作方名称")
    train_party_ip = CharField(max_length=64, null=True, help_text="自己方的eggroll_ip")
    train_port = IntegerField(null=True, help_text="自己方的eggroll_port")
    rollsite_ip = CharField(max_length=64, null=True, help_text="参数没用到")
    rollsite_port = IntegerField(null=True, help_text="参数没用到")
    predict_party_ip = CharField(max_length=64, null=True, help_text="合作方eggroll_ip")
    predict_port = IntegerField(null=True, help_text="合作方eggroll_port")
    status = CharField(max_length=1, null=True, help_text="节点状态（0 无效，1 有效）", default="1")
    ping_status = CharField(max_length=10, null=True, help_text="节点联通状态（正常，异常）")
    public_key = CharField(max_length=4096, null=True, help_text="合作方提供的公钥")
    contact_person = CharField(max_length=20, null=True, help_text="联系人")
    contact_phone = CharField(max_length=15, null=True, help_text="联系电话")
    contact_email = CharField(max_length=50, null=True, help_text="联系邮箱")
    comments = CharField(max_length=128, null=True, help_text="备注")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_party_info"


class StudioProjectInfo(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    name = CharField(max_length=64, null=True, help_text="项目名称")
    comments = CharField(max_length=128, null=True, help_text="项目简介")
    guest_party_id = CharField(max_length=25, null=True, help_text="项目发起方节点序号")
    role_type = CharField(max_length=50, null=True, help_text="项目中扮演角色guest、host、arbiter、initiator")
    status = CharField(max_length=1, null=True, help_text="项目状态:0无效，1有效", default="1")
    project_activation_code = CharField(max_length=64, null=True, help_text="项目激活码")
    host_own = BooleanField(help_text="是否有拥有者", null=True, default=False)
    host_own_id = CharField(max_length=32, null=True, help_text="host拥有者id")
    def __str__(self):
        return self.name

    # @staticmethod
    # def get_auth_projects(role_type=RoleTypeEnum.GUEST.value):
    #     creator = current_user.username
    #     current_user_id = current_user.id
    #
    #     if current_user.is_superuser:
    #         auth_projects = StudioProjectInfo. \
    #             select(StudioProjectInfo.id). \
    #             where(StudioProjectInfo.status == StatusEnum.VALID.value, StudioProjectInfo.role_type ==role_type). \
    #             distinct()
    #     else:
    #         auth_projects = StudioProjectInfo. \
    #             select(StudioProjectInfo.id). \
    #             join(StudioProjectUser, JOIN.LEFT_OUTER, on=(StudioProjectInfo.id == StudioProjectUser.project_id)). \
    #             where(StudioProjectInfo.status == StatusEnum.VALID.value, StudioProjectInfo.role_type == role_type,
    #                   (StudioProjectInfo.creator == creator) | (StudioProjectUser.user_id == current_user_id)). \
    #             distinct()
    #     return auth_projects
    #
    # @classmethod
    # def get_auth_canvas(cls):
    #     auth_projects = cls.get_auth_projects()
    #     if auth_projects:
    #         canvas = StudioProjectCanvas.select(StudioProjectCanvas.id.alias("canvas_id")). \
    #             where(StudioProjectCanvas.project_id.in_(auth_projects))
    #         if canvas:
    #             return [i["canvas_id"] for i in canvas.dicts()]
    #     return []
    #
    class Meta:
        db_table = "studio_project_info"

class StudioProjectActivationCode(WebDataBaseModel):

    project_id = CharField(max_length=64, null=True, help_text="项目名称")
    # project_activation_code = CharField(max_length=64, null=True, help_text="项目名称")
    party_id = CharField(max_length=128, null=True, help_text="项目简介")

    def __str__(self):
        return self.project_id

    class Meta:
        db_table = "studio_project_activation_code"

class StudioProjectParty(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    project_id = CharField(max_length=32, help_text="项目序号")
    party_id = CharField(max_length=10, null=True, help_text="合作方编号")

    def __str__(self):
        return "{}-{}".format(self.project_id, self.party_id)

    class Meta:
        db_table = "studio_project_party"


class StudioProjectSample(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    project_id = CharField(max_length=32, null=True, help_text="项目序号")
    sample_id = CharField(max_length=32, null=True, help_text="样本序号")
    sample_type = CharField(max_length=1, null=True, help_text="样本类型：0原始样本,1融合样本")
    job_type = CharField(max_length=10, null=True, help_text="任务类型")



    def __str__(self):
        return "{}-{}".format(self.project_id, self.sample_id)

    class Meta:
        db_table = "studio_project_sample"


class StudioProjectUsedSample(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    project_id = CharField(max_length=32, null=True, help_text="项目序号")
    sample_id = CharField(max_length=32, null=True, help_text="样本序号")
    party_id = CharField(max_length=10, null=True, help_text="合作方id")
    sample_type = CharField(max_length=1, null=True, help_text="样本类型：0原始样本,1融合样本")
    job_id = CharField(max_length=25, help_text="任务id")
    canvas_id = CharField(max_length=32, help_text="画布id")

    def __str__(self):
        return "{}-{}".format(self.project_id, self.sample_id)

    class Meta:
        db_table = "studio_project_used_sample"


class StudioProjectUsedModel(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    project_id = CharField(max_length=32, null=True, help_text="项目序号")
    model_id = CharField(max_length=100, null=True, help_text="样本序号")
    model_version = CharField(max_length=100, null=True, help_text="样本序号")
    mix_type = CharField(max_length=10, null=True, help_text="融合方式")
    job_id = CharField(max_length=25, help_text="任务id")
    canvas_id = CharField(max_length=32, help_text="画布id")

    def __str__(self):
        return "{}".format(self.model_version)

    class Meta:
        db_table = "studio_project_used_model"


class StudioProjectCanvas(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号，画布id")
    project_id = CharField(max_length=32, null=True, help_text="项目序号")
    job_type = CharField(max_length=10, null=True, help_text="任务类型")
    job_name = CharField(max_length=64, null=True, help_text="任务名称")
    canvas_content = JSONField(null=True, help_text="画布编排内容")
    target_content = JSONField(null=True, help_text="画布任务的目标及label的信息")
    status = CharField(max_length=10, null=False, default="save", help_text="画布状态，save/run/stop")

    def __str__(self):
        return "{}".format(self.id)

    class Meta:
        db_table = "studio_project_canvas"


class StudioJobContent(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    job_id = CharField(max_length=25, null=True, help_text="任务id")
    job_name = CharField(max_length=128, null=True, help_text="任务名称，可自动生成")
    last_job_id = CharField(max_length=25, null=True, help_text="上游任务id")
    canvas_id = CharField(max_length=32, null=True, help_text="画布id")
    module_name = CharField(max_length=64, null=True, help_text="组件名称")
    job_content = TextField(null=True, help_text="任务编排内容")
    run_param = JSONField(null=True, help_text="任务参数")
    party_info = JSONField(null=True, help_text="任务参与方信息")
    is_latest = BooleanField(null=True, help_text="是否是最新画布内容")

    def __str__(self):
        return "{}".format(self.id)

    class Meta:
        db_table = "studio_job_content"

class StudioChainInfo(WebDataBaseModel):
    id = CharField(max_length=100, help_text="id")
    type = CharField(max_length=64, null=True, help_text="类型")
    last_store_time = DateTimeField(null=True, help_text="上次上链时间")
    is_latest = BooleanField(null=True, help_text="是否是最新内容")
    store_data = JSONField(null=True, help_text="上链数据")
    store_return = CharField(max_length=64, null=True, help_text="上链返回id")


    def __str__(self):
        return self.store_data

    class Meta:
        db_table = "studio_clain_info"
        primary_key = CompositeKey("id")


class StudioProjectUser(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    project_id = CharField(max_length=32, help_text="项目序号")
    user_id = CharField(max_length=32, null=True, help_text="人员序号")
    role_type = CharField(max_length=32, null=True, help_text="角色")
    is_own = BooleanField(help_text="是否是拥有者", null=True, default=False)
    project_activation_code = CharField(max_length=64, null=True, help_text="项目激活码")

    def __str__(self):
        return "{}-{}".format(self.project_id, self.user_id)

    class Meta:
        db_table = "studio_project_user"


class StudioSampleAuthorize(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    sample_id = CharField(max_length=32, null=True, help_text="样本序号")
    sample_name = CharField(max_length=256, null=True, help_text="本方参与样本名称")
    apply_party_id = CharField(max_length=25, null=True, help_text="申请方节点编码")
    apply_party_name = CharField(max_length=64, null=True, help_text="申请方节点名称")
    approve_party_id = CharField(max_length=25, null=True, help_text="授权方节点编码")
    approve_party_name = CharField(max_length=64, null=True, help_text="授权方节点名称")
    apply_time = DateTimeField(null=True, help_text="申请时间")
    approve_time = DateTimeField(null=True, help_text="审批时间")
    fusion_times_limits = BigIntegerField(help_text="求交次数限制数", null=True)
    fusion_deadline = DateField(help_text="截至日期", null=True)
    fusion_limit = BooleanField(help_text="融合上限", null=True, default=True)
    current_fusion_count = BigIntegerField(help_text="当前求交次数", null=True, default=0)
    total_fusion_count = BigIntegerField(help_text="总计求交次数", null=True, default=0)
    approve_result = CharField(max_length=1, help_text="审批状态(申请中0、同意1、拒绝2、取消授权3)", null=True, default=0)
    owner = CharField(max_length=1, null=True, help_text="样本拥有者(0:本方、1:合作方)")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_sample_authorize"

class StudioSampleAuthorizeHistory(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    sample_id = CharField(max_length=32, null=True, help_text="样本序号")
    sample_name = CharField(max_length=256, null=True, help_text="本方参与样本名称")
    sample_type = CharField(max_length=30, null=True, help_text="样本集类别(0纵向融合X样本,1纵向融合Y样本,2纵向融合仅ID值样本,3横向融合样本)")
    apply_party_id = CharField(max_length=25, null=True, help_text="申请方节点编码")
    apply_party_name = CharField(max_length=64, null=True, help_text="申请方节点名称")
    approve_party_id = CharField(max_length=25, null=True, help_text="授权方节点编码")
    approve_party_name = CharField(max_length=64, null=True, help_text="授权方节点名称")
    apply_time = DateTimeField(null=True, help_text="申请时间")
    approve_time = DateTimeField(null=True, help_text="审批时间")
    fusion_times_limits = BigIntegerField(help_text="求交次数限制数", null=True)
    fusion_deadline = DateField(help_text="截至日期", null=True)
    fusion_limit = BooleanField(help_text="融合上限", null=True, default=True)
    current_fusion_count = BigIntegerField(help_text="当前求交次数", null=True, default=0)
    total_fusion_count = BigIntegerField(help_text="总计求交次数", null=True, default=0)
    approve_result = CharField(max_length=1, help_text="审批状态(申请中0、同意1、拒绝2、取消授权3)", null=True, default=0)
    approve_username = CharField(max_length=32, help_text="授权用户名", null=True)
    owner = CharField(max_length=1, null=True, help_text="样本拥有者(0:本方、1:合作方)")
    algorithm_name =CharField(max_length=1024, null=True, help_text="算法名称")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_sample_authorize_history"


class StudioSampleFields(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    sample_id = CharField(max_length=32, null=True, help_text="本方参与样本id")
    field_name = CharField(max_length=255, null=True, help_text="特征名称")
    field_type = CharField(max_length=10, null=True, help_text="特征类型：int、float、str、bool")
    field_sort = IntegerField(null=True, help_text="特征head顺序")
    distribution_type = CharField(max_length=10, null=True, help_text="分布类型:离散型 、连续型")
    data_type = CharField(max_length=10, null=True, help_text="标签列: Y,ID,特征")
    field_description = CharField(max_length=255, null=True, help_text="特征描述")
    field_examples = CharField(max_length=512, null=True, help_text="特征值示例")
    positive_value = CharField(max_length=100, null=True, help_text="正例值")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_sample_fields"


class StudioSampleInfo(WebDataBaseModel):
    id = CharField(max_length=32, help_text="序号")
    party_id = CharField(max_length=10, null=True, help_text="样本所属节点编号")
    party_name = CharField(max_length=64, null=True, help_text="合作方名称")
    name = CharField(max_length=256, help_text="样本名称(默认表名或文件名)")
    comments = CharField(max_length=256, null=True, help_text="简介")
    type = CharField(null=True, max_length=20, help_text="类型(MYSQL, HDFS,本地文件)")
    node_name = CharField(max_length=100, null=True, help_text="文件系统节点名称")
    file_path = CharField(max_length=512, null=True, help_text="文件系统全路径名")
    # db_url = CharField(max_length=256, null=True, help_text="数据库地址")
    db_host = CharField(max_length=64, null=True, help_text="数据库IP")
    db_port = CharField(max_length=10, null=True, help_text="数据库端口")
    db_database = CharField(max_length=64, null=True, help_text="数据库名称")
    db_username = CharField(max_length=100, null=True, help_text="用户名")
    db_password = CharField(max_length=100, null=True, help_text="密码")
    db_tablename = CharField(max_length=100, null=True, help_text="表名称")
    db_dsn = CharField(max_length=100, null=True, help_text="服务名")
    sample_type = CharField(max_length=30, null=True, help_text="样本集类别(0纵向融合X样本,1纵向融合Y样本,2纵向融合仅ID值样本,3横向融合样本)")
    sample_count = BigIntegerField(null=True, help_text="样本记录数")
    # publish_status加入-1： 不可发布
    publish_status = CharField(max_length=30, null=True, help_text="发布状态：0未发布,1已发布", default="0")
    status = CharField(max_length=1, null=True, help_text="样本状态：0无效,1有效", default="1")
    owner = CharField(max_length=1, null=True, help_text="样本所有者：0本方,1合作方")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "studio_sample_info"
        primary_key = CompositeKey("party_id", "name")


class StudioSysLicense(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    start_date = CharField(max_length=50, null=True, help_text="证书开始时间")
    end_date = CharField(max_length=50, null=True, help_text="证书结束时间")
    ip = CharField(max_length=255, null=True, help_text="Ip服务地址")
    mac = CharField(max_length=255, null=True, help_text="Mac服务地址")
    cpu = CharField(max_length=255, null=True, help_text="Cpu服务信息")
    main_board = CharField(max_length=255, null=True, help_text="可被允许的主板序列号")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_sys_license"


class StudioVSampleInfo(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    v_name = CharField(max_length=255, null=True, help_text="融合数据名称")
    party_info = JSONField(null=True, help_text="任务参与方信息")
    mix_type = CharField(max_length=10, null=True, help_text="融合方式")
    job_id = CharField(max_length=25, help_text="任务id")
    party_id = CharField(max_length=10, help_text="参与方编码")
    component_name = CharField(max_length=50, help_text="组件名称")
    role = CharField(max_length=50, help_text="角色")
    sample_count = BigIntegerField(help_text="记录数")
    project_id =CharField(max_length=32, null=True, help_text="项目id")

    def __str__(self):
        return self.v_name

    class Meta:
        db_table = "studio_v_sample_info"


# 权限表
class StudioAuthUser(WebDataBaseModel, UserMixin):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    nickname = CharField(max_length=100, null=True, help_text="昵称")
    password = CharField(max_length=255, null=True, help_text="用户密码")
    username = CharField(max_length=100, null=True, help_text="登陆名称")
    alternative_id = CharField(max_length=32, null=True, help_text="备选id")
    status = CharField(max_length=1, null=True, help_text="用户状态(0无效，1有效)", default="1")
    is_superuser = BooleanField(null=True, help_text="是否是超级用户", default=False)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "studio_auth_user"

    def get_id(self):
        jwt = TimedJSONWebSignatureSerializer(secret_key=config.secret_key, expires_in=config.token_expires_in)
        return jwt.dumps(str(self.alternative_id)).decode()

    # @staticmethod
    # @classmethod
    def get_permission_code(self):
        # if current_user_obj:
        #     current_user_id = current_user_obj.id
        # else:
        #     current_user_id = current_user.id
        if self.is_superuser:
            query = StudioAuthPermission.select(StudioAuthPermission.code).distinct().dicts()
            return [i["code"] for i in query]
        else:
            user_extra_auth = StudioUserPermission.select(StudioUserPermission.permission_code).where(
                StudioUserPermission.user_id == self.id).distinct().dicts()
            user_role_permission = StudioUserRole. \
                select(StudioRolePermission.permission_code). \
                join(StudioRolePermission, JOIN.INNER, on=(StudioUserRole.role_id == StudioRolePermission.role_id)). \
                where(StudioUserRole.user_id == self.id). \
                distinct().dicts()
            user_extra_auth_code = [i["permission_code"] for i in user_extra_auth]
            user_role_permission_code = [i["permission_code"] for i in user_role_permission]
            return list(set(user_extra_auth_code + user_role_permission_code))

    def get_auth_projects(self):
        creator = current_user.username
        current_user_id = current_user.id

        if current_user.is_superuser:
            auth_projects = StudioProjectInfo. \
                select(StudioProjectInfo.id). \
                where(StudioProjectInfo.status == StatusEnum.VALID.value ). \
                distinct()
        else:
            auth_projects = StudioProjectInfo. \
                select(StudioProjectInfo.id). \
                join(StudioProjectUser, JOIN.LEFT_OUTER, on=(StudioProjectInfo.id == StudioProjectUser.project_id)). \
                where(StudioProjectInfo.status == StatusEnum.VALID.value,
                      (StudioProjectInfo.creator == creator) | (StudioProjectUser.user_id == current_user_id)). \
                distinct()
        if auth_projects:
            return [i["id"] for i in auth_projects.dicts()]
        return []

    def get_auth_canvas(cls):
        auth_projects = cls.get_auth_projects()
        if auth_projects:
            canvas = StudioProjectCanvas.select(StudioProjectCanvas.id). \
                where(StudioProjectCanvas.project_id.in_(auth_projects))
            if canvas:
                return [i["id"] for i in canvas.dicts()]
        return []


class StudioAuthRole(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    name = CharField(max_length=64, null=True, unique=True, help_text="角色名称")
    comments = CharField(max_length=128, null=True, help_text="备注")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "studio_auth_role"


class StudioAuthPermission(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    p_id = CharField(max_length=32, null=True, help_text="父节点")
    code = CharField(max_length=20, null=True, unique=True, help_text="功能代码")
    name = CharField(max_length=64, null=True, help_text="功能名称")
    menu_level = CharField(max_length=1, null=True, help_text="菜单层级")
    url = CharField(max_length=512, null=True, help_text="链接地址")
    img = CharField(max_length=512, null=True, help_text="图标名称")
    is_superuser_auth = BooleanField(null=True, default=False, help_text="超级用户独有的权限")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_auth_permission"


class StudioAuthGroup(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    name = CharField(max_length=64, null=True, help_text="用户组名称")
    comments = CharField(max_length=128, null=True, help_text="备注")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_auth_group"


class StudioUserRole(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    user_id = CharField(max_length=32, null=True, help_text="用户id")
    role_id = CharField(max_length=32, null=True, help_text="角色id")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_user_role"


class StudioUserGroup(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    user_id = CharField(max_length=32, null=True, help_text="用户id")
    group_id = CharField(max_length=32, null=True, help_text="用户组id")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_user_group"


class StudioRolePermission(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    role_id = CharField(max_length=32, null=True, help_text="角色id")
    permission_code = CharField(max_length=32, null=True, help_text="权限code")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_role_permission"


class StudioUserPermission(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    user_id = CharField(max_length=32, null=True, help_text="用户id")
    permission_code = CharField(max_length=32, null=True, help_text="权限code")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_user_permission"


class StudioAlgorithmInfo(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    name = CharField(max_length=32, null=True, help_text="名称")
    module_name = CharField(max_length=32, null=True, unique=True, help_text="算法模块名称")
    mix_type = CharField(max_length=1, null=True, help_text="融合方式:0求交，1求并")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_algorithm_info"


class StudioSampleAlgorithm(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    sample_id = CharField(max_length=32, null=True, help_text="样本名称")
    algorithm_id = CharField(max_length=32, null=True, help_text="算法id")
    module_name = CharField(max_length=32, null=True, help_text="算法模块名称")
    algorithm_name = CharField(max_length=32, null=True, help_text="算法名称")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_sample_algorithm"

class StudioEvent(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    p_id = CharField(max_length=32, null=True, help_text="父节点")
    code = CharField(max_length=20, null=True, unique=True, help_text="功能代码")
    name = CharField(max_length=64, null=True, help_text="功能名称")
    p_name = CharField(max_length=64, null=True, help_text="父节点名称")
    menu_level = CharField(max_length=1, null=True, help_text="菜单层级")
    log = BooleanField(null=True, help_text="日志")
    chain = BooleanField(null=True, help_text="上链")
    def __str__(self):
        return self.id
    class Meta:
        db_table = "studio_event"


class StudioEventHistory(WebDataBaseModel):
    id = CharField(max_length=32, primary_key=True, help_text="序号")
    event_class = CharField(max_length=32, null=True, help_text="事件分类")
    event_sub_class = CharField(max_length=20, null=True,  help_text="事件子类")
    event_is_success = CharField(max_length=64, null=True, help_text="事件结果success or failed")
    event_ret =  JSONField(null=True, help_text="事件失败时返回的结果")
    user_id = CharField(max_length=32, null=True, help_text="用户id")
    user_name = CharField(max_length=32, null=True, help_text="用户名称")
    session_id =CharField(max_length=128, null=True, help_text="会话id")
    client_ip=CharField(max_length=32, null=True, help_text="客户端ip")
    event_detail =   JSONField(null=True, help_text="请求参数")
    is_chain = BooleanField(null=True, help_text="是否上链")
    chain_ret = CharField(max_length=64, null=True, help_text="上链结果")
    def __str__(self):
        return self.id

    class Meta:
        db_table = "studio_event_history"



class SiteKeyInfo(WebDataBaseModel):
    party_id = CharField(max_length=10, index=True)
    key_name = CharField(max_length=10, index=True)
    key = LongTextField()

    class Meta:
        db_table = "studio_site_key_info"
        primary_key = CompositeKey('party_id', 'key_name')


@DB.connection_context()
def init_database_tables():
    members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    table_objs = []
    for name, obj in members:
        if obj != WebDataBaseModel and issubclass(obj, WebDataBaseModel):
            table_objs.append(obj)
    print("init web db")
    DB.create_tables(table_objs)


@DB.connection_context()
def init_database_tables():
    members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    table_objs = []
    create_failed_list = []
    for name, obj in members:
        if obj != WebDataBaseModel and issubclass(obj, WebDataBaseModel):
            table_objs.append(obj)
            LOGGER.info(f"start create table {obj.__name__}")
            try:
                obj.create_table()
                LOGGER.info(f"create table success: {obj.__name__}")
            except Exception as e:
                LOGGER.exception(e)
                create_failed_list.append(obj.__name__)
    if create_failed_list:
        LOGGER.info(f"create tables failed: {create_failed_list}")
        raise Exception(f"create tables failed: {create_failed_list}")
migrator = MySQLMigrator(DB)
#3.2的数据库 迁移
operations = [
    migrator.add_column('studio_v_sample_info', 'project_id', StudioVSampleInfo.project_id),
    migrator.drop_column('studio_v_sample_info', 'project_id')
]
for operation in operations:
    try:
        operation.run()
    except:
        pass

