from copy import deepcopy
from datetime import datetime

import peewee

from fate_flow.db.db_models import DB
from fate_flow.web_server.utils.common_util import get_uuid, datetime_format


class CommonService:
    model = None

    @classmethod
    @DB.connection_context()
    def query(cls, cols=None, reverse=None, order_by=None, **kwargs):
        return cls.model.query(cols=cols, reverse=reverse, order_by=order_by, **kwargs)

    @classmethod
    @DB.connection_context()
    def get_all(cls, cols=None, reverse=None, order_by=None):
        if cols:
            query_records = cls.model.select(*cols)
        else:
            query_records = cls.model.select()
        if reverse is not None:
            if not order_by or not hasattr(cls, order_by):
                order_by = "create_time"
            if reverse is True:
                query_records = query_records.order_by(cls.model.getter_by(order_by).desc())
            elif reverse is False:
                query_records = query_records.order_by(cls.model.getter_by(order_by).asc())
        return query_records

    @classmethod
    @DB.connection_context()
    def get(cls, **kwargs):
        return cls.model.get(**kwargs)

    @classmethod
    @DB.connection_context()
    def get_or_none(cls, **kwargs):
        try:
            return cls.model.get(**kwargs)
        except peewee.DoesNotExist:
            return None

    @classmethod
    @DB.connection_context()
    def save(cls, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = get_uuid()
        sample_obj = cls.model(**kwargs).save(force_insert=True)
        return sample_obj

    @classmethod
    @DB.connection_context()
    def insert_many(cls, data_list, batch_size=100):
        with DB.atomic():
            for i in range(0, len(data_list), batch_size):
                cls.model.insert_many(data_list[i:i + batch_size]).execute()

    @classmethod
    @DB.connection_context()
    def update_many_by_id(cls, data_list):
        cur = datetime_format(datetime.now())
        with DB.atomic():
            for data in data_list:
                data["update_time"] = cur
                cls.model.update(data).where(cls.model.id == data["id"]).execute()

    @classmethod
    @DB.connection_context()
    def update_by_id(cls, pid, data):
        data["update_time"] = datetime_format(datetime.now())
        num = cls.model.update(data).where(cls.model.id == pid).execute()
        return num

    @classmethod
    @DB.connection_context()
    def get_by_id(cls, pid):
        try:
            obj = cls.model.query(id=pid).get()
            return True, obj
        except peewee.DoesNotExist:
            return False, None

    @classmethod
    @DB.connection_context()
    def get_by_ids(cls, pids, cols=None):
        if cols:
            objs = cls.model.select(*cols)
        else:
            objs = cls.model.select()
        return objs.where(cls.model.id.in_(pids))

    @classmethod
    @DB.connection_context()
    def delete_by_id(cls, pid):
        cls.model.delete().where(cls.model.id == pid).execute()


    @classmethod
    @DB.connection_context()
    def filter_delete(cls, filters):
        with DB.atomic():
            num = cls.model.delete().where(*filters).execute()
            return num

    @classmethod
    @DB.connection_context()
    def filter_update(cls, filters, update_data):
        with DB.atomic():
            cls.model.update(update_data).where(*filters).execute()

    @staticmethod
    def cut_list(tar_list, n):
        length = len(tar_list)
        arr = range(length)
        result = [tuple(tar_list[x:(x + n)]) for x in arr[::n]]
        return result

    @classmethod
    @DB.connection_context()
    def filter_scope_list(cls, in_key, in_filters_list, filters=None, cols=None):
        in_filters_tuple_list = cls.cut_list(in_filters_list, 20)
        if not filters:
            filters = []
        res_list = []
        if cols:
            for i in in_filters_tuple_list:
                query_records = cls.model.select(*cols).where(getattr(cls.model, in_key).in_(i), *filters)
                if query_records:
                    res_list.extend([query_record for query_record in query_records])
        else:
            for i in in_filters_tuple_list:
                query_records = cls.model.select().where(getattr(cls.model, in_key).in_(i), *filters)
                if query_records:
                    res_list.extend([query_record for query_record in query_records])
        return res_list
