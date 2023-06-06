import argparse

from pipeline.backend.pipeline import PipeLine
from pipeline.component import DataTransform
from pipeline.component import Intersection
from pipeline.component import Reader
from pipeline.interface import Data
from pipeline.utils.tools import load_job_config


def main(config="../../config.yaml",namespace=""):
    if isinstance(config,str):
        config = load_job_config(config)
    parties = config.parties
    guest = parties.guest[0]
    hosts = parties.host[0:1]

    guest_train_data = {"name":"breast_hetero_guest","namespace":f"experiment{namespace}"}
    # host_train_data = [{"name":"host_train_0004","namespace":f'experiment{namespace}'},
    #                    {"name":"host_train_0004","namespace":f'experiment{namespace}'}]
    host_train_data = [{"name":"breast_hetero_host","namespace":f'experiment{namespace}'}
        # ,
        #                {"name": "breast_hetero_host1", "namespace": f'experiment{namespace}'}
        # ,
        #                {"name": "breast_hetero_host2", "namespace": f'experiment{namespace}'},
        #                {"name": "breast_hetero_host3", "namespace": f'experiment{namespace}'}
                       ]

    pipeline = PipeLine().set_initiator(role="guest",party_id=guest).set_roles(guest=guest,host=hosts)

    reader_0 = Reader(name="reader_0")
    reader_0.get_party_instance(role="guest",party_id=guest).component_param(table=guest_train_data)
    reader_0.get_party_instance(role="host",party_id=hosts[0]).component_param(table=host_train_data[0])
    # reader_0.get_party_instance(role="host", party_id=hosts[1]).component_param(table=host_train_data[1])
    # reader_0.get_party_instance(role="host", party_id=hosts[2]).component_param(table=host_train_data[2])
    # reader_0.get_party_instance(role="host", party_id=hosts[3]).component_param(table=host_train_data[3])

    data_transform_0 = DataTransform(name='data_transform_0')
    data_transform_0.get_party_instance(role="guest",party_id=guest).component_param(with_label=False,output_format="dense")
    data_transform_0.get_party_instance(role="host",party_id=hosts[0]).component_param(with_label=False,output_format="dense")
    # data_transform_0.get_party_instance(role="host", party_id=hosts[1]).component_param(with_label=False,
    #                                                                                     output_format="dense")
    # data_transform_0.get_party_instance(role="host", party_id=hosts[2]).component_param(with_label=False,
    #                                                                                     output_format="dense")
    # data_transform_0.get_party_instance(role="host", party_id=hosts[3]).component_param(with_label=False,
    #                                                                                     output_format="dense")

    param = {
        "intersect_method":"bark-oprf",
        "sync_intersect_ids":True,
        "only_output_key":False,
        "bark_oprf_params":{
            "encrypt_method":"md5",
            "need_encrypt":True
        }
    }
    intersect_0 = Intersection(name="intersect_0",**param)
    pipeline.add_component(reader_0)
    # pipeline.add_component(data_transform_0,data=Data(data=reader_0.output.data))
    # pipeline.add_component(intersect_0,data=Data(data=data_transform_0.output.data))
    pipeline.add_component(intersect_0,data=Data(data=reader_0.output.data))

    pipeline.compile()
    pipeline.fit()

    print(pipeline.get_component('intersect_0').get_summary())


if __name__ == "__main__":
    main()