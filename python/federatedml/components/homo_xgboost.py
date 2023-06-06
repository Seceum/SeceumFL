#author_='seceum'

from .components import ComponentMeta

homo_xgboost_cpn_meta = ComponentMeta("HomoXGBoost", "HomoXGBoost")


@homo_xgboost_cpn_meta.bind_param
def homo_xgboost_param():
    from federatedml.param.homo_xgboost_param import HomoXGBoostParam

    return HomoXGBoostParam


@homo_xgboost_cpn_meta.bind_runner.on_guest.on_host
def homo_xgboost_runner_client():
    from federatedml.ensemble.boosting.homo.homo_xgboost_client  import (
        HomoXGBoostingTreeClient,
    )
    return HomoXGBoostingTreeClient


@homo_xgboost_cpn_meta.bind_runner.on_arbiter
def homo_xgboost_runner_arbiter():
    from federatedml.ensemble.boosting.homo.homo_xgboost_arbiter import (
        HomoXGBoostingTreeArbiter,
    )

    return HomoXGBoostingTreeArbiter
