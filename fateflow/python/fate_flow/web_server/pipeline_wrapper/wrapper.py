import json, re, copy

import numpy as np

from pipeline.component.nn.interface import DatasetParam
from pipeline.backend.pipeline import PipeLine
from pipeline.component import *
from typing import List, Dict, Tuple
from fate_flow.web_server.pipeline_wrapper import Factory
from pipeline.interface import Data, Model
from fate_flow.settings import stat_logger
from torch import nn
from torch import optim
from collections import OrderedDict
from pipeline import fate_torch_hook
from pipeline.component.nn import TrainerParam
import torch
fate_torch_hook(torch)


class WrapperParam:
    jid4reader: str
    cpn4reader: str = "outs"
    pid: int
    guest: int
    hosts: List[int]
    arbiter: int
    role: str = "guest"  # host, guest
    cmp_nm: str
    job_type: str = "hetero"  # hetero, homo
    host_readers: Dict[int, Tuple[str, str]] = {}  # host: (jid, cpn)


class WrapperBase(WrapperParam):
    def __init__(self, **kwargs):
        if not kwargs: kwargs = {}
        for k, v in kwargs.items(): self.__setattr__(k, v)
        # print(self.__dict__)

        if self.__dict__.get("guest", None): self.guest = int(self.guest)
        if self.__dict__.get("hosts", None): self.hosts = [int(h) for h in self.hosts]
        if self.__dict__.get("arbiter", None): self.arbiter = int(self.arbiter)

        g = self.__dict__.get("guest", None)
        h = self.__dict__.get("hosts", None)
        a = self.__dict__.get("arbiter", None)

        self.pip = (
            PipeLine()
                .set_initiator(role=self.role, party_id=int(self.pid))
                .set_roles(guest=g, host=h, arbiter=a)
        )
        self.reader = None
        if self.__dict__.get("cmp_nm", "").find("Homo")>= 0 or \
                self.__dict__.get("cmp_nm", "").find("homo")>= 0: self.job_type = "homo"

    def _set_cpn_party_param(self, cpn, guest_param=None, host_param=None):
        if guest_param and self.guest:
            cpn.get_party_instance(
                role="guest", party_id=int(self.guest)
            ).component_param(**guest_param)

        if host_param and self.hosts:
            host_param = {int(h):v for h, v in host_param.items()}
            for h in self.hosts:
                if not host_param.get(int(h)):
                    cpn.get_party_instance(
                        role="host", party_id=int(h)
                    ).component_param(need_run=False)
                else:
                    cpn.get_party_instance(
                        role="host", party_id=int(h)
                    ).component_param(**host_param[h])

    def setReader(self, gst_tab=None, host_tb=None):
        self.reader = Reader(name="reader")
        if not gst_tab and self.__dict__.get("jid4reader"):
            gst_tab = {
                "job_id": self.jid4reader,
                "component_name": self.cpn4reader,
                "data_name": "data"
            }
        if gst_tab:
            self.reader.get_party_instance(
                role="guest", party_id=self.guest
            ).component_param(table=gst_tab)

        if not host_tb: host_tb = {}
        for h in self.hosts:
            if not host_tb.get(str(h)):
                if int(h) in self.host_readers:

                    j, c = self.host_readers[int(h)]
                else:
                    j, c = self.jid4reader, self.cpn4reader
                host_tb[str(h)] = {"job_id": j,
                              "component_name": c,
                              "data_name": "data"
                              }
            self.reader.get_party_instance(
                role="host", party_id=h
            ).component_param(table=host_tb[str(h)])
        self.pip.add_component(self.reader)

    def exe(self,
            common_param=None,
            guest_only_param=None,
            host_only_param=None,
            asyn=True
            ):

        if common_param is None: common_param = {}
        def missing_impute(va):
            if not va:return va
            va_ = []
            if isinstance(va, str): va = va.split(",")
            for v in va:
                if isinstance(v, str):
                    try:
                        if v.find(".") >= 0:
                            v = float(v)
                        else:
                            v = int(v)
                    except Exception as e:
                        pass
                va_.append(v)
            return va_

        if guest_only_param and "missing_impute" in guest_only_param:
            guest_only_param["missing_impute"] = missing_impute(guest_only_param["missing_impute"])
        if host_only_param:
            for h,v in host_only_param.items():
                if "missing_impute" in v:
                    host_only_param[h]["missing_impute"] = missing_impute(v["missing_impute"])

        assert self.reader, "call setReader() before this."
        self.cmp_nm = self.cmp_nm.lower()
        _component = Factory(self.cmp_nm)(name="outs", **common_param)

        self._set_cpn_party_param(_component,
                                  guest_only_param,
                                  host_only_param
                                  #{h: host_only_param for h in self.hosts}
                                  )

        if self.cmp_nm not in ["reader"]:
            _component.validate()

            self.pip.add_component(
                _component,
                data=Data(data=self.reader.output.data)
            )
        self.pip.compile()
        #print(self.pip.get_train_conf())
        return self.pip.fit(asyn=asyn)


class MLWrapperBase(WrapperBase):
    split_param = None
    eva_param = None
    scr_param = None
    cv_param = None
    local_baseline = False
    def _clean_param(self, common_param):
        if common_param is None: common_param = {}

        if "split_param" in common_param: self.split_param = common_param.pop("split_param")
        if "eva_param" in common_param: self.eva_param = common_param.pop("eva_param")
        if "scd_param" in common_param: self.scr_param = common_param.pop("scd_param")
        if "use_local_baseline" in common_param: self.local_baseline = common_param.pop("use_local_baseline")
        if common_param.get("cv_param"): self.cv_param = common_param["cv_param"]

        assert not (self.split_param and \
                    (self.cv_param and self.cv_param.get("need_cv"))), \
            "Can't split data into training/validating/testing set with 'cross validation' at the same time"

        for fld in ["validation_freqs", "callback_param"]:
            if fld in common_param and not common_param.get(fld):
                del common_param[fld]

    def add_components(self, _component):
        assert self.reader, "call setReader() before this."
        eva_cpn = [_component.output.data]
        if self.cmp_nm.lower().find("means") > 0: eva_cpn = [_component.output.data.data[0]]
        if self.split_param:
            cmpnt = HomoDataSplit if self.job_type == "homo" else HeteroDataSplit
            cmpnt = cmpnt(name="data_split", **self.split_param)
            self.pip.add_component(
                cmpnt, data=Data(data=self.reader.output.data)
            )

            self.pip.add_component(
                _component,
                data=Data(train_data=cmpnt.output.data.train_data,
                          validate_data=cmpnt.output.data.validate_data)
            )

            if self.split_param.get("test_size", 0) > 0:
                _component1 = type(_component)(name=self.cmp_nm + "_test")
                self.pip.add_component(
                    _component1,
                    data=Data(test_data=cmpnt.output.data.test_data),
                    model=Model(model=_component.output.model)
                )
                eva_cpn.append(_component1.output.data)

        else:
            self.pip.add_component(
                _component,
                data=Data(train_data=self.reader.output.data)
            )

        if self.local_baseline:
            assert self.eva_param
            lb = LocalBaseline(name="localbaseline")
            self._set_cpn_party_param(lb,
                                      {"need_run": True},
                                      {h: {"need_run": False} for h in self.hosts}
                                      )
            self.pip.add_component(
                lb,
                data=Data(train_data=self.reader.output.data)
            )
            eva_cpn.append(lb.output.data)

        if self.eva_param:
            eva = Evaluation(name="evaluation", **self.eva_param)
            if self.cv_param and self.cv_param.get("need_cv"):
                for h in self.hosts:
                    eva.get_party_instance(
                        role="host", party_id=h
                    ).component_param(need_run=False)

            self.pip.add_component(
                eva,
                data=Data(data=eva_cpn)
            )

        if self.scr_param:
            scr = Scorecard(name="scorecard", **self.scr_param)
            for h in self.hosts:
                scr.get_party_instance(
                    role="host", party_id=h
                ).component_param(need_run=False)
            self.pip.add_component(
                scr,
                data=Data(data=eva_cpn[-1])
            )

    def exe(self,
            common_param=None,
            guest_only_param=None,
            host_only_param=None,
            asyn=True
            ):
        common_param = copy.deepcopy(common_param)
        self._clean_param(common_param)

        self.cmp_nm = self.cmp_nm.lower()
        _component = Factory(self.cmp_nm)(name="outs", **common_param)

        self._set_cpn_party_param(_component,
                                  guest_only_param,
                                  {h: host_only_param for h in self.hosts}
                                  )

        self.add_components(_component)

        self.pip.compile()
        return self.pip.fit(asyn=asyn)


def t_(jid,
       cmp_nm,
       cpn="outs",
       common_param=None,
       guest_only_param=None,
       host_only_param=None,
       split_param=None,
       cv_param=None,
       eva_param=None,
       scr_param=None,
       local_baseline=False,
       pid=9999, guest=9999, hosts=[10000],
       jtype="hetero",
       arbiter=10000,
       ml=True):

    if ml:
        job = MLWrapperBase(jid4reader=jid, cpn4reader=cpn,
                            cmp_nm=cmp_nm, pid=pid, guest=guest,
                            hosts=hosts, arbiter=arbiter, job_type=jtype)

        if cv_param: common_param["cv_param"] = cv_param
        common_param["eva_param"] = eva_param
        common_param["scd_param"] = scr_param
        common_param["split_param"] = split_param
        common_param["use_local_baseline"] = local_baseline
    else:
        job = WrapperBase(jid4reader=jid, cpn4reader=cpn,
                          cmp_nm=cmp_nm, pid=pid, guest=guest,
                          hosts=hosts, arbiter=arbiter, job_type=jtype)

    job.setReader()
    return job.exe(common_param, guest_only_param, host_only_param, asyn=False)

class UnionWrapper(WrapperBase):
    """
    After several data source selected, union them respectively in guest and hosts.
    """

    def exe(self, tables: List[Dict] = [],  # [{"name":"xxx", "namespace":"yyy"}]
            asyn=True):

        self.cmp_nm = "Union"

        dt = []
        for i, tb in enumerate(tables):
            reader = Reader(name=f"reader_guest_{i}")
            reader.get_party_instance(role='guest',
                                      party_id=self.guest).component_param(table=tb)

            self.pip.add_component(reader)
            dt.append(reader.output.data)

        if dt:
            union = Union(name="outs", allow_missing=True, keep_duplicate=False)
            self.pip.add_component(union, data=Data(data=dt))

        self.pip.compile()
        return self.pip.fit(asyn=self.asyn)


class DataTransformWrapper(WrapperBase):
    def setReader(self,
                  guest_tables: List[Dict[str, str]] = [],  # {"name":"xxx", "namespace":"yyy"} OR {"job_id":"xxxxx" }
                  host_tables: Dict[str, Dict] = {}  # "hostid":{"name":"xxx","namespace":"yyy"}
                  ):
        self.reader = []
        for i, gtb in enumerate(guest_tables):
            rdr = Reader(name=f"reader_{i}")
            if "job_id" in gtb:
                if not gtb.get("component_name"):
                    gtb["component_name"] = "outs"
                gtb["data_name"] = "data"

            self._set_cpn_party_param(rdr,
                                  {"table": gtb},
                                  {h: {"table": tb} for h, tb in host_tables.items()}
                                  )
            self.reader.append(rdr)
            self.pip.add_component(rdr)

        self.cmp_nm = "DataTransform"

    def exe(self,
            common_param=None,
            guest_only_param=None,
            host_only_param=None,
            asyn=True
            ):

        if common_param is None: common_param = {}

        assert self.reader, "call setReader() before this."

        if not host_only_param: host_only_param = {}
        for h in host_only_param.keys():
            host_only_param[h]["with_match_id"] = guest_only_param.get("with_match_id", False)

        dts = []
        for i, rdr in enumerate(self.reader):
            dt = DataTransform(name=("outs" if len(self.reader) == 1 else f"datatransform_{i}"))
            self._set_cpn_party_param(dt,
                                      guest_only_param,
                                      host_only_param#{h: host_only_param for h in self.hosts}
                                      )
            if i == 0:
                self.pip.add_component(dt, data=Data(data=rdr.output.data))
            else:
                self.pip.add_component(dt, data=Data(data=rdr.output.data),
                                       model=Model(dts[0].output.model))
            dts.append(dt)

        if len(dts) > 1:
            union_0 = Union(name="outs")
            self.pip.add_component(union_0, data=Data(data=[dt.output.data for dt in dts]))

        self.pip.compile()
        return self.pip.fit(asyn=asyn)


class EvaluationWrapper(WrapperBase):
    def setReader(self, jids, cpn_nms=[], mdl_nms=[], host_sample=[]):
        self.reader = []
        if mdl_nms:
            nms = []
            for n in mdl_nms:
                n = re.sub(r"_.*", "", n)
                if n not in nms:
                    nms.append(n)
                    continue
                for i in range(0, 100):
                    if f"{n}-{i}" in nms:continue
                    nms.append(f"{n}-{i}")
                    break
            mdl_nms = nms

        for i, jid in enumerate(jids):
            tb = {
                "job_id": jid,
                "component_name": "outs" if i + 1 > len(cpn_nms) else cpn_nms[i],
                "data_name": "data"
            }
            r = Reader(name=re.sub(r"(hetero|homo)", "", f"reader_{i}" if not mdl_nms else mdl_nms[i], flags=re.IGNORECASE))
            self._set_cpn_party_param(r,
                                      {"table": tb},
                                      {h: {"table": {"name":"breast_homo_host","namespace":f"experiment"}} for h in self.hosts} if not host_sample \
                                 else {host_sample[0] : {"table": {"name": host_sample[1],"namespace":f"experiment"}}}
                                      )

            self.pip.add_component(r)
            self.reader.append(r)

        self.cmp_nm = "Evaluation"

    def exe(self, eva_param=None,
            guest_only_param=None,
            host_only_param=None,
            asyn=True):
        if not eva_param: eva_param = {}
        eva_param["name"] = "outs"

        eva = Evaluation(**eva_param)
        self._set_cpn_party_param(eva,
                                  None,
                                  {h: {"need_run": False} for h in self.hosts}
                                  )
        self.pip.add_component(eva, data=Data(
            data=[r.output.data for r in self.reader]))
        self.pip.compile()
        return self.pip.fit(asyn=asyn)


class PredictWrapper(WrapperBase):
    def exe(self, mdl_param: dict,
            guest_only_param=None,
            host_only_param=None,
            asyn=True):
        # 多个job 包含多个组件
        # mdl_param: {
        #     "model_id": "guest-9999#host-10000#model",
        #     "model_versions": [
        #         ("202210201120144748370",["data_transform_0"]),
        #         # 多个feature selection 组件，model version和组件需要一一对应起来
        #         ("202210201120144748371",["hetero_feature_selection_0"])
        #     ]
        # }
        component_name_list = mdl_param["model_versions"]
        total = 0
        for c in component_name_list:
            total += len(c[1])
        previous_component = None
        # 多个job
        count = 0
        for i in range(len(component_name_list)):
            model_version, component_names = component_name_list[i]
            if re.match(r"(DataTransform|Intersection|Reader)", component_names[0], flags=re.IGNORECASE):
                total -= len(component_names)
                continue
            # 一个job中多个component
            for nm in component_names:
                mdlnm = nm.split(":")
                cnm = "outs" if len(mdlnm) == 1 else mdlnm[1]
                mdlnm = mdlnm[0]
                model_loader = ModelLoader(name=f"model_loader_{count}",
                                           component_name=cnm,
                                           model_id=mdl_param["model_id"],
                                           model_version=model_version)
                self.pip.add_component(model_loader)
                self.cmp_nm = mdlnm
                _component = Factory(self.cmp_nm)(name=(f"{mdlnm}_{count}" if count < total - 1 else "outs"))
                if count == 0:
                    if total > 1:
                        self.pip.add_component(_component, data=Data(data=self.reader.output.data),
                                           model=Model(model=model_loader.output.model))
                    else:
                        self.pip.add_component(_component, data=Data(test_data=self.reader.output.data),
                                           model=Model(model=model_loader.output.model))
                elif count < total - 1:
                    self.pip.add_component(_component, data=Data(data=previous_component.output.data),
                                           model=Model(model=model_loader.output.model))
                else:
                    self.pip.add_component(_component, data=Data(test_data=previous_component.output.data),
                                           model=Model(model=model_loader.output.model))
                previous_component = _component
                count += 1

        self.pip.compile()
        return self.pip.fit(asyn=asyn)


class PositiveUnlabeledWrapper(WrapperBase):
    def setReader(self, jids:list, cpn_nms=[], mdl_nms=[], host_sample=[]):
        assert len(jids) == 2, "必须有两个上游组件输入，一个是数据输入，另一个是模型输入。"
        self.reader = []
        if mdl_nms:
            nms = []
            for n in mdl_nms:
                n = re.sub(r"_.*", "", n)
                if n not in nms:
                    nms.append(n)
                    continue
                for i in range(0, 100):
                    if f"{n}-{i}" in nms:continue
                    nms.append(f"{n}-{i}")
                    break
            mdl_nms = nms

        data_i = 0
        for i in range(len(mdl_nms)):
            if not re.match(r"Hetero(LR|LinR|Poiss|NN|XGB|Light|K)", mdl_nms[i], flags=re.IGNORECASE):
                data_i = i
                break
        hst_tbl = {
            "job_id": jids[data_i],
            "component_name": "outs",
            "data_name": "data"
        }

        for i, jid in enumerate(jids):
            tb = {
                "job_id": jid,
                "component_name": "outs" if i + 1 > len(cpn_nms) else cpn_nms[i],
                "data_name": "data"
            }
            r = Reader(name=re.sub(r"(hetero|homo)", "", f"reader_{i}" if not mdl_nms else mdl_nms[i], flags=re.IGNORECASE))

            self._set_cpn_party_param(r,
                                      {"table": tb},
                                      {h: {"table": hst_tbl} for h in self.hosts}
                                      )

            self.pip.add_component(r)
            self.reader.append(r)

        self.cmp_nm = "PositiveUnlabeled"

    def exe(self, common_param=None,
            guest_only_param=None,
            host_only_param=None,
            asyn=True):
        if not common_param: common_param = {}
        common_param["name"] = "outs"

        _cpn = Factory(self.cmp_nm)(**common_param)
        self._set_cpn_party_param(_cpn,
                                  None,
                                  {h: {"need_run": False} for h in self.hosts}
                                  )
        self.pip.add_component(_cpn, data=Data(
            data=[r.output.data for r in self.reader]))
        self.pip.compile()
        return self.pip.fit(asyn=asyn)


class HeteroNNWrapper(MLWrapperBase):
    def exe(self, common_param=None,
            guest_only_param=None,
            host_only_param=None,
            asyn=True):
        assert self.reader, "call setReader() before this."
        common_param = copy.deepcopy(common_param)
        self._clean_param(common_param)

        self.cmp_nm = self.cmp_nm.lower()
        if not host_only_param: host_only_param = {}
        if common_param.get("host_bottom_nn"): host_only_param = common_param["host_bottom_nn"]

        nn_param = {"dataset": DatasetParam(dataset_name="table", flatten_label=True, label_dtype='long'), "coae_param": {"enable":True}}
        if common_param.get("task_type", "") == "regression": nn_param = {}
        for k in ["task_type", "epochs", "batch_size", "early_stop", "tol", "encrypt_param","predict_param", "interactive_layer_lr",
                 "floating_point_precision", "seed", "callback_param"]:
            if k not in common_param:continue
            nn_param[k] = common_param.pop(k)

        loss_reduction = "mean"
        if "reduction" in nn_param: loss_reduction = nn_param["reduction"]
        _cpn = Factory(self.cmp_nm)(name="outs", **nn_param)

        assert common_param["guest_bottom_nn"], "请配置本方网络！"
        assert not re.search(r"(drop|activa|pool)", common_param["guest_bottom_nn"][0][0].lower()), "第一层网络类型错误！"
        gst_nn = []
        for i,(nm,pa) in enumerate(common_param["guest_bottom_nn"]):
            gst_nn.append((nm+f"_{i}", layerFactory(nm)(**pa)))
        _cpn_gst = _cpn.get_party_instance(role='guest', party_id=int(self.guest))
        _cpn_gst.add_bottom_model(nn.Sequential(OrderedDict(gst_nn)))

        for h, host_param in host_only_param.items():
            h = int(re.sub(r"[^0-9]+", "", str(h)))
            if h not in self.hosts:continue
            hst_nn = []
            for i, (nm, pa) in enumerate(host_param):
                hst_nn.append((nm + f"_{i}", layerFactory(nm)(**pa)))
            _cpn.get_party_instance(role="host", party_id=int(h))\
                .add_bottom_model(nn.Sequential(OrderedDict(hst_nn)))

        _cpn.set_interactive_layer(
            nn.InteractiveLayer(host_num=len(host_only_param.keys()), **common_param["interactive_layer_param"])
        )

        gst_nn = []
        for i,(nm,pa) in enumerate(common_param["top_nn_param"]):
            gst_nn.append((nm+f"_{i}", layerFactory(nm)(**pa)))
        _cpn_gst.add_top_model(nn.Sequential(OrderedDict(gst_nn)))

        _cpn.compile(optimizerFactory(common_param["optimizer"])(lr=common_param["optimizer_learning_rate"]),
                     loss=lossFactory(common_param["loss"])(reduction=loss_reduction))

        self.add_components(_cpn)
        self.pip.compile()
        return self.pip.fit(asyn=asyn)


class HomoNNWrapper(MLWrapperBase):
    def exe(self, common_param=None,
            guest_only_param=None,
            host_only_param=None,
            asyn=True):
        assert self.reader, "call setReader() before this."
        common_param = copy.deepcopy(common_param)
        self._clean_param(common_param)
        self.cmp_nm = self.cmp_nm.lower()
        if not host_only_param: host_only_param = {}

        tr_param = {}
        for k in ["epochs", "batch_size", "early_stop", "tol", "secure_aggregate", "aggregate_every_n_epoch", "weighted_aggregation"]:
            if k not in common_param:continue
            tr_param[k] = common_param.pop(k)

        out_features = None
        for key,value in common_param['nn_define']['nn_define'][::-1]:
            if 'out_features' in value.keys():
                out_features = value['out_features']
                if out_features == 2:
                    value['out_features'] = 1
                    out_features = 1
                break

        gst_nn = []
        for i,(nm,pa) in enumerate(common_param["nn_define"]["nn_define"]):
            gst_nn.append((nm+f"_{i}", layerFactory(nm)(**pa)))

        # update by tjx 2023427
        if out_features and out_features>2:
            dataset = DatasetParam(dataset_name="table", flatten_label=True, label_dtype='long')
        else:
            dataset = DatasetParam(dataset_name="table")
        _cpn = Factory(self.cmp_nm)(name="outs",
                                    model=nn.Sequential(OrderedDict(gst_nn)),
                                    loss=lossFactory(common_param["loss"])(),
                                    optimizer=optimizerFactory(common_param["optimizer"])(
                                        lr=common_param["optimizer_learning_rate"]),
                                    dataset = dataset,
                                    torch_seed=100,
                                    callback_param=common_param.get("callback_param"),
                                    trainer=TrainerParam(trainer_name="fedavg_trainer", **tr_param))
        self.add_components(_cpn)
        self.pip.compile()
        return self.pip.fit(asyn=asyn)


def activationFactory(activation="sigmoid"):
    __map = {"GELU": nn.GELU,
             "Hardshrink": nn.Hardshrink,
             "LeakyReLU": nn.LeakyReLU,
             "LogSigmoid": nn.LogSigmoid,
             "LogSoftmax": nn.LogSoftmax,
             "PReLU": nn.PReLU,
             "RReLU": nn.RReLU,
             "ReLU": nn.ReLU,
             "ReLU6": nn.ReLU6,
             "SELU": nn.SELU,
             "Sigmoid": nn.Sigmoid,
             "Softmax": nn.Softmax,
             "Softmax2d": nn.Softmax2d,
             "Softmin": nn.Softmin,
             "Softplus": nn.Softplus,
             "Softshrink": nn.Softshrink,
             "Softsign": nn.Softsign,
             "Tanh": nn.Tanh,
             "Tanhshrink": nn.Tanhshrink
             }
    for k in list(__map.keys()): __map[k.lower()] = __map[k]
    if activation.lower() in ["logsoftmax", "softmax", "softmin"]:
        return __map[activation.lower()](1)
    return __map[activation.lower()]()


def layerFactory(nm):
    __map = {
        "Linear": nn.Linear,
        "Activation": activationFactory,
        "Dropout": nn.Dropout,
        "AlphaDropout": nn.AlphaDropout,
        "FeatureAlphaDropout": nn.FeatureAlphaDropout,
        "Conv1D": nn.Conv1d,
        "Conv2D": nn.Conv2d,
        "AvgPool1d": nn.AvgPool1d,
        "AvgPool2d": nn.AvgPool2d,
        "MaxPool1d": nn.MaxPool1d,
        "MaxPool2d": nn.MaxPool2d,
        "Embedding": nn.Embedding,
    }
    for k in list(__map.keys()): __map[k.lower()] = __map[k]
    return __map[nm.lower()]


def optimizerFactory(nm="AdamW"):
    __map = {"ASGD": optim.ASGD,
             "Adadelta": optim.ASGD,
             "Adagrad": optim.Adagrad,
             "Adam": optim.Adam,
             "AdamW": optim.AdamW,
             "Adamax": optim.Adamax,
             "LBFGS": optim.LBFGS,
             "NAdam": optim.NAdam,
             "RAdam": optim.RAdam,
             "RMSprop": optim.RMSprop,
             "Rprop": optim.Rprop,
             "SGD": optim.SGD,
             "SparseAdam": optim.SparseAdam
             }
    for k in list(__map.keys()): __map[k.lower()] = __map[k]
    return __map[nm.lower()]


def lossFactory(nm):
    __map = {
        "L1": nn.L1Loss,
        "NLL": nn.NLLLoss,
        "PoissonNLL": nn.PoissonNLLLoss,
        "KLDiv": nn.KLDivLoss,
        "MSE": nn.MSELoss,
        "BCE": nn.BCELoss,
        "BCEWithLogits": nn.BCEWithLogitsLoss,
        "HingeEmbedding": nn.HingeEmbeddingLoss,
        "MultiLabelMargin": nn.MultiLabelMarginLoss,
        "SmoothL1": nn.SmoothL1Loss,
        "SoftMargin": nn.SoftMarginLoss,
        "CrossEntropy": nn.CrossEntropyLoss,
        "MultiLabelSoftMargin": nn.MultiLabelSoftMarginLoss,
        "CosineEmbedding": nn.CosineEmbeddingLoss,
        "MarginRanking": nn.MarginRankingLoss,
        "MultiMargin": nn.MultiMarginLoss,
        "TripletMargin": nn.TripletMarginLoss,
        "CTC": nn.CTCLoss
    }
    for k in list(__map.keys()): __map[k.lower()] = __map[k]
    return __map[nm.lower()]
