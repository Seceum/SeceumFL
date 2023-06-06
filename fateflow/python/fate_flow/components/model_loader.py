#
#  Copyright 2021 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from fate_flow.components._base import (
    BaseParam, ComponentBase,
    ComponentInputProtocol, ComponentMeta,
)
from fate_flow.entity import MetricMeta, MetricType
from fate_flow.model.checkpoint import CheckpointManager
from fate_flow.model.sync_model import SyncComponent
from fate_flow.pipelined_model.pipelined_model import PipelinedModel
from fate_flow.settings import ENABLE_MODEL_STORE
from fate_flow.utils.log_utils import getLogger
from fate_flow.utils.model_utils import gen_party_model_id


LOGGER = getLogger()
model_loader_cpn_meta = ComponentMeta('ModelLoader')


@model_loader_cpn_meta.bind_runner.on_guest.on_host.on_arbiter
class ModelLoader(ComponentBase):
    """ ModelLoader is a component for loading models trained by previous jobs.

        `self.model_id`, `self.model_version`, `self.component_name` and `self.model_alias`
        come from the previous job. However, most of the data in `self.tracker` belongs to the current job.
        Such as `self.tracker.job_id`, `self.tracker.task_id`, `self.tracker.task_version`, etc.
        Be careful when using them.
    """

    def __init__(self):
        super().__init__()
        self.serialize = False

        self.model_id = None
        self.model_version = None
        self.component_name = None
        self.model_alias = None
        self.step_index = None
        self.step_name = None

    def read_component_model(self):
        pipelined_model = PipelinedModel(gen_party_model_id(
            self.model_id, self.tracker.role, self.tracker.party_id
        ), self.model_version)

        if self.model_alias is None:
            self.model_alias = pipelined_model.get_model_alias(self.component_name)

        component_model = pipelined_model._read_component_model(self.component_name, self.model_alias)
        if not component_model:
            raise ValueError('The component model is empty.')

        self.model_output = component_model
        self.tracker.set_metric_meta('model_loader', f'{self.component_name}-{self.model_alias}',
                                     MetricMeta('component_model', MetricType.COMPONENT_MODEL_INFO, {
                                         'model_id': self.model_id,
                                         'model_version': self.model_version,
                                         'component_name': self.component_name,
                                         'model_alias': self.model_alias,
                                     }))

    def read_checkpoint(self):
        checkpoint_manager = CheckpointManager(
            role=self.tracker.role, party_id=self.tracker.party_id,
            model_id=self.model_id, model_version=self.model_version,
            component_name=self.component_name,
        )
        checkpoint_manager.load_checkpoints_from_disk()

        if self.step_index is not None:
            checkpoint = checkpoint_manager.get_checkpoint_by_index(self.step_index)
        elif self.step_name is not None:
            checkpoint = checkpoint_manager.get_checkpoint_by_name(self.step_name)
        else:
            checkpoint = checkpoint_manager.latest_checkpoint

        if checkpoint is None:
            raise ValueError('The checkpoint was not found.')

        data = checkpoint.read(include_database=True)
        data['model_id'] = checkpoint_manager.model_id
        data['model_version'] = checkpoint_manager.model_version
        data['component_name'] = checkpoint_manager.component_name

        self.model_output = data.pop('models')
        self.tracker.set_metric_meta('model_loader', f'{checkpoint.step_index}-{checkpoint.step_name}',
                                     MetricMeta('checkpoint', MetricType.CHECKPOINT_INFO, data))

    def _run(self, cpn_input: ComponentInputProtocol):
        need_run = cpn_input.parameters.get('need_run', True)
        if not need_run:
            return

        for k in ('model_id', 'model_version', 'component_name'):
            v = cpn_input.parameters.get(k)
            if v is None:
                raise KeyError(f'The component ModelLoader needs "{k}"')
            setattr(self, k, v)

        for k in ('model_alias', 'step_index', 'step_name'):
            v = cpn_input.parameters.get(k)
            if v is not None:
                setattr(self, k, v)
                break

        if ENABLE_MODEL_STORE:
            sync_component = SyncComponent(
                role=self.tracker.role, party_id=self.tracker.party_id,
                model_id=self.model_id, model_version=self.model_version,
                component_name=self.component_name,
            )
            sync_component.download()

        if self.model_alias is not None:
            return self.read_component_model()

        if self.step_index is not None or self.step_name is not None:
            return self.read_checkpoint()

        try:
            return self.read_component_model()
        except Exception:
            try:
                return self.read_checkpoint()
            except Exception:
                raise EnvironmentError('Unable to find component model and checkpoint. '
                                       'Try specifying "model_alias", "step_index" or "step_name".')

@model_loader_cpn_meta.bind_param
class ModelLoaderParam(BaseParam):

    def __init__(self, model_id: str = None, model_version: str = None, component_name: str = None,
                 model_alias: str = None, step_index: int = None, step_name: str = None, need_run: bool = True):
        self.model_id = model_id
        self.model_version = model_version
        self.component_name = component_name
        self.model_alias = model_alias
        self.step_index = step_index
        self.step_name = step_name
        self.need_run = need_run

        if self.step_index is not None:
            self.step_index = int(self.step_index)

    def check(self):
        for i in ('model_id', 'model_version', 'component_name'):
            if getattr(self, i) is None:
                raise KeyError(f"The parameter '{i}' is required.")
