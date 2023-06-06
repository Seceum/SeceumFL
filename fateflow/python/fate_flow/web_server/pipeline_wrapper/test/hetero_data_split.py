import sys
sys.path.append("./")
import wrapper

MODULE = "HeteroDataSplit"
COMMON_PARAM = {
    "stratified":True,
    "test_size":0.3, "split_points":[0.0, 0.2]
}

def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid,MODULE,common_param=COMMON_PARAM,cpn="intersection_0",ml=False)

if __name__ == "__main__":
    jobid = "202210201411545685130"
    base(jobid)