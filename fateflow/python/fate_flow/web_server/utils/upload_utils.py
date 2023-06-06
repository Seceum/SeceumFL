import os
import shutil
from fate_arch.session import Session
from fate_arch.storage import DEFAULT_ID_DELIMITER, StorageTableOrigin
from fate_flow.components.upload import Upload, LOGGER
from fate_arch import storage
from fate_flow.scheduling_apps.client import TrackerClient
from fate_flow.settings import IS_STANDALONE


class Diy_upload(Upload):
    def diy_run(self,job_id,parameters):
        self.parameters =parameters
        self.parameters["role"] = {'local': [0]}
        self.parameters["local"] = {'role': 'local', 'party_id': 0}
        self.parameters["extend_sid"] = False
        self.parameters["partition"] = self.parameters["partitions"]
        if IS_STANDALONE:
            storage_engine = 'STANDALONE'
        else:
            storage_engine = 'STANDALONE'
        sess = Session()
        address_dict = {'cores_per_node': 20, 'nodes': 1, 'name': self.parameters["name"], 'namespace': self.parameters["namespace"],
                        'storage_type': 'LMDB'}
        storage_session = sess.storage(
            storage_engine=storage_engine
        )
        if not self.parameters.get("id_delimiter"):self.parameters["id_delimiter"] =DEFAULT_ID_DELIMITER
        self.parameters["extend_sid"] =False
        self.parameters["auto_increasing_sid"] = False
        address = storage.StorageTableMeta.create_address(
            storage_engine=storage_engine, address_dict=address_dict
        )
        self.tracker = TrackerClient(**{"job_id":job_id,"role":"local","party_id":0})
        self.table  = storage_session.create_table(address=address,origin=StorageTableOrigin.UPLOAD, **self.parameters)

        #data_table_count = self.save_data_table(job_id, self.parameters["name"], self.parameters["namespace"], storage_engine, self.parameters["head"])
        data_table_count = self.save_data_table(job_id, self.parameters["name"], self.parameters["namespace"], self.parameters["head"])
        self.table.meta.update_metas(in_serialized=True)
        try:
            if "{}/fate_upload_tmp".format(job_id) in self.parameters["file"]:
                shutil.rmtree(os.path.dirname(self.parameters["file"]))
        except:
            LOGGER.error("diy Myupload remove tmp file failed")

    """
    def save_data_table(self, job_id, dst_table_name, dst_table_namespace, storage_engine, head=True):
        input_file = self.parameters["file"]
        input_feature_count = self.get_count(input_file)
        data_head, file_list, table_list = self.split_file(input_file, head, input_feature_count, dst_table_name,
                                                           dst_table_namespace, storage_engine)
        if len(file_list) == 1:
            self.upload_file(input_file, head, job_id, input_feature_count,without_block=False)
        else:
            self.upload_file_block(file_list, data_head, table_list)
        table_count = self.table.count()
        self.table.meta.update_metas(
            count=table_count,
            partitions=self.parameters["partition"],
            extend_sid=self.parameters["extend_sid"],
        )
        self.save_meta(
            dst_table_namespace=dst_table_namespace,
            dst_table_name=dst_table_name,
            table_count=table_count,
        )
        return table_count
    """

    def save_data_table(self, job_id, dst_table_name, dst_table_namespace, head=True):
        input_file = self.parameters["file"]
        input_feature_count = self.get_count(input_file)
        if head is True:
            input_feature_count -= 1
        self.upload_file(input_file, head, job_id, input_feature_count)
        # table_count = self.table.count()
        metas_info = {
            "count": input_feature_count,
            "partitions": self.parameters["partition"],
            "extend_sid": self.parameters["extend_sid"]
        }
        if self.parameters.get("with_meta"):
            metas_info.update({"schema": self.generate_anonymous_schema()})
        self.table.meta.update_metas(**metas_info)
        self.save_meta(
            dst_table_namespace=dst_table_namespace,
            dst_table_name=dst_table_name,
            table_count=input_feature_count,
        )
        return input_feature_count
