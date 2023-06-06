import re
from flask import request
from flask_login import login_required, current_user
from fate_arch.session import Session
from fate_flow.settings import ENGINES, stat_logger
from fate_flow.utils.detect_utils import validate_request
from fate_flow.utils.job_utils import generate_job_id
from fate_flow.web_server.db_service.sample_service import SampleFieldsService, SampleService, VSampleInfoService
from fate_flow.utils.api_utils import get_json_result, server_error_response, get_data_error_result, federated_api
from fate_flow.web_server.utils.sample_util import get_fusion_fields, get_field_info_df
from fate_flow.web_server.fl_config import config
from fate_flow.web_server.pipeline_wrapper import pickname, WrapperFactory
from fate_flow.web_server.db_service.job_service import JobContentService
from fate_flow.web_server.utils.license_util import check_license
from fate_flow.web_server.db_service.project_service import ProjectCanvasService
from fate_flow.web_server.data import get_data_by_name, statistics
from fate_flow.web_server.pipeline_wrapper import data_transform


@manager.route("/nameit", methods=['POST'])
@login_required
def nameit():
    return get_json_result(data={"name": pickname()})


@manager.route("/fields", methods=['POST'])
@login_required
@validate_request("sample_id")
def sample_fields_list():
    """（自有数据、外部数据）_特征展示列表"""
    sample_id = request.json["sample_id"]
    sample_fields_objs = SampleFieldsService.query(sample_id=sample_id)
    all_field_type = []
    for sample in sample_fields_objs:
        all_field_type.append(sample.field_type)
    sample_list = list(sample_fields_objs.dicts())
    data = {
        "all_field_type": ["int", "float", "str", "bool"],
        "all_data_type": ["Y", "ID", "特征"],
        "all_distribution_type": ["连续型", "离散型"],
        "data": sample_list
    }
    return get_json_result(data=data)


@manager.route("/detail", methods=['POST'])
@login_required
@validate_request("sample_id", "type")
def sample_detail():
    """样本信息"""
    sample_id = request.json["sample_id"]
    data_type = request.json["type"]  # fusion/origin
    data = {
        "base_info": {},
        "feature_info": {},
        "fusion_info": {}
    }
    feature_cols = [SampleFieldsService.model.id, SampleFieldsService.model.sample_id,
                    SampleFieldsService.model.field_name, SampleFieldsService.model.field_examples,
                    SampleFieldsService.model.field_type, SampleFieldsService.model.distribution_type,
                    SampleFieldsService.model.data_type, SampleFieldsService.model.field_description]
    if data_type == "origin":
        # 样本信息(所属节点、样本集类别、特征数量、样本记录数、描述)
        # 元数据信息
        sample_cols = [SampleService.model.id.alias("sample_id"),
                       SampleService.model.name.alias("sample_name"),
                       SampleService.model.party_name, SampleService.model.sample_type,
                       SampleService.model.sample_count, SampleService.model.party_id,
                       SampleService.model.comments]
        sample_objs = SampleService.query(id=sample_id, cols=sample_cols).dicts()
        if not sample_objs:
            return get_json_result(data=False, retmsg="样本不存在", retcode=100)
        data["base_info"] = sample_objs[0]
        feature_info = list(SampleFieldsService.query(sample_id=sample_id, cols=feature_cols).dicts())
        data["feature_info"]["data"] = feature_info
        data["feature_info"]["all_field_type"] = ["int", "float", "str", "bool"]
        data["feature_info"]["all_data_type"] = ["Y", "ID", "特征"]
        data["feature_info"]["all_distribution_type"] = ["连续型", "离散型"]
        data["base_info"]["feature_count"] = len(list(filter(lambda x: x["data_type"] == "特征", feature_info)))
        try:
            ret = federated_api(job_id=generate_job_id(),
                                method='POST',
                                endpoint="/sample/statistics",
                                src_role="guest",
                                src_party_id=config.local_party_id,
                                dest_party_id=data["base_info"]["party_id"],
                                json_body={"sample_id": sample_id},
                                federated_mode=ENGINES["federated_mode"])
            if ret["retcode"]:
                stat_logger.error(f"%s: {ret['retmsg']}" % str(data["base_info"]["party_name"]))
            data["stats"] = ret.get("data", {})
        except Exception as e:
            stat_logger.exception(e)
    else:
        # 样本信息（样本集类别、特征数量、样本记录数）todo 样本记录数暂时拿不到
        # 求并的特征列表是guest
        # 元数据信息、融合信息
        sample_cols = [VSampleInfoService.model.id.alias("sample_id"), VSampleInfoService.model.v_name.alias(
            "sample_name"), VSampleInfoService.model.party_info, VSampleInfoService.model.mix_type,
                       VSampleInfoService.model.sample_count, VSampleInfoService.model.job_id]
        v_sample_objs = VSampleInfoService.query(id=sample_id, cols=sample_cols)
        if not v_sample_objs:
            return get_json_result(data=False, retmsg="样本不存在", retcode=100)
        v_sample_obj = v_sample_objs[0]
        party_info = v_sample_obj.party_info
        feature_info = get_fusion_fields(party_info, v_sample_obj.mix_type)
        data["feature_info"]["data"] = feature_info
        data["feature_info"]["all_field_type"] = ["int", "float", "str", "bool"]
        data["feature_info"]["all_data_type"] = ["Y", "ID", "特征"]
        data["feature_info"]["all_distribution_type"] = ["连续型", "离散型"]
        sample_list = [info["sample_id"] for info in party_info["host"]]
        sample_list.insert(0, party_info["guest"]["sample_id"])
        fusion_info = SampleService.query(filters=[SampleService.model.id.in_(sample_list)],
                                          cols=[SampleService.model.id.alias(
                                              "sample_id"), SampleService.model.name.alias("sample_name"),
                                              SampleService.model.party_name,
                                              SampleService.model.party_id, SampleService.model.sample_count]).dicts()
        feature_count = len(list(filter(lambda x: x["data_type"] == "特征", feature_info)))
        data["base_info"] = {"sample_count": v_sample_obj.sample_count, "feature_count": feature_count,
                             "sample_name": v_sample_obj.sample_name, "sample_type": v_sample_obj.mix_type}

        jb = JobContentService.get_or_none(job_id=v_sample_obj.job_id)
        if jb:
            data["base_info"]["job_name"] = jb.job_name
            data["base_info"]["module_name"] = WrapperFactory(jb.module_name, 1)
            data["base_info"]["time"] = jb.create_time
            cnvs = ProjectCanvasService.get_or_none(id=jb.canvas_id)
            if cnvs: data["base_info"]["canvas_name"] = cnvs.job_name

        fusion_info_list = []
        temp_local_info = {}
        for i in fusion_info:
            if i['party_name'].find('out_') >= 0:
                i['sample_name'] = '********'
            temp = {"party_name": i["party_name"], "sample_name": i["sample_name"]}
            if i["party_name"] != "本地节点":
                fusion_info_list.append(temp)
            else:
                temp_local_info = temp
        if temp_local_info:
            fusion_info_list.insert(0, temp_local_info)
        data["fusion_info"] = fusion_info_list
        data["feature_info"]["all_party"] = list(set([j["party_name"] for j in fusion_info]))
    return get_json_result(data=data)


@manager.route("/data/detail", methods=['POST'])
@login_required
@validate_request("sample_id", "limit")
def data_detail():
    smp_id, limit = request.json["sample_id"], request.json["limit"]

    nms = SampleService.sample_name_type(smp_id)
    if not nms:
        return get_data_error_result(100, "Sorry, 样本不存在！")
    sample = nms[0]
    if sample["type"] == "本地文件":
        df = get_data_by_name(sample["name"])
        if not df: return get_data_error_result(100, "Sorry, 无权查看样本数据！")
        df, cnt = df
    else:
        sess = Session()
        table = sess.get_table(
            name=sample["name"], namespace="experiment"
        )
        flag, msg, df, schema = table.read_fl_table(sql=table.meta.schema.get("sql"), part_of_data=False)
        df.fillna("", inplace=True)
        cnt = len(df)
    if cnt is None: cnt = len(df)
    cnt = max(cnt, len(df))
    sts = statistics(df)
    feature_cols = [SampleFieldsService.model.field_name.alias("特征名称"),
                    SampleFieldsService.model.distribution_type.alias("分布"),
                    SampleFieldsService.model.data_type.alias("业务属性"),
                    SampleFieldsService.model.field_type.alias("数据类型"),
                    SampleFieldsService.model.field_examples.alias("数据示例"),
                    SampleFieldsService.model.field_description.alias("描述")]
    clmns = list(SampleFieldsService.query(sample_id=smp_id, cols=feature_cols).dicts())
    return get_json_result(data={
        "total": cnt,
        "loaded": min(limit, cnt),
        "column_num": len([0 for c in clmns if c["业务属性"] == "特征"]),
        "rows": df.iloc[0: limit, 0:256].to_dict("records"),  # df2json(df.iloc[0: limit, 0:256]),
        "statistic": sts,
        "columns": clmns,
        "is_all_columns_included": 256 > len(df.columns)
    })


@manager.route("/statistics", methods=['POST'])
@check_license
@validate_request("sample_id")
def feature_statistics():
    smp_id = request.json["sample_id"]
    nms = SampleService.sample_names(smp_id)
    if not nms:
        return get_data_error_result(100, "Sorry, 样本不存在！")
    nms = nms[0]["name"]
    df = get_data_by_name(nms)
    if not df: return get_data_error_result(100, "Sorry, 无权查看样本数据！")
    df, cnt = df
    sts = statistics(df)
    return get_json_result(data=sts)


@manager.route("/data/can_union_or_not", methods=['POST'])
@login_required
@validate_request("sample_ids")
def data_can_union_or_not():
    smp_ids = request.json["sample_ids"]
    nms = SampleFieldsService.is_samples_field_different(smp_ids)
    if not nms: return get_json_result(data=[])

    return get_data_error_result(100, f"Sorry, {nms} 样本特征不同，暂不支持多选！")


@manager.route("/data/union", methods=['POST'])
@login_required
@validate_request("sample_ids", "new_name")
def data_union():
    if not request.json["new_name"]: return get_data_error_result(100, "请为您的新样本取个靓名！")

    obj = SampleService.query(name=request.json["new_name"])
    if obj:
        return get_data_error_result(100, "Sorry, 样本名称已存在，请重新取个靓名！")

    smp_ids = request.json["sample_ids"]
    if len(smp_ids) < 2: return get_data_error_result(100, "Sorry, 请选择多个样本！")

    nms = SampleService.sample_names(smp_ids)
    if not nms:
        return get_data_error_result(100, "Sorry, 样本不存在！")

    ids = set([n["id"] for n in nms])
    for i in smp_ids:
        if i not in ids:
            return get_data_error_result(100, f"Sorry, {i}样本不存在！")

    nms = [n["name"] for n in nms]

    from fate_flow.web_server.pipeline_wrapper import UnionWrapper
    pip = UnionWrapper(role="guest", pid=config.local_party_id, guest=config.local_party_id)
    try:
        jid, mdl_info = pip.exe([{"name": n, "namespace": config.namespace} for n in nms])
        return get_json_result(data={
            "job_id": jid,
            "component_name": "outs",
            "model_info": mdl_info
        })
    except Exception as e:
        return server_error_response(e)


@manager.route("/data/transform", methods=['POST'])
@login_required
@validate_request("guest", "canvas_id")
def data_transform():
    try:
        return get_json_result(data=data_transform(request.json, current_user.username))
    except Exception as e:
        return server_error_response(e)


@manager.route("/features", methods=["POST"])
@login_required
@validate_request("job_id")
def features():
    jid = request.json["job_id"]
    both_side = request.json.get("both_side", True)
    used_mdl = request.json.get("used_module", "")
    party_id = request.json.get('party_id', config.local_party_id)
    role = request.json.get('role', 'guest')

    jb = JobContentService.get_or_none(job_id=jid)
    if not jb: return get_data_error_result(100, retmsg="Sorry，找不到上游任务！")

    from fate_flow.web_server.pipeline_wrapper import component_data_features
    gst_feas, stats = component_data_features(request.json["job_id"], role=role, party_id=party_id, stats=True)
    if not gst_feas: return get_data_error_result(100, retmsg="Sorry, 找不到上游任务产生的数据，请确认上游任务已经成功执行！")

    def filterout_features(df):
        nonlocal used_mdl
        if df is None or df.empty: return df
        df["field_name"] = df["field_name"].map(lambda x: x.lower())
        t = "连续型"
        if re.search(r"onehot", used_mdl, flags=re.IGNORECASE): t = "离散型"
        if re.search(r"selection", used_mdl, flags=re.IGNORECASE): return df
        return df[df.distribution_type == t].reset_index()

    def feature_info(feas, df, lbl=""):
        if not feas or df is None or df.empty: return
        feas = [f for f in feas if f.lower() != lbl.lower()] if lbl else feas
        feas = {f: i for i, f in enumerate(feas)}
        idx = []
        for ii, row in df.iterrows():
            if row["field_name"] not in feas: continue
            idx.append((feas[row["field_name"]], ii))
        if not idx: return []
        return df.iloc[[i for _, i in sorted(idx)]].to_dict("records")

    def clean_stats(feas: list, sta: dict):
        if not feas: return {}
        feas = list(set([f["field_name"].lower() for f in feas]) & set([k.lower() for k in sta.keys()]))
        return {k: v for k, v in sta.items() if k in feas}

    res = {"guest": [], "host": {}, "host_stats": {}}
    if role == 'guest':
        gst_smp_id = jb.party_info.get("guest", {}).get("sample_id", [])
    else:
        gst_smp_id = \
        [p.get("sample_id", "") for p in jb.party_info.get("host", []) if str(p.get("party_id", "")) == str(party_id)][
            0]

    if gst_smp_id:
        res[role] = feature_info(gst_feas,
                                 filterout_features(get_field_info_df([gst_smp_id], "")),
                                 jb.party_info.get("guest", {}).get("label_name", []))

        res[f"{role}_stats"] = clean_stats(res[role], stats)

    if role == "host":
        res["host"] = {party_id: res["host"], 'host_stats': res['host_stats']}
        del res['host_stats']
        return get_json_result(data=res)

    hst_feas = {}
    hst_stats = {}
    if both_side:
        endpoint = "/canvas/component/data/features"
        error_info = {}
        host_party_ids = [host["party_id"] for host in jb.party_info.get("host", [])]
        host_smp_ids = [host["sample_id"] for host in jb.party_info.get("host", [])]
        lbl_nms = [host.get("label_name", "") for host in jb.party_info.get("host", [])]
        for i, dest_party_id in enumerate(host_party_ids):
            try:
                ret = federated_api(job_id=jid,
                                    method='POST',
                                    endpoint=endpoint,
                                    src_role=role,
                                    src_party_id=party_id,
                                    dest_party_id=dest_party_id,
                                    json_body={"job_id": jid, "role": "host" if role == 'guest' else 'guest',
                                               "party_id": dest_party_id, "stats": True},
                                    federated_mode=ENGINES["federated_mode"])
                if ret["retcode"]:
                    error_info[dest_party_id] = ret["retmsg"]
                    stat_logger.error(f"{dest_party_id}: {ret['retmsg']}")
                else:
                    hst_feas[dest_party_id] = feature_info(ret["data"]["features"],
                                                           filterout_features(get_field_info_df([host_smp_ids[i]], "")),
                                                           lbl_nms[i])
                    hst_stats[dest_party_id] = clean_stats(hst_feas[dest_party_id], ret["data"]["stats"])
            except Exception as e:
                stat_logger.exception(e)
                error_info[dest_party_id] = str(e)

        res["host"] = hst_feas
        res["host_stats"] = hst_stats

    return get_json_result(data=res)
