#author_='seceum'

from federatedml.param.base_param import deprecated_param
from federatedml.param.boosting_param import BoostingParam, DecisionTreeParam, ObjectiveParam
from federatedml.param.cross_validation_param import CrossValidationParam
from federatedml.param.predict_param import PredictParam
from federatedml.param.callback_param import CallbackParam
from federatedml.util import consts
import copy


homo_deprecated_param_list = ["validation_freqs", "metrics"]

@deprecated_param(*homo_deprecated_param_list)
class HomoXGBoostParam(BoostingParam):

    """
    Parameters
    ----------
    backend: {'distributed', 'memory'}
        decides which backend to use when computing histograms for homo-xgboost
    """

    def __init__(self, tree_param: DecisionTreeParam = DecisionTreeParam(), task_type=consts.CLASSIFICATION,
                 objective_param=ObjectiveParam(),
                 learning_rate=0.3, num_trees=5, subsample_feature_rate=1, n_iter_no_change=True,
                 tol=0.0001, bin_num=32, predict_param=PredictParam(), cv_param=CrossValidationParam(),
                 validation_freqs=None, use_missing=False, zero_as_missing=False, random_seed=100,
                 binning_error=consts.DEFAULT_RELATIVE_ERROR, backend=consts.DISTRIBUTED_BACKEND,
                 callback_param=CallbackParam()):
        super(HomoXGBoostParam, self).__init__(task_type=task_type,
                                                   objective_param=objective_param,
                                                   learning_rate=learning_rate,
                                                   num_trees=num_trees,
                                                   subsample_feature_rate=subsample_feature_rate,
                                                   n_iter_no_change=n_iter_no_change,
                                                   tol=tol,
                                                   bin_num=bin_num,
                                                   predict_param=predict_param,
                                                   cv_param=cv_param,
                                                   validation_freqs=validation_freqs,
                                                   random_seed=random_seed,
                                                   binning_error=binning_error
                                                   )
        self.use_missing = use_missing
        self.zero_as_missing = zero_as_missing
        self.tree_param = copy.deepcopy(tree_param)
        self.backend = backend
        self.callback_param = copy.deepcopy(callback_param)

    def check(self):

        super(HomoXGBoostParam, self).check()
        self.tree_param.check()
        if type(self.use_missing) != bool:
            raise ValueError('use missing should be bool type')
        if type(self.zero_as_missing) != bool:
            raise ValueError('zero as missing should be bool type')
        if self.backend not in [consts.MEMORY_BACKEND, consts.DISTRIBUTED_BACKEND]:
            raise ValueError('unsupported backend')

        # for p in ["validation_freqs", "metrics"]:
        #     if self._deprecated_params_set.get(p):
        #         if "callback_param" in self.get_user_feeded():
        #             raise ValueError(f"{p} and callback param should not be set simultaneously，"
        #                              f"{self._deprecated_params_set}, {self.get_user_feeded()}")
        #         else:
        #             self.callback_param.callbacks = ["PerformanceEvaluate"]
        #         break

        descr = "boosting_param's"

        if self._warn_to_deprecate_param("validation_freqs", descr, "callback_param's 'validation_freqs'"):
            self.callback_param.validation_freqs = self.validation_freqs
            #self.validation_freqs = None

        if self._warn_to_deprecate_param("metrics", descr, "callback_param's 'metrics'"):
            self.callback_param.metrics = self.metrics
            #self.metrics = []

        return True
