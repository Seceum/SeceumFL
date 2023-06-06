
from federatedml.param.boosting_param import HeteroSecureBoostParam,ObjectiveParam
from federatedml.param.encrypt_param import EncryptParam
from federatedml.param.encrypted_mode_calculation_param import EncryptedModeCalculatorParam
from federatedml.param.cross_validation_param import CrossValidationParam
from federatedml.param.predict_param import PredictParam
from federatedml.param.callback_param import CallbackParam
from federatedml.util import consts, LOGGER
import copy
from federatedml.param.boosting_param import DecisionTreeParam


class HeteroLightGBMParam(HeteroSecureBoostParam):

    def __init__(self, tree_param: DecisionTreeParam = DecisionTreeParam(), task_type=consts.CLASSIFICATION,
                 objective_param=ObjectiveParam(),
                 learning_rate=0.3, num_trees=5, subsample_feature_rate=1, n_iter_no_change=True,
                 tol=0.0001, encrypt_param=EncryptParam(),
                 bin_num=32,
                 encrypted_mode_calculator_param=EncryptedModeCalculatorParam(),
                 predict_param=PredictParam(), cv_param=CrossValidationParam(),
                 validation_freqs=None, early_stopping_rounds=None, use_missing=False, zero_as_missing=False,
                 complete_secure=False, metrics=None,
                 sparse_optimization=False, random_seed=100, binning_error=consts.DEFAULT_RELATIVE_ERROR,
                 cipher_compress_error=None, new_ver=True, run_goss=False, top_rate=0.2, other_rate=0.1,
                 cipher_compress=True, callback_param=CallbackParam(), run_efb=False):

        """
        Parameters
        ----------
        run_efb: bool
            Run EFB process or not
        """

        super(HeteroLightGBMParam, self).__init__(tree_param, task_type, objective_param, learning_rate,
                                                  num_trees, subsample_feature_rate, n_iter_no_change, tol,
                                                  encrypt_param, bin_num, encrypted_mode_calculator_param,
                                                  predict_param, cv_param, validation_freqs, early_stopping_rounds,
                                                  use_missing, zero_as_missing, complete_secure, metrics=metrics,
                                                  random_seed=random_seed,
                                                  sparse_optimization=sparse_optimization,
                                                  binning_error=binning_error,
                                                  cipher_compress_error=cipher_compress_error,
                                                  new_ver=new_ver,
                                                  cipher_compress=cipher_compress,
                                                  run_goss=run_goss, top_rate=top_rate, other_rate=other_rate)

        self.run_efb = run_efb  # 互斥特征绑定
        self.callback_param = copy.deepcopy(callback_param)

    def check(self):
        super(HeteroLightGBMParam, self).check()
        return True
