import copy

from fate_flow.web_server.pipeline_wrapper.wrapper import WrapperBase
from fate_flow.web_server.pipeline_wrapper import Factory
from .default_param import *
from pipeline.interface import Data, Model


class HeteroFeatureSelectionWrapper(WrapperBase):
    '''
    consts.STATISTIC_FILTER, consts.IV_FILTER, consts.PSI_FILTER,
                          consts.HETERO_SBT_FILTER, consts.HOMO_SBT_FILTER, consts.HETERO_FAST_SBT_FILTER,
                          consts.VIF_FILTER
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pearson_component = None
        self.bin_component = None
        self.psi_component = None
        self.statistic_component = None
        self.homo_sbt_component = None
        self.heter_sbt_component = None
        self.previous_model_lst = []

    def _get_feature_binning_component(self, binning_param):
        if self.bin_component is not None:
            return
        self.bin_component = Factory("HeteroFeatureBinning")(**binning_param)
        self.pip.add_component(
            self.bin_component,
            data=Data(data=self.reader.output.data)
        )
        self.previous_model_lst.append(self.bin_component.output.model)

    def _get_pearson_component(self, pearson_param):
        if self.pearson_component is not None:
            return
        self.pearson_component = Factory("HeteroPearson")(**pearson_param)
        self.pip.add_component(
            self.pearson_component,
            data=Data(data=self.reader.output.data)
        )
        self.previous_model_lst.append(self.pearson_component.output.model)

    def _base_feature_selection(self, selection_param, input_data, hst_param=None, asyn=True):

        _component = Factory(self.cmp_nm)(name="outs")#(**selection_param)
        self._set_cpn_party_param(_component, guest_param=selection_param, host_param=hst_param)
        self.pip.add_component(
            _component,
            data=Data(data=input_data),
            model=Model(isometric_model=[x for x in self.previous_model_lst])
        )
        self.pip.compile()
        return self.pip.fit(asyn=asyn)

    def _method_manully_selection(self, selection_param):
        self._base_feature_selection(selection_param, self.reader.output.data)

    def _method_iv_filter(self, binning_param):
        self._get_feature_binning_component(binning_param)
    
    def _method_psi_filter(self, psi_param):
        if self.psi_component is not None:
            return
        self.psi_component = Factory("PSI")(**psi_param)
        self.pip.add_component(
            self.psi_component,
            data=Data(train_data=self.reader.output.data,
                    validate_data=self.reader.output.data)
        )
        self.previous_model_lst.append(self.psi_component.output.model)

    def _method_vif_filter(self, pearson_param):
        self._get_pearson_component(pearson_param)

    def _method_statistic_filter(self, statistic_param):
        self.statistic_component = Factory("DataStatistics")(**statistic_param)
        self.pip.add_component(
            self.statistic_component,
            data=Data(data=self.reader.output.data)
        )
        self.previous_model_lst.append(self.statistic_component.output.model)

    def _method_correlation_filter(self, binning_param, pearson_param):
        self._get_feature_binning_component(binning_param)
        self._get_pearson_component(pearson_param)

    def _method_homo_sbt(self, homo_sbt_param):
        # self.homo_sbt_component = Factory("HomoSecureBoost")(**homo_sbt_param)
        self.homo_sbt_component = Factory("HomoXGBoost")(**homo_sbt_param)
        self.pip.add_component(
            self.homo_sbt_component,
            data=Data(train_data=self.reader.output.data)
        )
        self.previous_model_lst.append(self.homo_sbt_component.output.model)

    def _method_fast_sbt(self, fast_sbt_param):
        self.fast_sbt_component = Factory("HeteroFastSecureBoost")(**fast_sbt_param)
        self.pip.add_component(
            self.fast_sbt_component,
            data=Data(train_data=self.reader.output.data)
        )
        self.previous_model_lst.append(self.fast_sbt_component.output.model)

    def _method_hetero_sbt(self, hetero_sbt_param):
        self.heter_sbt_component = Factory("HeteroXGBoost")(**hetero_sbt_param)
        self.pip.add_component(
            self.heter_sbt_component,
            data=Data(train_data=self.reader.output.data)
        )
        self.previous_model_lst.append(self.heter_sbt_component.output.model)

    def exe(self, selection_param, guest_only_param=None, host_only_param=None, asyn=True):
        if not selection_param: selection_param = {}
        if not guest_only_param: guest_only_param = {}
        if not host_only_param: host_only_param = {}
        #update by tjx 202346
        for k in guest_only_param.keys():selection_param[k] = guest_only_param[k]
        selection_param["select_col_indexes"] = []
        if "filter_methods" not in selection_param:selection_param["filter_methods"] = []
        if selection_param.get("manually_param", {}).get("left_col_names"):selection_param["manually_param"]["left_col_names"] = None
        if selection_param.get("manually_param", {}).get("filter_out_names"):
            if "manually" not in selection_param["filter_methods"]:selection_param["filter_methods"].append("manually")
        else: selection_param["filter_methods"] = [m for m in selection_param["filter_methods"] if m != "manually"]

        mds = copy.deepcopy(selection_param.get('filter_methods', []))
        mds = set(mds)
        #if "correlation_filter" in mds and "iv_filter" not in mds:mds.add("iv_filter")
        mds = list(mds)

        for h in host_only_param.keys():
            # update by tjx 202346
            host_only_param[h]["select_col_indexes"] = []
            if not host_only_param[h]["select_names"]:
                host_only_param[h]["need_run"] = False
                continue
            if "filter_methods" not in host_only_param[h]: host_only_param[h]["filter_methods"] = []
            if host_only_param[h].get("manually_param", {}).get("left_col_names"): host_only_param[h]["manually_param"]["left_col_names"] = None
            if host_only_param[h].get("manually_param", {}).get("filter_out_names") and "manually" not in host_only_param[h]["filter_methods"]:
                host_only_param[h]["filter_methods"].append("manually")
            else: host_only_param[h]["filter_methods"] = [m for m in host_only_param[h]["filter_methods"] if m != "manually"]
            for m in mds:
                if m != "manually": host_only_param[h]["filter_methods"].append(m)
            #for m in host_only_param[h]["filter_methods"]: mds.append(m)


        sbt_param = copy.deepcopy(XGB_SBT_PARAM)
        for p in ["task_type", "objective", "learning_rate", "num_trees", "subsample_feature_rate", "n_iter_no_change", "tol", "bin_num", "random_seed", "binning_error"]:
            if p not in selection_param.get("sbt_param", {}):continue
            if p == "objective":
                sbt_param["objective_param"][p] =selection_param["sbt_param"].pop(p)
                if sbt_param["objective_param"][p] in ["huber", "fair", "tweedie"]:sbt_param["objective_param"]["params"] = [1,2]
                continue
            sbt_param[p] = selection_param["sbt_param"].pop(p)

        #selection_param["name"] = "outs"
        for method in mds:
            if method == 'iv_filter':
                self._method_iv_filter(BINNING_PARAM)
            elif method == 'psi_filter':
                self._method_psi_filter(PSI_PARAM)
            elif method == 'vif_filter':
                self._method_vif_filter(PEARSON_PARAM)
            elif method == 'statistic_filter':
                self._method_statistic_filter(STATISTIC_PARAM)
            elif method == 'correlation_filter':
                self._method_correlation_filter(BINNING_PARAM, PEARSON_PARAM)
            elif method == 'homo_sbt_filter':
                self._method_homo_sbt(HOMO_SBT_PARAM)
            elif method == 'hetero_fast_sbt_filter':
                self._method_fast_sbt(sbt_param)
            elif method == 'hetero_sbt_filter':
                self._method_hetero_sbt(sbt_param)
            elif method in ['manually', 'percentage_value']:
                pass
            else:
                raise ValueError(f"{method} is not supported!") 
        return self._base_feature_selection(selection_param, self.reader.output.data,host_only_param, asyn)
