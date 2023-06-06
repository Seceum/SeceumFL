
from pipeline.param.boosting_param import HeteroXGBoostParam
from pipeline.component.component_base import FateComponent
from pipeline.interface import Input
from pipeline.interface import Output
from pipeline.utils.logger import LOGGER


class HeteroXGBoost(FateComponent, HeteroXGBoostParam):

    def __init__(self, **kwargs):
        FateComponent.__init__(self, **kwargs)

        # print(self.name)
        LOGGER.debug(f"{self.name} component created")

        new_kwargs = self.erase_component_base_param(**kwargs)

        HeteroXGBoostParam.__init__(self, **new_kwargs)
        self.input = Input(self.name, data_type="multi")
        self.output = Output(self.name)
        self._module_name = "HeteroXGBoost"