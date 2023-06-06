
from .components import ComponentMeta

hetero_lightGBM_cpn_meta = ComponentMeta("HeteroLightGBM")


@hetero_lightGBM_cpn_meta.bind_param
def hetero_lightgbm_param():
    from federatedml.param.hetero_lightgbm_param import HeteroLightGBMParam

    return HeteroLightGBMParam


@hetero_lightGBM_cpn_meta.bind_runner.on_guest
def hetero_lightgbm_guest_runner():
    from federatedml.ensemble.boosting.hetero.hetero_lightgbm_guest import (
        HeteroLightGBMGuest,
    )

    return HeteroLightGBMGuest


@hetero_lightGBM_cpn_meta.bind_runner.on_host
def hetero_lightgbm_host_runner():
    from federatedml.ensemble.boosting.hetero.hetero_lightgbm_host import (
        HeteroLightGBMHost,
    )

    return HeteroLightGBMHost
