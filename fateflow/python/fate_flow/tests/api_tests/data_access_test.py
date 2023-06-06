import os
import time
import unittest

import requests

from fate_flow.entity.run_status import JobStatus
from fate_flow.utils.base_utils import get_fate_flow_directory
from fate_flow.settings import API_VERSION, HOST, HTTP_PORT


class TestDataAccess(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(get_fate_flow_directory(), "examples", "data")
        self.upload_guest_config = {"file": os.path.join(self.data_dir, "breast_hetero_guest.csv"), "head": 1,
                                    "partition": 10, "namespace": "experiment",
                                    "table_name": "breast_hetero_guest", "use_local_data": 0, 'drop': 1, 'backend': 0, "id_delimiter": ',', }
        self.upload_host_config = {"file": os.path.join(self.data_dir, "breast_hetero_host.csv"), "head": 1,
                                   "partition": 10, "namespace": "experiment",
                                   "table_name": "breast_hetero_host", "use_local_data": 0, 'drop': 1, 'backend': 0, "id_delimiter": ',', }
        self.download_config = {"output_path": os.path.join(get_fate_flow_directory(),
                                                            "fate_flow/fate_flow_unittest_breast_b.csv"),
                                "namespace": "experiment",
                                "table_name": "breast_hetero_guest"}
        self.server_url = "http://{}:{}/{}".format(HOST, HTTP_PORT, API_VERSION)

    def test_upload_guest(self):
        response = requests.post("/".join([self.server_url, 'data', 'upload']), json=self.upload_guest_config)
        self.assertTrue(response.status_code in [200, 201])
        self.assertTrue(int(response.json()['retcode']) == 0)
        job_id = response.json()['jobId']
        for i in range(60):
            response = requests.post("/".join([self.server_url, 'job', 'query']), json={'job_id': job_id})
            self.assertTrue(int(response.json()['retcode']) == 0)
            if response.json()['data'][0]['f_status'] == JobStatus.SUCCESS:
                break
            time.sleep(1)

    def test_upload_host(self):
        response = requests.post("/".join([self.server_url, 'data', 'upload']), json=self.upload_host_config)
        self.assertTrue(response.status_code in [200, 201])
        self.assertTrue(int(response.json()['retcode']) == 0)
        job_id = response.json()['jobId']
        for i in range(60):
            response = requests.post("/".join([self.server_url, 'job', 'query']), json={'job_id': job_id})
            self.assertTrue(int(response.json()['retcode']) == 0)
            if response.json()['data'][0]['f_status'] == JobStatus.SUCCESS:
                break
            time.sleep(1)

    def test_upload_history(self):
        response = requests.post("/".join([self.server_url, 'data', 'upload/history']), json={'limit': 2})
        self.assertTrue(response.status_code in [200, 201])
        self.assertTrue(int(response.json()['retcode']) == 0)

    def test_download(self):
        response = requests.post("/".join([self.server_url, 'data', 'download']), json=self.download_config)
        self.assertTrue(response.status_code in [200, 201])
        self.assertTrue(int(response.json()['retcode']) == 0)


if __name__ == '__main__':
    unittest.main()
