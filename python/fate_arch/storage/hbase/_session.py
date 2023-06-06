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
import traceback

import happybase
from impala.dbapi import connect

from fate_arch.common.address import HiveAddress, HBASEAddress
from fate_arch.storage import StorageSessionBase, StorageEngine, HiveStoreType
from fate_arch.abc import AddressABC
import func_timeout

class StorageSession(StorageSessionBase):
    def __init__(self, session_id, options=None):
        super(StorageSession, self).__init__(session_id=session_id, engine=StorageEngine.HIVE)
        self._db_con = {}

    def create_table(self, address, name, namespace, partitions=None, **kwargs):
        try:
            table = self.table(address=address, name=name, namespace=namespace, partitions=partitions, **kwargs)
            return table
        except:
            return None

    def verify_conn(self, address, name, namespace, partitions=None, **kwargs):
        try:
            table = self.table(address=address, name=name, namespace=namespace, partitions=partitions, **kwargs)
            return True,None,table
        except func_timeout.exceptions.FunctionTimedOut as e:
            return False, "ip地址或端口错误", None
        except:
            return False, '请求参数验证失败', None

    @func_timeout.func_set_timeout(5)
    def table(self, name, namespace, address: AddressABC, partitions,
              storage_type: HiveStoreType = HiveStoreType.DEFAULT, options=None, **kwargs):

        if isinstance(address, HBASEAddress):
            from fate_arch.storage.hbase._table import StorageTable
            address_key = HBASEAddress(
                host=address.host,
                port=address.port,
                name=address.name
               )
            if address_key in self._db_con:
                table= self._db_con[address_key]
            else:
                connection = happybase.Connection(host=address_key.host, port=address_key.port)
                table = connection.table("%s:%s"%(address.namespace,address.name))
                table.families()
                self._db_con[address_key] = table
            return StorageTable(table=table, address=address, name=name,namespace=namespace,partitions=partitions)
        raise NotImplementedError(f"address type {type(address)} not supported with eggroll storage")


    def stop(self):
        pass

    def kill(self):
        return self.stop()

