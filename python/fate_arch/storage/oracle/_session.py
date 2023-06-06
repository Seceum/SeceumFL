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
import cx_Oracle as cx
# import pymysql
import func_timeout
from fate_arch.storage import StorageSessionBase, StorageEngine, StorageTableMeta
from fate_arch.abc import AddressABC
from fate_arch.common.address import MysqlAddress, OracleAddress


class StorageSession(StorageSessionBase):
    def __init__(self, session_id, options=None):
        super(StorageSession, self).__init__(session_id=session_id, engine=StorageEngine.ORACLE)
        self._db_con = {}

    def create_table(self, address, name, namespace, partitions=None, **kwargs):
        try:
            table = self.table(address=address, name=name, namespace=namespace, partitions=partitions, **kwargs)
            table.create_meta(**kwargs)
            return table
        except cx.DatabaseError:
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
               options=None, **kwargs):

        if isinstance(address, OracleAddress):
            from fate_arch.storage.oracle._table import StorageTable
            address_key = OracleAddress(user=address.user,
                                       passwd=address.passwd,
                                       host=address.host,
                                       port=address.port,
                                        dsn= address.dsn,
                                       # db=address.db,
                                       name=address.name)

            if address_key in self._db_con:
                con, cur = self._db_con[address_key]
            else:
                # self._create_db_if_not_exists(address)

                con = cx.connect(
                    user=address.user,
                    password=address.passwd,
                    dsn="%s:%s/%s"%(address.host,address.port,address.dsn)
                )
                cur = con.cursor()
                self._db_con[address_key] = (con, cur)

            return StorageTable(cur=cur, con=con, address=address, name=name, namespace=namespace,
                                 partitions=partitions, options=options)

        raise NotImplementedError(f"address type {type(address)} not supported with eggroll storage")

    def cleanup(self, name, namespace):
        pass

    def stop(self):
        try:
            for key, val in self._db_con.items():
                con = val[0]
                cur = val[1]
                cur.close()
                con.close()
        except Exception as e:
            traceback.print_exc()

    def kill(self):
        return self.stop()

