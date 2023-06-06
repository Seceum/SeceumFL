from federatedml.param.base_param import deprecated_param
from federatedml.param.boosting_param import HeteroBoostingParam,DecisionTreeParam,ObjectiveParam
from federatedml.param.encrypt_param import EncryptParam
from federatedml.param.encrypted_mode_calculation_param import EncryptedModeCalculatorParam
from federatedml.param.cross_validation_param import CrossValidationParam
from federatedml.param.predict_param import PredictParam
from federatedml.param.callback_param import CallbackParam
from federatedml.util import consts
import copy

hetero_deprecated_param_list = ["early_stopping_rounds", "validation_freqs", "metrics", "use_first_metric_only"]


@deprecated_param(*hetero_deprecated_param_list)
class HeteroXGBoostParam(HeteroBoostingParam):
    """
    Define boosting tree parameters that used in federated ml.

    Parameters
    ----------
    task_type : {'classification', 'regression'}, default: 'classification'
        task type

    tree_param : DecisionTreeParam Object, default: DecisionTreeParam()
        tree param

    objective_param : ObjectiveParam Object, default: ObjectiveParam()
        objective param

    learning_rate : float, int or long
        the learning rate of secure boost. default: 0.3

    num_trees : int or float
        the max number of trees to build. default: 5

    subsample_feature_rate : float
        a float-number in [0, 1], default: 1.0

    random_seed: int
        seed that controls all random functions

    n_iter_no_change : bool,
        when True and residual error less than tol, tree building process will stop. default: True

    encrypt_param : EncodeParam Object
        encrypt method use in secure boost, default: EncryptParam(), this parameter
        is only for hetero-secureboost

    bin_num: positive integer greater than 1
        bin number use in quantile. default: 32

    encrypted_mode_calculator_param: EncryptedModeCalculatorParam object
        the calculation mode use in secureboost, default: EncryptedModeCalculatorParam(), only for hetero-secureboost

    use_missing: bool
        use missing value in training process or not. default: False

    zero_as_missing: bool
        regard 0 as missing value or not, will be use only if use_missing=True, default: False

    validation_freqs: None or positive integer or container object in python
        Do validation in training process or Not.
        if equals None, will not do validation in train process;
        if equals positive integer, will validate data every validation_freqs epochs passes;
        if container object in python, will validate data if epochs belong to this container.
        e.g. validation_freqs = [10, 15], will validate data when epoch equals to 10 and 15.
        Default: None
        The default value is None, 1 is suggested. You can set it to a number larger than 1 in order to
        speed up training by skipping validation rounds. When it is larger than 1, a number which is
        divisible by "num_trees" is recommended, otherwise, you will miss the validation scores
        of last training iteration.

    early_stopping_rounds: integer larger than 0
        will stop training if one metric of one validation data
        doesn’t improve in last early_stopping_round rounds，
        need to set validation freqs and will check early_stopping every at every validation epoch,

    metrics: list, default: []
        Specify which metrics to be used when performing evaluation during training process.
        If set as empty, default metrics will be used. For regression tasks, default metrics are
        ['root_mean_squared_error', 'mean_absolute_error']， For binary-classificatiin tasks, default metrics
        are ['auc', 'ks']. For multi-classification tasks, default metrics are ['accuracy', 'precision', 'recall']

    use_first_metric_only: bool
        use only the first metric for early stopping

    complete_secure: bool
        if use complete_secure, when use complete secure, build first tree using only guest features

    sparse_optimization:
        this parameter is abandoned in FATE-1.7.1

    run_goss: bool
        activate Gradient-based One-Side Sampling, which selects large gradient and small
        gradient samples using top_rate and other_rate.

    top_rate: float
        the retain ratio of large gradient data, used when run_goss is True

    other_rate: float
        the retain ratio of small gradient data, used when run_goss is True

    cipher_compress_error: {None}
        This param is now abandoned

    cipher_compress: bool
        default is True, use cipher compressing to reduce computation cost and transfer cost

    """

    def __init__(self, tree_param: DecisionTreeParam = DecisionTreeParam(), task_type=consts.CLASSIFICATION,
                 objective_param=ObjectiveParam(),
                 learning_rate=0.3, num_trees=5, subsample_feature_rate=1.0, n_iter_no_change=True,
                 tol=0.0001, encrypt_param=EncryptParam(),
                 bin_num=32,
                 encrypted_mode_calculator_param=EncryptedModeCalculatorParam(),
                 predict_param=PredictParam(), cv_param=CrossValidationParam(),
                 validation_freqs=None, early_stopping_rounds=None, use_missing=False, zero_as_missing=False,
                 complete_secure=False, metrics=None, use_first_metric_only=False, random_seed=100,
                 binning_error=consts.DEFAULT_RELATIVE_ERROR,
                 sparse_optimization=False, run_goss=False, top_rate=0.2, other_rate=0.1,
                 cipher_compress_error=None, cipher_compress=True, new_ver=True,
                 callback_param=CallbackParam()):

        super(HeteroXGBoostParam, self).__init__(task_type, objective_param, learning_rate, num_trees,
                                                     subsample_feature_rate, n_iter_no_change, tol, encrypt_param,
                                                     bin_num, encrypted_mode_calculator_param, predict_param, cv_param,
                                                     validation_freqs, early_stopping_rounds, metrics=metrics,
                                                     use_first_metric_only=use_first_metric_only,
                                                     random_seed=random_seed,
                                                     binning_error=binning_error)

        self.tree_param = copy.deepcopy(tree_param)
        self.zero_as_missing = zero_as_missing
        self.use_missing = use_missing
        self.complete_secure = complete_secure
        self.sparse_optimization = sparse_optimization
        self.run_goss = run_goss
        self.top_rate = top_rate
        self.other_rate = other_rate
        self.cipher_compress_error = cipher_compress_error
        self.cipher_compress = cipher_compress
        self.new_ver = new_ver
        self.callback_param = copy.deepcopy(callback_param)

    def check(self):

        super(HeteroXGBoostParam, self).check()
        self.tree_param.check()
        if type(self.use_missing) != bool:
            raise ValueError('use missing should be bool type')
        if type(self.zero_as_missing) != bool:
            raise ValueError('zero as missing should be bool type')
        self.check_boolean(self.complete_secure, 'complete_secure')
        self.check_boolean(self.run_goss, 'run goss')
        self.check_decimal_float(self.top_rate, 'top rate')
        self.check_decimal_float(self.other_rate, 'other rate')
        self.check_positive_number(self.other_rate, 'other_rate')
        self.check_positive_number(self.top_rate, 'top_rate')
        self.check_boolean(self.new_ver, 'code version switcher')
        self.check_boolean(self.cipher_compress, 'cipher compress')

        #for p in ["early_stopping_rounds", "validation_freqs", "metrics",
        #          "use_first_metric_only"]:
        #    # if self._warn_to_deprecate_param(p, "", ""):
        #    if self._deprecated_params_set.get(p):
        #        if "callback_param" in self.get_user_feeded():
        #            raise ValueError(f"{p} and callback param should not be set simultaneously，"
        #                             f"{self._deprecated_params_set}, {self.get_user_feeded()}")
        #        else:
        #            self.callback_param.callbacks = ["PerformanceEvaluate"]
        #        break

        descr = "boosting_param's"

        if self._warn_to_deprecate_param("validation_freqs", descr, "callback_param's 'validation_freqs'"):
            self.callback_param.validation_freqs = self.validation_freqs
            #self.validation_freqs = None

        if self._warn_to_deprecate_param("early_stopping_rounds", descr, "callback_param's 'early_stopping_rounds'"):
            self.callback_param.early_stopping_rounds = self.early_stopping_rounds
            #self.early_stopping_rounds = None

        if self._warn_to_deprecate_param("metrics", descr, "callback_param's 'metrics'"):
            self.callback_param.metrics = self.metrics
            #self.metrics = []

        if self._warn_to_deprecate_param("use_first_metric_only", descr, "callback_param's 'use_first_metric_only'"):
            self.callback_param.use_first_metric_only = self.use_first_metric_only
            #self.use_first_metric_only = False

        if self.top_rate + self.other_rate >= 1:
            raise ValueError('sum of top rate and other rate should be smaller than 1')

        return True