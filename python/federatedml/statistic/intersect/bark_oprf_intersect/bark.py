import os, time, hashlib

import random

import subprocess

from fate_flow.entity import Metric, MetricMeta
from federatedml.statistic.intersect import Intersect
from federatedml.util import consts, LOGGER
import pandas as pd
from pathlib import Path
from fate_arch.common.conf_utils import get_base_config
from fate_flow.utils.base_utils import get_fate_flow_directory
from federatedml.transfer_variable.base_transfer_variable import BaseTransferVariables

"""
{'dsl_version': 2, 'initiator': {'role': 'guest', 'party_id': 9999}, 'role': {'guest': [9999], 'host': [10000]},
 'job_parameters': {
     'common': {'job_type': 'train', 'inheritance_info': {}, 'computing_engine': 'SeceumGlue', 'engines_address': {},
                'federated_mode': 'MULTIPLE', 'task_parallelism': 1, 'computing_partitions': 4,
                'federated_status_collect_type': 'PUSH', 'model_id': 'arbiter-10000#guest-9999#host-10000#model',
                'model_version': '202304261849176925220', 'auto_retries': 0, 'auto_retry_delay': 1,
                'SeceumGlue_run': {}, 'spark_run': {}, 'rabbitmq_run': {}, 'pulsar_run': {},
                'adaptation_parameters': {'task_nodes': 1, 'task_cores_per_node': 4, 'task_memory_per_node': 0,
                                          'request_task_cores': 4, 'if_initiator_baseline': True}}},
 'local': {'role': 'guest', 'party_id': 9999}, 'module': 'Intersection', 'CodePath': 'IntersectGuest',
 'ComponentParam': {'intersect_method': 'rsa', 'sync_intersect_ids': True, 'raw_params': {},
                    'rsa_params': {'salt': 'Seceum', 'hash_method': 'sha256', 'final_hash_method': 'sha256',
                                   'key_length': 1024, 'random_bit': 128, 'random_base_fraction': 0,
                                   'split_calculation': False}, 'bark_oprf_params': {}, 'only_output_key': False,
                    'sample_id_generator': 'guest', 'run_cache': False, 'join_method': 'inner_join',
                    'new_sample_id': False, 'dh_params': {}, 'cardinality_only': False, 'sync_cardinality': False,
                    'cardinality_method': 'rsa', 'run_preprocess': False, 'intersect_preprocess_params': {},
                    'ecdh_params': {}}, 'ComponentParameterSource': 'outs'}
"""

# noinspection PyAttributeOutsideInit
class BaRKTransferVariable(BaseTransferVariables):
    def __init__(self, flowid=0):
        super().__init__(flowid)
        # 公共的id
        self.intersect_ids = self._create_variable(name='intersect_ids', src=['guest'], dst=['host'])
        self.port = self._create_variable(name='port', src=['guest'], dst=['host'])
        self.md5id = self._create_variable(name='md5id', src=['host'], dst=['guest'])


class BaRK(Intersect):
    def __init__(self, jid, hosts=[]):
        self.role = None
        self.jid = jid
        self.hosts = hosts
        self._summary = {}
        self.conf = get_base_config("bark_oprf")
        LOGGER.info("guest bark oprf config {}".format(self.conf))
        self.exe = '/opt/BaRK-OPRF/Release/bOPRFmain.exe'
        self.transfer_variable = BaRKTransferVariable(jid)

        def run_intersect(self, data_instances):
            raise NotImplementedError("method should not be called here")

        def run_cardinality(self, data_instances):
            raise NotImplementedError("method should not be called here")

        def generate_cache(self, data_instances):
            raise NotImplementedError("method should not be called here")

        def run_cache_intersect(self, data_instances, cache_data):
            raise NotImplementedError("method should not be called here")

    @staticmethod
    def md5(k):
        h = hashlib.md5()
        h.update(str(k).encode('utf-8'))
        return h.hexdigest()

    def summary(self):return self._summary

    def callback(self, tracker):
        tracker.log_metric_data(
            metric_name="intersection",
            metric_namespace="train",
            metrics=[Metric("intersect_count", self.match_id_intersect_num),
                     Metric("input_match_id_count", self.match_id_num),
                     Metric("intersect_rate", self.intersect_rate),
                     Metric("unmatched_count", self.unmatched_num),
                     Metric("unmatched_rate", self.unmatched_rate)]
        )
        tracker.set_metric_meta(metric_namespace="train",
                                metric_name="intersection",
                                metric_meta=MetricMeta(name="intersection",
                                                       metric_type="INTERSECTION",
                                                       extra_metas={"intersect_method": "bark-oprf",
                                                                    "join_method": "left"}
                                                       )
                                )


class BaRKGuest(BaRK):
    def __init__(self, jid, hosts):
        super().__init__(jid, hosts)
        self.role = consts.GUEST

    def run_intersect(self, data_instances):
        start = time.time()
        ostart = start

        random.seed(time.time())
        port = int(self.conf["port"])# + random.randint(0,1000)
        self.transfer_variable.port.remote(port, role=consts.HOST, idx=-1)
        # 交集结果存储
        guest_data_path = Path(get_fate_flow_directory('bark'), self.jid, "guest")
        assert not os.path.exists(guest_data_path), f"Duplicated file exist.{guest_data_path}"
        os.makedirs(guest_data_path)
        guest_data_path = guest_data_path / "id.parquet"

        id_md5_pair = list(data_instances.map(lambda k, v: (k, BaRK.md5(k))).collect())
        LOGGER.info(">>>> id_md5_pair: {}".format(time.time() - start))
        start = time.time()

        hosts_dir = [Path(get_fate_flow_directory('bark'), self.jid, "hosts", str(h)) for h in self.hosts]
        for dir in hosts_dir:
            if not os.path.isdir(dir): os.makedirs(dir)

        gst_md5s = set([md5 for _, md5 in id_md5_pair])
        unique_id_num = len(gst_md5s)
        for ii, h in enumerate(self.hosts):
            pd.DataFrame(list(gst_md5s), columns=['md5']) \
                .to_parquet(guest_data_path, index=False, engine='fastparquet')
            command = ' '.join(
                [self.exe, "-r 0", str(guest_data_path), "-ip", "0.0.0.0:{}".format(port), " 2>&1 >",
                 str(guest_data_path) + ".console"])
            LOGGER.info("command: {}".format(command))
            LOGGER.debug("os.getenv: {}".format(os.getenv("PATH")))
            shell_console = subprocess.Popen(command, shell=True)
            LOGGER.info(">>>> {}: {}".format(shell_console.wait(), time.time()-start))

            gst_md5s = set(self.transfer_variable.md5id.get(idx=ii)) & gst_md5s

            if not gst_md5s: break

        intersect_ids = [id for id, md5 in id_md5_pair if md5 in gst_md5s]
        assert len(intersect_ids) == len(gst_md5s), "intersected data is not in original data: {} vs {}".format(len(intersect_ids), len(gst_md5s))
        LOGGER.info(">>>> bark over: {},{}".format(time.time() - start, len(intersect_ids)))
        start = time.time()

        if self.sync_intersect_ids:
            self.transfer_variable.intersect_ids.remote(intersect_ids, role=consts.HOST, idx=-1)

        self.match_id_intersect_num = len(intersect_ids)
        self.match_id_num = data_instances.count()
        self.intersect_rate = self.match_id_intersect_num*1./self.match_id_num
        self.unmatched_num = self.match_id_num - self.match_id_intersect_num
        self.unmatched_rate = self.unmatched_num*1./self.match_id_num

        intersect_ids = set(intersect_ids)
        intersect_ids = data_instances.filter(lambda k,v: k in intersect_ids)
        intersect_ids.schema = data_instances.schema

        self._summary = {"intersect_num": self.match_id_intersect_num,
                         "intersect_rate": self.intersect_rate,
                         "cardinality_only": self.cardinality_only,
                         "unique_id_num": unique_id_num
                         }
        LOGGER.info(">>>> Join value: {}, Overall: {}, {}".format(time.time() - start, time.time() - ostart, intersect_ids.count()))
        return intersect_ids


class BaRKHost(BaRK):
    def __init__(self, jid):
        super().__init__(jid)
        self.role = consts.HOST
        self.data_path = Path(get_fate_flow_directory('bark'), jid)
        if not os.path.isdir(self.data_path): os.makedirs(self.data_path)

    def run_intersect(self, data_instances):
        start = time.time()
        ostart = start

        port = self.transfer_variable.port.get(idx=0)
        host_data_path = Path(get_fate_flow_directory('bark'), self.jid, "host")
        assert not os.path.exists(host_data_path), f"Duplicated file exist.{host_data_path}"
        os.makedirs(host_data_path)

        id_md5_pair = data_instances.map(lambda k, v: (k, BaRK.md5(k))).collect()
        gst_md5s = set([md5 for _, md5 in id_md5_pair])
        unique_id_num = len(gst_md5s)
        LOGGER.info(">>>> id_md5_pair: {}".format(time.time() - start))
        start = time.time()

        pd.DataFrame(list(gst_md5s), columns=['md5']) \
            .to_parquet(host_data_path / "id.parquet", index=False, engine='fastparquet')
        command = ' '.join([self.exe, "-r 1", str(host_data_path / "id.parquet"), "-ip",
                            "{}:{}".format(self.conf["psi_pair_ip"], port), " 2>&1 >",
                            str(host_data_path / "console.log")])
        LOGGER.info("command: {}".format(command))
        LOGGER.debug("os.getenv: {}".format(os.getenv("PATH")))
        shell_console = subprocess.Popen(command, shell=True)
        LOGGER.info(">>>> {}: {}".format(shell_console.wait(), time.time()-start))

        md5_ids = []
        with open(host_data_path / "id.txt", "r") as f:
            while True:
                line = f.readline()
                if not line: break
                md5_ids.append(line.strip("\n"))
        self.transfer_variable.md5id.remote(md5_ids, role=consts.GUEST, idx=0)
        md5_ids = set(md5_ids)

        LOGGER.info(">>>> bark over: {}, {}".format(time.time() - start, len(md5_ids)))
        start = time.time()

        if self.sync_intersect_ids:
            intersect_ids = self.transfer_variable.intersect_ids.get(idx=0)
        else:
            intersect_ids = [id for id,md5 in id_md5_pair if md5 in md5_ids]
            assert len(intersect_ids) == len(md5_ids), "intersected data is not in original data: {} vs {}".format(len(intersect_ids), len(md5_ids))

        self.match_id_intersect_num = len(intersect_ids)
        self.match_id_num = data_instances.count()
        self.intersect_rate = self.match_id_intersect_num*1./self.match_id_num
        self.unmatched_num = self.match_id_num - self.match_id_intersect_num
        self.unmatched_rate = self.unmatched_num*1./self.match_id_num

        intersect_ids = set(intersect_ids)
        intersect_ids = data_instances.filter(lambda k,v: k in intersect_ids)
        intersect_ids.schema = data_instances.schema

        self._summary = {"intersect_num": self.match_id_intersect_num,
                         "intersect_rate": self.intersect_rate,
                         "cardinality_only": self.cardinality_only,
                         "unique_id_num": unique_id_num
                         }
        LOGGER.info(">>>> Join value: {}, Overall: {}, count: {}".format(time.time() - start, time.time() - ostart, intersect_ids.count()))
        return intersect_ids
