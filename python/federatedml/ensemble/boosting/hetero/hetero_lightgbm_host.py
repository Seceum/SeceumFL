
from federatedml.param.hetero_lightgbm_param import HeteroLightGBMParam
from federatedml.ensemble.basic_algorithms.decision_tree.hetero.hetero_leaf_wise_decision_tree_host import \
    HeteroLeafWiseDecisionTreeHost
from federatedml.ensemble.boosting.hetero.hetero_secureboost_host import HeteroSecureBoostingTreeHost
from federatedml.ensemble.basic_algorithms.decision_tree.tree_core.efb import EFB


class HeteroLightGBMHost(HeteroSecureBoostingTreeHost):

    def __init__(self):
        super(HeteroLightGBMHost, self).__init__()
        self.model_param = HeteroLightGBMParam()
        self.efb = None
        self.run_efb = False
        self.categorical_features = []

    def _init_model(self, param: HeteroLightGBMParam):
        super(HeteroLightGBMHost, self)._init_model(param)
        # TODO: categorical features
        # TODO: need efb
        self.run_efb = param.run_efb
        if self.run_efb:
            self.efb = EFB(self.categorical_features)

    def fit(self, data_inst, validate_data=None):
        # run EFB process
        if self.run_efb:
            self.efb.fit(data_inst)
            data_inst = self.efb.transform(data_inst)
            if validate_data is not None:
                validate_data = self.efb.transform(validate_data)
        super(HeteroLightGBMHost, self).fit(data_inst, validate_data)

    def fit_a_booster(self, epoch_idx: int, booster_dim: int):
        """
        训练一棵按叶生长的决策树
        """
        tree = HeteroLeafWiseDecisionTreeHost(tree_param=self.tree_param)
        tree.init(flowid=self.generate_flowid(epoch_idx, booster_dim),
                  valid_features=self.sample_valid_features(),
                  data_bin=self.data_bin, bin_split_points=self.bin_split_points,
                  bin_sparse_points=self.bin_sparse_points,
                  runtime_idx=self.component_properties.local_partyid,
                  goss_subsample=self.enable_goss,
                  bin_num=self.bin_num,
                  complete_secure=True if (self.complete_secure and epoch_idx == 0) else False,
                  cipher_compressing=self.cipher_compressing,
                  new_ver=self.new_ver
                  )
        tree.fit()
        return tree

    def predict(self, data_inst):
        if self.run_efb:
            data_inst = self.efb.transform(data_inst)
        return super(HeteroLightGBMHost, self).predict(data_inst)
