import sys
sys.path.append("../")
from fate_flow.web_server.pipeline_wrapper import PredictWrapper, Factory
import copy,prepare


# 模型加载参数
MDL_PARAM = {
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    # 多个job或model_version
    "model_versions": [
        ("202210261309107620300", ["FeatureScale:outs"]),
        ("202210261309334053120", ["HeteroFeatureSelection"]),
        #("202210191718094565380", ["OneHotEncoder"]),
        ("202210261345194897290", ["HeteroLR:outs"])
    ]
}
MDL_PARAM_FEATURE_SELECT = {
    "model_id": "guest-9999#host-10000#model",
    "model_versions": [
        # 多个feature selection 组件，model version和组件需要一一对应起来
        ("202210201120144748370",["hetero_feature_selection_0"])
    ],
}

BASE_PARAM = {
    "pid": 9999,
    "guest": 9999,
    "hosts": [10000],
    "role": "guest"
}

def base_multijob_single_component(jobid):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = jobid
    # 初始化输入
    base_param["cpn4reader"] = MDL_PARAM["data_source"]
    del MDL_PARAM["data_source"]
    MODULE = Factory("".join(MDL_PARAM["model_versions"][-1][-1][-1].split("_")[0:-1]))
    #最后一个组件
    base_param["cmp_nm"] = MODULE.__name__
    pw = PredictWrapper(**base_param)
    pw.setReader()
    pw.exe(mdl_param=MDL_PARAM)

def base_feature_select(jobid):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = jobid
    # 初始化输入
    base_param["cpn4reader"] = MDL_PARAM_FEATURE_SELECT["data_source"]
    del MDL_PARAM_FEATURE_SELECT["data_source"]
    MODULE = Factory("".join(MDL_PARAM_FEATURE_SELECT["model_versions"][-1][-1][-1].split("_")[0:-1]))
    # 最后一个组件
    base_param["cmp_nm"] = MODULE.__name__
    pw = prepare.PredictWrapper(**base_param)
    pw.setReader()
    pw.exe(mdl_param=MDL_PARAM_FEATURE_SELECT)

def base_multijob_single_component(jobid):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = jobid
    # 初始化输入
    base_param["cpn4reader"] = "reader"
    pw = PredictWrapper(**base_param)
    pw.setReader()
    pw.exe(mdl_param=MDL_PARAM)

if __name__ == "__main__":
    # To test PredictWrappr, you could run 'hetero_feature_selection::testcase_feature_all()' to get the jobid firstly,
    # then, run one hot encoder and hetero lr

    jid = prepare.a_jobid()
    base_multijob_single_component(jid)
    sys.exit()

    jobid = "202210201120144748370"
    base_feature_select(jobid)