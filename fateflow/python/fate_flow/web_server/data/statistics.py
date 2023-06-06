import re
import sys, json, time
from fate_flow.operation.job_saver import JobSaver
from fate_arch import storage
from fate_flow.operation.job_tracker import Tracker
from fate_flow.manager.data_manager import delete_metric_data, TableStorage, get_component_output_data_schema
from fate_flow.component_env_utils.env_utils import import_component_output_depend
from fate_flow.component_env_utils import feature_utils
from fate_arch.session import Session
import pandas as pd
import numpy as np
from functools import wraps
import math

DEBUG = False

from fate_flow.web_server.utils.redis_util import Redis_db
try:
    redis_db = Redis_db()
except Exception as e:
    print("Can't connect redis...")
    redis_db = None

def redis_get(key):
    global redis_db
    if not redis_db:return
    try:
        r,e = redis_db.hget(key)
        if r:return json.loads(r["value"])
    except Exception as e:
        pass

def redis_set(key, obj):
    global redis_db
    if not redis_db:return
    try:
        redis_db.hset(key, "value", json.dumps(obj), 3600)
    except Exception as e:
        pass

def timeit(my_func):
    @wraps(my_func)
    def timed(*args, **kw):
        if not DEBUG: return my_func(*args, **kw)
        tstart = time.time()
        output = my_func(*args, **kw)
        tend = time.time()

        print('"{}" took {:.3f} ms to execute\n'.format(my_func.__name__, (tend - tstart) * 1000))
        return output
    return timed

def get_component_output_tables_meta(jid, cnm, pid=9999, role='guest'):
    tracker = Tracker(job_id=jid, component_name=cnm, role=role, party_id=pid)
    output_data_table_infos = tracker.get_output_data_info()
    output_tables_meta = tracker.get_output_data_table(output_data_infos=output_data_table_infos)
    return output_tables_meta

@timeit
def component_output_data(jid, cnm, pid=9999, role='guest', limit=-1):
    r = redis_get(f"{jid}-{cnm}-{pid}-{role}-{limit+1}")
    if r: return pd.DataFrame(r[0]),r[1]

    tasks = JobSaver.query_task(only_latest=True, job_id=jid, component_name=cnm, role=role, party_id=pid)
    if not tasks:
        request_data = {"job_id": jid, "role": role, "party_id": pid, "component_name": cnm}
        raise ValueError(f'no task found, please check if the parameters are correct:{request_data}')
    import_component_output_depend(tasks[0].f_provider_info)
    output_tables_meta = get_component_output_tables_meta(jid, cnm, pid, role)
    if limit>0 and limit < 300:
        res = get_data_by_metas(output_tables_meta, limit)
    else:
        res = get_data_by_metas_unlimited(output_tables_meta, limit)
    if res: redis_set(f"{jid}-{cnm}-{pid}-{role}-{limit+1}", (res[0].to_dict(orient="records"), res[1]))
    return res

def get_data_by_metas(output_tables_meta, limit = -1):
    for output_name, output_table_meta in output_tables_meta.items():
        rows = []
        is_str = False
        all_extend_header = {}
        if output_table_meta:
            for k, v in output_table_meta.get_part_of_data():
                data_line, is_str, all_extend_header = feature_utils.get_component_output_data_line(src_key=k, src_value=v, schema=output_table_meta.get_schema(), all_extend_header=all_extend_header)
                rows.append(data_line)
                if limit>0 and len(rows) >= limit:break
        if rows:
            extend_header = feature_utils.generate_header(all_extend_header, schema=output_table_meta.get_schema())
            if output_table_meta.schema.get("is_display", True):
                header = get_component_output_data_schema(output_table_meta=output_table_meta, is_str=is_str,
                                                          extend_header=extend_header)
            else:
                header = [f"ID{i}" for i in range(0, len(rows[0]))]
            return pd.DataFrame(rows, columns=header), output_table_meta.get_count()

    return pd.DataFrame(), 0

def get_data_by_metas_unlimited(output_tables_meta, limit = -1):
    for name, meta in output_tables_meta.items():
        return get_data_by_meta(meta, limit), meta.get_count()

    return pd.DataFrame(), 0

def get_data_by_meta(meta, limit = -1):
    output_data_count = 0
    rows = []
    header = None

    with Session() as sess:
        output_table = sess.get_table(name = meta.get_name(),
                                      namespace = meta.get_namespace())
        if not output_table: return

        all_extend_header = {}
        for k, v in output_table.collect():
            data_line, is_str, all_extend_header = feature_utils.get_component_output_data_line(src_key = k,
                                                                                            src_value = v,
                                                                                            schema = meta.get_schema(),
                                                                                            all_extend_header=all_extend_header)
            rows.append(data_line)

            if output_data_count == 0:
                extend_header = feature_utils.generate_header(all_extend_header,
                                                              schema=meta.get_schema())
                header = get_component_output_data_schema(output_table_meta = meta,
                                                          is_str = is_str,
                                                          extend_header = extend_header)

            output_data_count += 1
            if output_data_count == limit:break

    if not header and len(rows)>0:
        header = [f"ID{i}" for i in range(0, len(rows[0]))]
    if len(rows) > 0 and len(header) < len(rows[0]):
        diff = len(rows[0]) - len(header)
        for i in range(0, diff): header.append(f"Feature_{i}")

    return pd.DataFrame(rows, columns=header)


@timeit
def get_data_by_name(name, limit=1000, namespace="experiment"):
    meta = storage.StorageTableMeta(name = name, namespace = namespace)
    if not meta: return
    return get_data_by_metas({name: meta}, limit)#, meta.get_count()

def df2json(df):
    res = {}
    for c in df.columns:
        res[c] = list(df[c])
    return res

@timeit
def statistics(df):
    res = {}
    if len(df) <2:return res

    for cc, c in enumerate(df.columns):
        st = {}
        if len(df[c].dropna().values)<1: continue
        if re.search(r"(^[a-z]id|[^a-z]id)$", c, flags=re.IGNORECASE): continue
        try:
            if isinstance(df[c].dropna().values[0], dict):
                df[c] = df[c].map(lambda x: json.dumps(x, ensure_ascii=False))
                continue
        except Exception as e:
            pass

        vc = df.iloc[:,cc].astype(str).value_counts(normalize=True).to_dict()
        if len(vc.keys())*1./len(df) < 0.3 and len(vc.keys()) < 30 and not re.search(r"[0-9]\.[0-9]+,", re.sub(r"\.0,", ",", ",".join([str(v) for v in df[c].dropna().values[0:10]]))):
            st["pie"] = {re.sub(r"\.0.*", "", str(k)): v for k,v in vc.items()}
            if not isinstance(df[c].dropna().values[0], (int, np.int, np.int64)) and not isinstance(df[c].dropna().values[0], (float, np.float)):
                df[c] = df[c].astype(str)
                res[c] = st
                continue

        try:
            st["min"] = df.iloc[:,cc].astype(float).min()
        except Exception as e:
            pass
        try:
            st["max"] = df.iloc[:,cc].astype(float).max()
        except Exception as e:
            pass
        try:
            st["mean"] = df.iloc[:,cc].astype(float).mean()
        except Exception as e:
            pass
        try:
            st["median"] = df.iloc[:,cc].astype(float).median()
        except Exception as e:
            pass
        try:
            st["std"] = df.iloc[:,cc].astype(float).std()
        except Exception as e:
            pass
        try:
            st["sum"] = df.iloc[:,cc].astype(float).sum()
        except Exception as e:
            pass
        try:
            st["skew"] = df.iloc[:,cc].astype(float).skew()
            st['skew'] = 0 if math.isnan(st['skew']) else st['skew']
        except Exception as e:
            pass
        try:
            st["miss"] = df.iloc[:,cc].isnull().sum()*1./len(df)
        except Exception as e:
            pass
        try:
            st["kurtosis"] = df.iloc[:,cc].astype(float).kurtosis()
            if np.isnan(st["kurtosis"]): del st["kurtosis"]
        except Exception as e:
            pass
        try:
            hist = {}
            for t in pd.qcut(df.iloc[:,cc].astype(float), 8, duplicates='drop').tolist():
                l,r = t.left, t.right
                if (l,r) not in hist:hist[(l,r)] = 0
                hist[(l,r)] += 1
            st["hist"] = sorted(hist.items(), key=lambda x: x[0][0])
        except Exception as e:
            pass
        try:
            dp = df.iloc[:,cc].astype(float).dropna()
            st["quatile"] = dp.tolist()#dp.sample(n=min(200,len(dp)), random_state=0).tolist()
        except Exception as e:
            pass
        if len(st.keys()) == 1 and "miss" in st: pass
        else: res[c] = st
    return res

@timeit
def categorical_cols(df):
    res = []
    l = len(df)
    for c in df.columns:
        if str(df[c].dtype) == "object":
            res.append(c)
            continue
        u = df[c].dropna().nunique()
        if u>0 and u*1./l <0.1: res.append(c)
    return res

@timeit
def is_binary_multi_regress(df, y):
    l = len(df)
    u = df[y].dropna().nunique()
    if u == 2: return "binary"
    if u*1./l < 0.5: return "multi"
    return "regress"

@timeit
def column_view(df):
    res = {}
    MxL = 11
    for c in df.columns:
        row = [str(a)[:MxL] + ("..." if len(str(a))>MxL else "") for a in df[c][:11]]

        res[c] = "|".join(row)

    return pd.DataFrame(res.items(), columns=["特征名称","特征样例"]).to_dict(orient="records")


if __name__ == "__main__":
    #print(get_data_by_name("breast_hetero_guest", "experiment"))

    JID, CNM = sys.argv[1:3]

    df = component_output_data(JID, CNM)
    print(df)
    print(categorical_cols(df["data"]["df"]))

