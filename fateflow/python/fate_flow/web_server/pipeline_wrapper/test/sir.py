import sys

from fate_flow.web_server.pipeline_wrapper.test import prepare

sys.path.append("./")
import wrapper
import copy

MODULE = "SecureInformationRetrieval"

COMMON_PMARA = {
    "security_level": 0.5,
        "oblivious_transfer_protocol": "OT_Hauck",
        "commutative_encryption": "CommutativeEncryptionPohligHellman",
        "non_committing_encryption": "aes",
        "dh_params": {
            "key_length": 1024
        },
        "raw_retrieval": False,
        "target_cols": ["x0","x1","x2"],
        # add by tjx 2022616
        "target_ids":[13,14,15]
}

def base(jid):
    if not jid: jid = prepare.a_jobid(do_intersect=False)
    wrapper.t_(jid, MODULE, common_param=COMMON_PMARA, ml=False)

if __name__ == "__main__":
    jid = "202211031258579798730"
    base(jid)