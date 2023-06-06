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
from sqlalchemy import create_engine

from fate_arch.storage import StorageEngine, MySQLStoreType
from fate_arch.storage import StorageTableBase
import pandas as pd

class StorageTable(StorageTableBase):
    def __init__(
        self,
        cur,
        con,
        address=None,
        name: str = None,
        namespace: str = None,
        partitions: int = 1,
        store_type: MySQLStoreType = MySQLStoreType.InnoDB,
        options=None,
    ):
        super(StorageTable, self).__init__(
            name=name,
            namespace=namespace,
            address=address,
            partitions=partitions,
            options=options,
            engine=StorageEngine.MYSQL,
            store_type=store_type,
        )
        self._cur = cur
        self._con = con

    def check_address(self):
        schema = self.meta.get_schema()
        if schema:
            if schema.get("sid") and schema.get("header"):
                sql = "SELECT {},{} FROM {}".format(
                    schema.get("sid"), schema.get("header"), self._address.name
                )
            else:
                sql = "SELECT {} FROM {}".format(
                    schema.get("sid"), self._address.name
                )
            feature_data = self.execute(sql)
            for feature in feature_data:
                if feature:
                    break
        return True

    @staticmethod
    def get_meta_header(feature_name_list):
        create_features = ""
        feature_list = []
        feature_size = "varchar(255)"
        for feature_name in feature_name_list:
            create_features += "{} {},".format(feature_name, feature_size)
            feature_list.append(feature_name)
        return create_features, feature_list

    def _count(self):
        sql = "select count(*) from {}".format(self._address.name)
        try:
            self._cur.execute(sql)
            # self.con.commit()
            ret = self._cur.fetchall()
            count = ret[0][0]
        except BaseException:
            count = 0
        return count

    def _collect(self, **kwargs) -> list:
        id_name, feature_name_list, _ = self._get_id_feature_name()
        id_feature_name = [id_name]
        id_feature_name.extend(feature_name_list)
        sql = "select {} from {}".format(",".join(id_feature_name), self._address.name)
        data = self.execute(sql)
        for line in data:
            feature_list = [str(feature) for feature in list(line[1:])]
            yield line[0], self.meta.get_id_delimiter().join(feature_list)

    def _put_all(self, kv_list, **kwargs):
        id_name, feature_name_list, id_delimiter = self._get_id_feature_name()
        feature_sql, feature_list = StorageTable.get_meta_header(feature_name_list)
        id_size = "varchar(100)"
        create_table = (
            "create table if not exists {}({} {} NOT NULL, {} PRIMARY KEY({}))".format(
                self._address.name, id_name, id_size, feature_sql, id_name
            )
        )
        self._cur.execute(create_table)
        sql = "REPLACE INTO {}({}, {})  VALUES".format(
            self._address.name, id_name, ",".join(feature_list)
        )
        for kv in kv_list:
            sql += '("{}", "{}"),'.format(kv[0], '", "'.join(kv[1].split(id_delimiter)))
        sql = ",".join(sql.split(",")[:-1]) + ";"
        self._cur.execute(sql)
        self._con.commit()

    def _destroy(self):
        sql = "drop table {}".format(self._address.name)
        self._cur.execute(sql)
        self._con.commit()

    def _save_as(self, address, name, namespace, partitions=None, **kwargs):
        sql = "create table {}.{} select * from {};".format(namespace, name, self._address.name)
        self._cur.execute(sql)
        self._con.commit()

    def execute(self, sql, select=True):
        self._cur.execute(sql)
        if select:
            while True:
                result = self._cur.fetchone()
                if result:
                    yield result
                else:
                    break
        else:
            result = self._cur.fetchall()
            return result

    def _get_id_feature_name(self):
        id = self.meta.get_schema().get("sid", "id")
        header = self.meta.get_schema().get("header", [])
        id_delimiter = self.meta.get_id_delimiter()
        if not header:
            feature_list = []
        elif isinstance(header, str):
            feature_list = header.split(id_delimiter)
        elif isinstance(header, list):
            feature_list = header
        else:
            feature_list = [header]
        if self.meta.get_extend_sid():
            id = feature_list[0]
            if len(feature_list) > 1:
                feature_list = feature_list[1:]
        return id, feature_list, id_delimiter



    def read_fl_table(self,sql=None,part_of_data=True):
        if sql:
            try:
                df = pd.read_sql(sql, self._con)
            except:
                return False, "执行sql错误", None, None
            if df.empty:
                return False, "查询为空",None,None
            if len(list(set(df.columns[1:]))) != len(df.columns[1:]):
                return False, "重复列",None,None
            header = ",".join(df.columns[1:].tolist())
            sid = df.columns[0]
            schema = {'header': header, 'sid': sid, "sql": sql}
            if part_of_data:
                df=df[:5]
            return True,None,df,schema
        else:
            feature_column, id_column = self.get_mysql_column_sid()
            if feature_column and id_column:
                schema = {'header': feature_column, 'sid': id_column}
            else:
                return False,"表缺少主键或特征列或表不存在",None,None
            sql = "SELECT {},{} FROM {}".format(
                schema.get("sid"), schema.get("header"), self._address.name
            )
            try:
                df = pd.read_sql(sql, self._con)
            except:
                return False, "执行sql错误", None, None
            if df.empty:
                return False, "查询为空",None,None
            if part_of_data:
                df = df[:5]
            return True,None,df,schema

    def get_mysql_column_sid(self, id_delimiter=","):
        engine_url = "mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8".format(
            user=self.address.user,
            password=self.address.passwd,
            host=self.address.host, port=self.address.port,
            db_name=self.address.db)
        e = create_engine(engine_url)
        future_column_sql = "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}'".format(
            self.address.db, self.address.name)
        sid_sql = "SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}'".format(
            self.address.db, self.address.name)
        future_column_df = pd.read_sql(future_column_sql, e)
        sid_df = pd.read_sql(sid_sql, e)
        all_columns = future_column_df["COLUMN_NAME"].astype(str).tolist()
        sid = sid_df["COLUMN_NAME"].astype(str).tolist()
        future_columns = id_delimiter.join(set(all_columns).difference(set(sid)))
        id_column = id_delimiter.join(sid)
        return future_columns, id_column

