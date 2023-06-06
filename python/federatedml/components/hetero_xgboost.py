from .components import ComponentMeta

hetero_xgboost_cpn_meta = ComponentMeta("HeteroXGBoost")


@hetero_xgboost_cpn_meta.bind_param
def hetero_xgboost_param():
    from federatedml.param.hetero_xgboost_param import HeteroXGBoostParam

    return HeteroXGBoostParam


@hetero_xgboost_cpn_meta.bind_runner.on_guest
def hetero_xgboost_guest_runner():
    from federatedml.ensemble.boosting.hetero.hetero_xgboost_guest import (
        HeteroXGBoostGuest,
    )

    return HeteroXGBoostGuest


@hetero_xgboost_cpn_meta.bind_runner.on_host
def hetero_xgboost_host_runner():
    from federatedml.ensemble.boosting.hetero.hetero_xgboost_host import (
        HeteroXGBoostHost,
    )

    return HeteroXGBoostHost
