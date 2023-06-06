import sys
sys.path.append("./")
from psi_wrapper import PsiWrapper
from prepare import *


HOST_TABLES = {
    "name": "breast_homo_host",
    "namespace": "experiment"
}

GUEST_TABLE = {
    "name": "breast_homo_guest",
    "namespace": "experiment"
}

GUEST_ONLY_PARAM = {
    "with_label": False,
    "output_format": "dense",
}

HOST_ONLY_PARAM = {
    "with_label": False,
    "output_format": "dense",
}

PSI_PARAM = {
    "max_bin_num": 20,
    "need_run": True,
    "dense_missing_val": None,
    "binning_error": 1e-4,
}

def psi(base_param, psi_param=PSI_PARAM):
    job = PsiWrapper(**base_param)
    job.setReader()
    job.exe(psi_param)

def test_psi():

    jobid = read(GUEST_TABLE, HOST_TABLES)
    jobid = data_transform(jobid, GUEST_ONLY_PARAM, HOST_ONLY_PARAM)
    
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'PSI'
    psi(base_param)


if __name__ == "__main__":

    test_psi()
