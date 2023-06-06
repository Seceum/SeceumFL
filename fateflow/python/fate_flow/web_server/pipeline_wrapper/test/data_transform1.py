import sys
sys.path.append("./")
import wrapper
import copy


guest_only_param = {
    "feature":["x1","x5"],
    "outlier_replace":True,
    "outlier_replace_method":"designated",
    "outlier_impute":[1,1],
    "outlier_replace_value":[10,11],
    "with_label":True,
    "label_name":"LABEL",
    "missing_fill":False,
    "missing_fill_method":"mean"}

host_only_param = {
    "with_label":False,
     "missing_fill":False,
     "missing_fill_method":"designated",
     "default_value":0,
    "feature":["x20"],
    "outlier_replace":True,
    "outlier_replace_method":"designated",
    "outlier_impute":[-1],
    "outlier_replace_value":[100]
}
BASE_PARAM = {
    "pid":9999,
    "guest":9999,
    "hosts":[10000],
    "arbiter":10000,
    "role":"guest"
}
MODULE = "DataTransform1"

GUEST_TABLE = {
    "name":"ionosphere_scale_hetero_guest",
    "namespace":"experiment"
}

HOST_TABLE = {
    "name":"ionosphere_scale_hetero_host",
    "namespace":"experiment"
}

def read(guest_tab=GUEST_TABLE,host_tab=HOST_TABLE):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["cmp_nm"] = "Reader"
    job = wrapper.WrapperBase(**base_param)
    job.setReader(gst_tab=guest_tab,host_tb={"10000":host_tab})
    newjobid,_ = job.exe()
    return newjobid

GUEST_ONLY_PARAM = {
    "with_label":True,
     "label_name":"LABEL",
    "missing_fill":False,
     "missing_fill_method":"mean",
      # designated ok
     "feature":["x1", "x5"],
     "outlier_replace":False,
      # outlier_replace_method is asmissing outlier_replace_value=None
      "outlier_replace_method":"designated",
      "outlier_impute":[1, 1],
      "outlier_replace_value":[10, 11]
}

HOST_ONLY_PARAM = {
    "with_label":False,
    "missing_fill":False,
    "missing_fill_method":"designated",
    "default_value":0,
    "outlier_replace":False
}

def data_transform1(newjobid,guest_only_param = guest_only_param,host_only_param = host_only_param):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = newjobid
    base_param["cpn4reader"] = "reader"
    base_param["cmp_nm"] = "DataTransform1"
    job = wrapper.WrapperBase(**base_param)
    job.setReader()
    newjobid4,_ = job.exe(guest_only_param=guest_only_param,host_only_param=host_only_param)
    print("data transform1 new jobid----",newjobid4)
    return newjobid4

def data_transform(newjobid,guest_only_param=GUEST_ONLY_PARAM,host_only_param=HOST_ONLY_PARAM):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = newjobid
    base_param["cpn4reader"] = "reader"
    base_param["cmp_nm"] = "DataTransform"
    job = wrapper.WrapperBase(**base_param)
    job.setReader()
    newjobid1,_ = job.exe(guest_only_param=guest_only_param,host_only_param=host_only_param)
    print("data transform new jobid---",newjobid1)
    return newjobid1

def intersection(newjobid):
    base_param = copy.deepcopy(BASE_PARAM)
    base_param["jid4reader"] = newjobid
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
    newjobid3,_ = job.exe(common_param=COMMON_PARAM)
    print("intersection jobid----",newjobid3)
    return newjobid3


def base(jobid):
    global COMMON_PARAM
    if jobid:
        wrapper.t_(jobid,MODULE,guest_only_param=guest_only_param,host_only_param=host_only_param,cpn="intersection_0",ml=False)
    elif jobid is None:
        newjobid = read()
        newjobid1 = data_transform(newjobid)
        newjobid2 = intersection(newjobid1)
        newjobid3 = data_transform1(newjobid2)


if __name__ == "__main__":
    jobid = "202210211628400101130"
    base(None)