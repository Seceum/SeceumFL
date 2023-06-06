from fate_flow.web_server.pipeline_wrapper.wrapper import WrapperBase
from fate_flow.web_server.pipeline_wrapper import Factory
from pipeline.interface import Data


class PsiWrapper(WrapperBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.psi_component = None
        self.data_split = None
        self.psi_param = None
        self.split_param = None

    def _parse_param(self, param):
        self.psi_param = {
            "max_bin_num": param.get("max_bin_num", 20),
            "need_run": param.get("need_run", True),
            "dense_missing_val": param.get("dense_missing_val",None),
            # "binning_error": param.get("binning_error", 1e-4),
        }
        self.split_param = {
            "validate_size":0.2,
            "train_size":0.8
        }

    def exe(self, param,
            common_param=None,
            guest_only_param=None,
            host_only_param=None,
            asyn=True):
        
        self._parse_param(param)

        self.data_split = Factory("HomoDataSplit")(**self.split_param)
        self.pip.add_component(
            self.data_split,
            data=Data(self.reader.output.data)
        )

        self.psi_component = Factory(self.cmp_nm)(name="outs", **self.psi_param)
        self.pip.add_component(
            self.psi_component,
            data=Data(train_data=self.data_split.output.data.train_data,
                    validate_data=self.data_split.output.data.validate_data)
        )
        
        self.pip.compile()
        return self.pip.fit(asyn=asyn)
