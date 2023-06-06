import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper
import copy

MODULE = "HeteroSecureBoost"
COMMON_PARAM = {
    "num_trees":3,
    "task_type":"classification",
    "objective_param":{"objective": "cross_entropy"},
    "encrypt_param":{"method": "Paillier"},
    "tree_param":{"max_depth": 3},
    "validation_freqs":1,
    "cv_param" : {
        "need_cv": False,
        "n_splits": 5,
        "shuffle": False,
        "random_seed": 103
    }
}

GUEST_ONLY_PARAM = {
    "with_label":True,
    "output_format":"dense"
}

HOST_ONLY_PARAM = {
    "with_label":False
}
BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}
SPLIT_PARAM = {
    "stratified":True,
    "test_size":0.2,
    "validate_size":0.3,
    "split_points":[0,0.2]
}
EVA_PARAM = {
    "eval_type":"binary",
    "pos_label":1
}
def read(guest_tab=GUEST_TABLE,host_tab=HOST_TABLE):
    param = copy.deepcopy(BASE_PARAM)
    param["cmp_nm"] = "Reader"
    job = wrapper.WrapperBase(**param)
    job.setReader(gst_tab=guest_tab,host_tb={"10000":host_tab})
    jobid,_= job.exe()
    print("jobid reader---",jobid)
    return jobid

def data_transform(jobid,guest_only_param=GUEST_ONLY_PARAM,host_only_param=HOST_ONLY_PARAM):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = jobid
    base_param["cpn4reader"] = "reader"
    base_param["cmp_nm"] = "DataTransform"
    job = wrapper.WrapperBase(**base_param)
    job.setReader()
    new_jobid,_ = job.exe(guest_only_param=guest_only_param,host_only_param=host_only_param)
    print("jobid data transform---",new_jobid)
    return new_jobid

def intersection(jobid):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = jobid
    base_param["cpn4reader"] = "reader"
    base_param["cmp_nm"] = "Intersection"
    job = wrapper.WrapperBase(**base_param)
    job.setReader()

    COMMON_PARAM = {"intersect_method": "rsa",
        # "sync_intersect_ids": True,
        "only_output_key": False,
        "rsa_params": {
            "hash_method": "sha256",
            "final_hash_method": "sha256",
            "key_length": 2048
        }}
    new_jobid, _ = job.exe(common_param=COMMON_PARAM)
    # new_jobid,_ = wrapper.t_(jobid,cmp_nm="Intersection",cpn="outs",common_param=COMMON_PARAM,ml=False)
    print("jobid intersection---",new_jobid)
    return new_jobid

def hetero_secure_boost(jobid,split_param=None,eva_param=None,cv=False):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = jobid
    base_param["cpn4reader"] = "reader"
    base_param["cmp_nm"] = MODULE
    job = wrapper.WrapperBase(**base_param)
    job.setReader()
    # new_jobid,_ = job.exe(common_param=COMMON_PARAM)
    new_jobid = None
    if cv:
        COMMON_PARAM["cv_param"] = {"n_splits": 4,
                                    "shuffle": True,
                                    "random_seed": 33,
                                    "need_cv": True}
        new_jobid,_ = wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM)
    if split_param is None or eva_param is None:
        new_jobid,_ = wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM)
    elif split_param and eva_param is None:
        new_jobid,_ = wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=split_param)
    elif eva_param and split_param is None:
        new_jobid,_ = wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,eva_param=eva_param)
    elif split_param and eva_param:
        new_jobid,_ = wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,split_param=split_param,eva_param=eva_param)
    print("hetero secure boost---",new_jobid)

def base(jobid):
    global COMMON_PARAM
    if jobid is None:
        jid = prepare.a_jobid()
        jobid4 = hetero_secure_boost(jid)
    else:
        wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="intersection_0")

def split(jobid):
    global COMMON_PARAM,SPLIT_PARAM
    if jobid is None:
        jid = prepare.a_jobid()
        jobid4 = hetero_secure_boost(jid,SPLIT_PARAM)
    else:
        wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="intersection_0",split_param=SPLIT_PARAM)

def split_and_eva(jobid):
    global COMMON_PARAM,SPLIT_PARAM,EVA_PARAM
    if jobid:
        wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="intersection_0",split_param=SPLIT_PARAM,eva_param=EVA_PARAM)
    elif jobid is None:
        jid = prepare.a_jobid()
        jobid4 = hetero_secure_boost(jid,SPLIT_PARAM,EVA_PARAM)

def eva(jobid):
    global COMMON_PARAM,EVA_PARAM
    if jobid:
        wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="intersection_0",eva_param=EVA_PARAM)
    elif jobid is None:
        jid = prepare.a_jobid()
        jobid4 = hetero_secure_boost(jid,eva_param=EVA_PARAM)

def cv(jobid):
    global COMMON_PARAM
    COMMON_PARAM["cv_param"] = {"n_splits": 4,
                                "shuffle": True,
                                "random_seed": 33,
                                "need_cv": True}

    if jobid:
        wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="intersection_0")
    elif jobid is None:
        jid = prepare.a_jobid()
        jobid4 = hetero_secure_boost(jid,cv=True)


if __name__ == "__main__":
    jobid = "202210201514581518030"
    base(None)
    # split(None)
    # split_and_eva(None)
    # eva(None)
    cv(None)