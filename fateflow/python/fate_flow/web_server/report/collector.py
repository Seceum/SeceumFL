
import re
import abc
import peewee
from fate_flow.operation.job_tracker import Tracker
from fate_flow.utils.api_utils import local_api
# # from fate_flow.web_server.utils.sample_util import *
from fate_flow.web_server.db_service.job_service import JobContentService
from fate_flow.web_server.blocks import BlockParser
from fate_flow.web_server.utils.sample_util import get_fusion_fields
from fate_flow.web_server.db_service.project_service import ProjectCanvasService,ProjectUsedSampleService
from fate_flow.web_server.db_service.sample_service import SampleFieldsService, SampleService, VSampleInfoService
from .common import BlockInfo
from .content import FateContent
from .consts import CollectorEnum
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.report.dataset_info import sample_analysis1
import os

class Collector:
    """
    获取Fate报告数据的基类
    """

    __collectors = {}

    def __init__(self, job_id: str, role: str, party_id: int, component_name: str):
        self.job_id: str = job_id
        self.role: str = role
        self.party_id: int = party_id
        self.component_name: str = component_name
        self.tracker = Tracker(job_id=self.job_id, component_name=self.component_name,
                               role=self.role, party_id=self.party_id)

    @abc.abstractmethod
    def collect(self, block_info: BlockInfo) -> dict:
        """
        获取报告数据的接口函数
        """
        raise NotImplementedError()

    def _use_fate_api(self, api_url):
        """
        调用Fate Web API获取报告数据
        """
        json_body = {
            'job_id': self.job_id,
            'role': self.role,
            'party_id': self.party_id,
            'component_name': self.component_name
        }
        # TODO: exception
        ret = local_api(self.job_id, 'POST', api_url, json_body)
        # add by tjx 20220628
        if api_url.find("/output/data") >= 0:
            return ret
        return ret['data']

    @staticmethod
    def register(type_: CollectorEnum):
        """
        用于注册子类的装饰器
        """
        def reg(cls_):
            Collector.__collectors[type_] = cls_
            return cls_
        return reg

    @staticmethod
    def create_collector(type_: CollectorEnum, jid: str, role: str, pid: int, cpt: str):
        """
        创建Collector对象的工厂方法
        """
        cls_ = Collector.__collectors[type_]
        return cls_(jid, role, pid, cpt)


@Collector.register(CollectorEnum.dummy)
class DummyCollector(Collector):
    """
    用于Mock数据
    TODO: 报告全部开发完成后应该移除该类
    """

    def collect(self, block_info: BlockInfo) -> dict:
        return {}

# add by tjx 20220819
@Collector.register(CollectorEnum.data1)
class Data1Collector(Collector):
    """
    样本分析报告中直方图数据
    """
    def collect(self, block_info: BlockInfo):
        job_id = self.job_id
        content_obj = JobContentService.get_or_none(job_id=job_id)
        if not content_obj:
            return {"data":["12211"]}
        # add by tjx 20220809
        canvas_obj = ProjectCanvasService.get_or_none(id=content_obj.canvas_id)
        if not canvas_obj:
            return {"data":["1000"]}
        # 2. 提取作业信息
        parser = BlockParser()
        parser.load(content_obj.run_param)
        job_meta = parser.get_party_info()
        # add by tjx 20220809
        mix_type = canvas_obj.job_type
        # 3. 生成统计信息
        # 以下代码搬运自fusion_fields()
        sample_list = get_fusion_fields(job_meta, mix_type)
        # add by tjx 20220810
        """
        基于job_id找到对应的样本数据 待测试

        """
        content_obj = ProjectUsedSampleService.get_or_none(job_id=job_id)
        sample_id = content_obj.sample_id
        content_obj = SampleService.get_or_none(id=sample_id)
        table_name = content_obj.name
        namespace = config.namespace
        endpoint = "/data/download"
        json_body = {
            "namespace": namespace,
            "table_name": table_name,
            "output_path": ''.join(["/data/", job_id, ".csv"])
        }
        if not os.path.exists(json_body["output_path"]):
            try:
                ret = local_api(job_id=job_id,
                            method='POST',
                            endpoint=endpoint,
                            json_body=json_body)

                if ret["retcode"]:
                    return {"data": ret["retmsg"]}
            except Exception as e:
                return {"data": ["1234"]}
            import time
            time.sleep(6)
        if not os.path.exists(json_body["output_path"]):
            return {"data": "file not exist"}

        if len(sample_list)>0:
            # add by tjx 20220810
            sample_list = sample_analysis1(sample_list, json_body["output_path"])
            # sample_list = gen_random_analysis(sample_list)
            return {"data":sample_list}
        else:
            return {"data":[]}


# add by tjx 20220811
@Collector.register(CollectorEnum.db_data3)
class DB3DataCollector(Collector):
    """
    融合样本基本信息获取，ok
    """
    def collect(self, block_info: BlockInfo):
        job_id = self.job_id
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
            return {"data": feature_info1}
        v_sample_obj = v_sample_objs[0]
        party_info = v_sample_obj.party_info
        feature_info = get_fusion_fields(party_info, v_sample_obj.mix_type)
        return {"data": feature_info}



# add by tjx 20220811
@Collector.register(CollectorEnum.db_data2)
class DB2DataCollector(Collector):
    """
    样本基本信息从数据库获取 待测试
    """
    def collect(self, block_info: BlockInfo):
        # job_id = self.job_id
        # content_obj = ProjectUsedSampleService.get_or_none(job_id=job_id)
        # sample_id = content_obj.sample_id
        data = {
            "base_info": {},
            "feature_info": {},
            "fusion_info": {}
        }
        # feature_cols = [SampleFieldsService.model.id, SampleFieldsService.model.sample_id,
        #                 SampleFieldsService.model.field_name,
        #                 SampleFieldsService.model.field_type, SampleFieldsService.model.distribution_type,
        #                 SampleFieldsService.model.data_type, SampleFieldsService.model.field_description]
        #
        # # 样本信息(所属节点、样本集类别、特征数量、样本记录数、描述)
        # # 元数据信息
        # sample_cols = [SampleService.model.id.alias("sample_id"), SampleService.model.name.alias("sample_name"),
        #                    SampleService.model.party_name, SampleService.model.sample_type,
        #                    SampleService.model.sample_count,
        #                    SampleService.model.comments]
        # sample_objs = SampleService.query(id=sample_id, cols=sample_cols)
        # if not sample_objs:
        #     return {"data":{}}
        data["base_info"]={"sample_id":"afdafd","sample_name":"afad","party_name":"local","sample_type":"1",
                           "sample_count":123,"comments":"自己使用"}
        # data["base_info"] = sample_objs[0].to_dict()
        # feature_info = list(SampleFieldsService.query(sample_id=sample_id, cols=feature_cols).dicts())
        # data["feature_info"] = feature_info
        data["feature_info"] = [{"id":1,"sample_id":"afd","field_name":1,"field_type":23,"distribution_type":12,
                                 "data_type":"int","field_description":"afdafd"},{"id":1,"sample_id":"afd","field_name":1,"field_type":23,"distribution_type":12,
                                 "data_type":"int","field_description":"afdafd"}]
        # data["base_info"]["feature_count"] = len(list(filter(lambda x: x["data_type"] == "特征", feature_info)))
        data["base_info"]["feature_count"] = 12
        return {"data":data}

# add by tjx 20220624
@Collector.register(CollectorEnum.db_data)
class DBDataCollector(Collector):
    """
    获取数据库中的数据
    """
    def collect(self, block_info: BlockInfo)->dict:
        # job_id = self.job_id
        # try:
        #     content_obj = JobContentService.get_or_none(job_id=job_id)
        # except peewee.DoesNotExist:
        #     content_obj = None
        # if not content_obj:
        #     return {"data":None}
        # # add by tjx 20220809
        # canvas_obj = ProjectCanvasService.get_or_none(id=content_obj.canvas_id)
        # if not canvas_obj:
        #     return {"data":None}
        # parser = BlockParser()
        # parser.load(content_obj.run_param)
        # job_meta = parser.get_party_info()
        # mix_type = canvas_obj.job_type
        # #获取样本字段信息 这个地方的数据暂时拿不到，需要后面优化处理20220805
        # sample_list = get_fusion_fields(job_meta,mix_type)
        return {"data":{}}


@Collector.register(CollectorEnum.data)
class DataCollector(Collector):
    """
    获取Fate组件的输出数据
    """

    API_URL = '/tracking/component/output/data'

    def collect(self, block_info: BlockInfo) -> dict:
        # TODO: use Tacker instead of Web API
        return self._use_fate_api(self.API_URL)


@Collector.register(CollectorEnum.model)
class ModelCollector(Collector):
    """
    获取Fate组件的输出模型
    """

    API_URL = '/tracking/component/output/model'

    def collect(self, block_info: BlockInfo) -> dict:
        # TODO: use Tacker instead of Web API
        return self._use_fate_api(self.API_URL)


class MetricMixin:
    """
    获取输出指标时的工具函数集
    """

    def get_metric_all_data(self, metric_namespace, metric_name):
        """
        获取某个评估指标的报告数据

        此函数搬运自fate_flow.apps.tracking_app.py
        搬运的原因是该文件内的manager装饰器导致导入时报错
        """
        metric_data = self.tracker.get_metric_data(metric_namespace=metric_namespace, metric_name=metric_name)
        metric_meta = self.tracker.get_metric_meta(metric_namespace=metric_namespace, metric_name=metric_name)
        if metric_data or metric_meta:
            metric_data_list = [(metric.key, metric.value) for metric in metric_data]
            metric_data_list.sort(key=lambda x: x[0])
            return metric_data_list, metric_meta.to_dict() if metric_meta else {}
        else:
            return [], {}

    def get_namespace_data(self, namespace: str, contents: list):
        """
        获取训练集或验证集中的报告数据
        """
        for content in contents:
            metric_data, metric_meta = self.get_metric_all_data(metric_name=content, metric_namespace=namespace)
            if metric_data or metric_meta[FateContent.name]:
                self.fate_report_data[namespace][content] = {
                    FateContent.data: metric_data,
                    FateContent.meta: metric_meta
                }


@Collector.register(CollectorEnum.metric)
class MetricCollector(Collector, MetricMixin):
    """
    获取Fate组件的输出指标
    """

    def collect(self, block_info: BlockInfo) -> dict:
        """
        参考了fate_flow.apps.tracking_app.py
        """
        metrics = self.tracker.get_metric_list()
        all_metric_data = {}
        if metrics:
            for metric_namespace, metric_names in metrics.items():
                all_metric_data[metric_namespace] = all_metric_data.get(metric_namespace, {})
                for metric_name in metric_names:
                    all_metric_data[metric_namespace][metric_name] = all_metric_data[metric_namespace].get(metric_name, {})
                    metric_data, metric_meta = self.get_metric_all_data(metric_namespace=metric_namespace,
                                                                        metric_name=metric_name)
                    all_metric_data[metric_namespace][metric_name]['data'] = metric_data
                    all_metric_data[metric_namespace][metric_name]['meta'] = metric_meta
        return all_metric_data


@Collector.register(CollectorEnum.cv_metric)
class CVMetricCollector(Collector, MetricMixin):
    """
    获取Fate组件的交叉验证指标
    """

    # 报告项的类别名
    fate_cv_curve = [
        FateContent.ks_tpr,
        FateContent.ks_fpr,
        FateContent.precision,
        FateContent.recall
    ]

    def __init__(self, job_id: str, role: str, party_id: int, component_name: str):
        super(CVMetricCollector, self).__init__(job_id, role, party_id, component_name)
        self.fate_report_data = {
            FateContent.train: {},
            FateContent.validate: {},
        }

    def collect(self, block_info: BlockInfo) -> dict:
        """
        交叉验证时的数据很多，因此逐项获取
        """
        train_contents = self._gen_fate_contents(block_info.n_split, FateContent.train)
        self.get_namespace_data(FateContent.train, train_contents)
        validate_contents = self._gen_fate_contents(block_info.n_split, FateContent.validate)
        self.get_namespace_data(FateContent.validate, validate_contents)
        return self.fate_report_data

    @classmethod
    def _gen_fate_contents(cls, n_split: int, namespace: str) -> list:
        """
        报告项在Fate报告中的实际名称，根据报告项类别名生成
        """
        contents = []
        for i in range(n_split):
            prefix = f'{namespace}_{FateContent.fold}_{i}'
            contents.append(prefix)
            contents.extend([f'{prefix}_{name}' for name in cls.fate_cv_curve])
        # Loss curve only exists in train data
        if namespace == FateContent.train:
            loss = [f'{FateContent.loss}.{i}' for i in range(n_split)]
            contents.extend(loss)
        return contents


@Collector.register(CollectorEnum.iter_metric)
class IterMetricCollector(Collector, MetricMixin):
    """
    获取Fate组件的迭代数据

    Boosting类算法，其组件报告中有iteration相关的内容，iteration的次数
    又可能与输入参数设定的不符，所以需要单独实现一个类来获取所有iteration
    的报告内容
    """

    def __init__(self, job_id: str, role: str, party_id: int, component_name: str):
        super(IterMetricCollector, self).__init__(job_id, role, party_id, component_name)
        self.fate_report_data = {
            FateContent.train: {},
            FateContent.validate: {},
        }

    def collect(self, block_info: BlockInfo) -> dict:
        """
        迭代的数据很多，因此逐项获取
        """
        metrics = self.tracker.get_metric_list()
        if not metrics:
            return {}
        iterations = self._get_all_iterations(metrics[FateContent.train])
        block_info.n_iter = len(iterations)
        self.get_namespace_data(FateContent.train, iterations)
        self.get_namespace_data(FateContent.validate, iterations)
        return self.fate_report_data

    @ staticmethod
    def _get_all_iterations(metrics: list):
        """
        通过正则表达式，获取实际的迭代次数
        """
        pattern = re.compile(r'iteration_\d+')
        return [iteration for iteration in metrics if pattern.fullmatch(iteration)]
