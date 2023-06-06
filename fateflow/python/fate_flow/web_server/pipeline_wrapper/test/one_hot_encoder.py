import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
from fate_flow.web_server.pipeline_wrapper import wrapper

COMMON_PARAM = {"transform_col_indexes": None, "transform_col_names": ["sex"], "need_run":True}
MODULE = "OneHotEncoder"


def base(jobid):
    global COMMON_PARAM
    wrapper.t_(jobid, MODULE, guest_only_param=COMMON_PARAM, host_only_param={10000:{"transform_col_indexes": None,
                                                                                "transform_col_names": ["sex"], "need_run":False}}, ml=False)


if __name__ == "__main__":
    jid = prepare.a_jobid()
    # jobid = "202303080032028318590"
    base(jid)
