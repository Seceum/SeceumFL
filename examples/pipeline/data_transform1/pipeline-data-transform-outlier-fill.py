#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
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

import argparse


from pipeline.backend.pipeline import PipeLine
from pipeline.component import DataTransform1
from pipeline.component import DataTransform
from pipeline.component import DataStatistics
from pipeline.component import Reader
from pipeline.component import Intersection
from pipeline.interface import Data
from pipeline.utils.tools import load_job_config


def main(config="../../config.yaml", namespace=""):
    # obtain config
    if isinstance(config, str):
        config = load_job_config(config)
    parties = config.parties
    guest = parties.guest[0]
    host = parties.host[0]

    guest_train_data = {"name": "ionosphere_scale_hetero_guest", "namespace": f"experiment{namespace}"}
    host_train_data = {"name": "ionosphere_scale_hetero_host", "namespace": f"experiment{namespace}"}

    pipeline = PipeLine().set_initiator(role='guest', party_id=guest).set_roles(guest=guest, host=host)

    reader_0 = Reader(name="reader_0")
    reader_0.get_party_instance(role='guest', party_id=guest).component_param(table=guest_train_data)
    reader_0.get_party_instance(role='host', party_id=host).component_param(table=host_train_data)
    data_transform_0 = DataTransform(name="data_transform_0")
    data_transform_0.get_party_instance(role='guest', party_id=guest).component_param(with_label=True,
                                                                                       label_name="LABEL",
                                                                                       missing_fill=False,
                                                                                       missing_fill_method="mean",
                                                                                       # below outlier deal with one or more feature ok
                                                                                       # designated ok
                                                                                       feature=["x1", "x5"],
                                                                                       outlier_replace=False,
                                                                                       # outlier_replace_method is asmissing outlier_replace_value=None
                                                                                       outlier_replace_method="designated",
                                                                                       outlier_impute=[1, 1],
                                                                                       outlier_replace_value=[10, 11])
    data_transform_0.get_party_instance(role='host', party_id=host).component_param(with_label=False,
                                                                                     missing_fill=False,
                                                                                     missing_fill_method="designated",
                                                                                     default_value=0,
                                                                                     outlier_replace=False)
    intersection_0 = Intersection(name="intersection_0")
    data_transform1_0 = DataTransform1(name="data_transform1_0")
    data_transform1_0.get_party_instance(role='guest', party_id=guest).component_param(with_label=True,
                                                                                      label_name="LABEL",
                                                                                      missing_fill=False,
                                                                                      missing_fill_method="mean",
                                                                                      # below outlier deal with one or more feature ok
                                                                                      # designated ok
                                                                                      feature=["x1","x5"],
                                                                                      outlier_replace=True,
                                                                                      # outlier_replace_method is asmissing outlier_replace_value=None
                                                                                      outlier_replace_method="designated",
                                                                                      outlier_impute=[1,1],
                                                                                      outlier_replace_value=[10,11])
    data_transform1_0.get_party_instance(role='host', party_id=host).component_param(with_label=False,
                                                                                    missing_fill=False,
                                                                                    missing_fill_method="designated",
                                                                                    default_value=0,
                                                                                    feature=["x20"],
                                                                                    outlier_replace=True,
                                                                                    outlier_replace_method="designated",
                                                                                    outlier_impute=[-1],
                                                                                    outlier_replace_value=[100])
    statistic_param = {
        "name": "statistic_0",
        "statistics": ["95%", "coefficient_of_variance", "stddev"],
        "column_indexes": -1,
        "column_names": []
    }
    statistic_0 = DataStatistics(**statistic_param)

    pipeline.add_component(reader_0)
    pipeline.add_component(data_transform_0,data=Data(data=reader_0.output.data))
    pipeline.add_component(intersection_0, data=Data(data=data_transform_0.output.data))
    pipeline.add_component(data_transform1_0,data=Data(data=intersection_0.output.data))
    pipeline.add_component(statistic_0, data=Data(data=data_transform1_0.output.data))

    pipeline.compile()

    pipeline.fit()
    print(pipeline.get_component("statistic_0").get_summary())


if __name__ == "__main__":
    parser = argparse.ArgumentParser("PIPELINE DEMO")
    parser.add_argument("-config", type=str,
                        help="config file")
    args = parser.parse_args()
    if args.config is not None:
        main(args.config)
    else:
        main()
