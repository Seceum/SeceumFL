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
import os
import uuid

from fate_arch.common import hive_utils
from fate_arch.common.file_utils import get_project_base_directory
from fate_arch.storage import StorageEngine, HiveStoreType
from fate_arch.storage import StorageTableBase
import pandas as pd

class StorageTable(StorageTableBase):
    def __init__(
        self,
        table=None,
        address=None,
        name: str = None,
        namespace: str = None,
        partitions: int = 1,
        options=None,
    ):
        super(StorageTable, self).__init__(
            name=name,
            namespace=namespace,
            address=address,
            partitions=partitions,
            options=options,
            engine=StorageEngine.HBASE,
            store_type=None,
        )
        self.table = table



    def get_schema(self):
        for key, data in self.table.scan():
            header = ",".join([bytes.decode(i).split(":")[1] for i in data.keys()])
            sid = bytes.decode(key)
            return {'header': header, 'sid': "id"}


    def _collect(self, **kwargs) -> list:
        for key, data in self.table.scan():
            v = ",".join([bytes.decode(i) for i in data.values()])
            k = bytes.decode(key)
            yield k,v

    def check_address_by_schema(self):
        for key, data in self.table.scan():
            if data:
                return True
        return False

    def read_fl_table(self,sql=None,part_of_data=True):
        s= 0
        values =[]
        columns =[]
        for key, data in self.table.scan():
            if columns==[]:
                columns = ["id"]
                columns.extend([bytes.decode(i).split(":")[1] for i in data.keys()])
            value= [bytes.decode(key)]
            value.extend([bytes.decode(i) for i in data.values()])
            values.append(value)
            # columns = ["id"].extend([bytes.decode(i).split(":")[1] for i in data.keys()])
            # values = [bytes.decode(key)].extend([bytes.decode(i) for i in data.values()])
            if part_of_data:
                if s==5:
                    break
        df = pd.DataFrame(values,columns= columns)
        if df.empty:
            return False, "查询为空", None, None
        schema = self.get_schema()
        return True, None, df, schema

    def _count(self, **kwargs):
        s=0
        for key, data in self.table.scan():
            s+=1
        return s

    def _read(self):
        pass

    def _destroy(self):
        pass

    def _save_as(self, address, name, namespace, partitions=None, schema=None, **kwargs):
        pass