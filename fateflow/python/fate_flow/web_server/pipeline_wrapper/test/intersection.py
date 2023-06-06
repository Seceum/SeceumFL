import sys, os
sys.path.append("./")
from pipeline.backend.pipeline import PipeLine
import wrapper

def base(jid):
    j = wrapper.t_(jid = jid, cmp_nm="Intersection",
            common_param = {
            "intersect_method": "dh",
            "sync_intersect_ids": True,
            "only_output_key": False,
            "dh_params": {
                "hash_method": "sha256",
                "salt": "12345",
                "key_length": 1024
            }
        },
        ml = False
    )


if __name__  ==  "__main__":
    base("202210081603355890570")

