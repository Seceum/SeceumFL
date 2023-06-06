
from federatedml.ensemble.basic_algorithms.decision_tree.hetero.hetero_leaf_wise_decision_tree_guest import \
    HeteroLeafWiseDecisionTreeGuest
from federatedml.param.hetero_lightgbm_param import HeteroLightGBMParam
from federatedml.ensemble.boosting.hetero.hetero_secureboost_guest import HeteroSecureBoostingTreeGuest
from federatedml.ensemble.basic_algorithms.decision_tree.tree_core.efb import EFB


class HeteroLightGBMGuest(HeteroSecureBoostingTreeGuest):

    def __init__(self):
        super(HeteroLightGBMGuest, self).__init__()
        self.model_param = HeteroLightGBMParam()
        self.efb = None
        self.run_efb = False
        self.categorical_features = []

    def _init_model(self, param: HeteroLightGBMParam):
        super(HeteroLightGBMGuest, self)._init_model(param)
        # TODO: categorical features
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
        super(HeteroLightGBMGuest, self).fit(data_inst, validate_data)

    def fit_a_booster(self, epoch_idx: int, booster_dim: int):
        """
        训练一棵按叶生长的决策树
        """
        if self.cur_epoch_idx != epoch_idx:
            self.grad_and_hess = self.compute_grad_and_hess(self.y_hat, self.y, self.data_inst)
            self.cur_epoch_idx = epoch_idx

        g_h = self.get_grad_and_hess(self.grad_and_hess, booster_dim)

        tree = HeteroLeafWiseDecisionTreeGuest(tree_param=self.tree_param)
        tree.init(flowid=self.generate_flowid(epoch_idx, booster_dim),
                  data_bin=self.data_bin, bin_split_points=self.bin_split_points,
                  bin_sparse_points=self.bin_sparse_points,
                  grad_and_hess=g_h,
                  encrypter=self.encrypter,
                  task_type=self.task_type,
                  valid_features=self.sample_valid_features(),
                  host_party_list=self.component_properties.host_party_idlist,
                  runtime_idx=self.component_properties.local_partyid,
                  goss_subsample=self.enable_goss,
                  top_rate=self.top_rate, other_rate=self.other_rate,
                  complete_secure=True if (self.cur_epoch_idx == 0 and self.complete_secure) else False,
                  cipher_compressing=self.cipher_compressing,
                  max_sample_weight=self.max_sample_weight,
                  new_ver=self.new_ver
                  )

        tree.fit()

        self.update_feature_importance(tree.get_feature_importance())

        return tree

    def predict(self, data_inst, ret_format='std'):
        if self.run_efb:
            data_inst = self.efb.transform(data_inst)
        return super(HeteroLightGBMGuest, self).predict(data_inst, ret_format)
