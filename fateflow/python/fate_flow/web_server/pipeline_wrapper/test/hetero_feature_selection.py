import sys
sys.path.append("./")
from prepare import a_jobid, upload
from fate_flow.web_server.pipeline_wrapper.feature_selection_wrapper import *
from fate_flow.web_server.pipeline_wrapper import wrapper
import copy


HOST_TABLES = {
    "name": "breast_hetero_host",
    "namespace": "experiment"
}

GUEST_TABLE = {
    "name": "breast_hetero_guest",
    "namespace": "experiment"
}

HOMO_HOST_TABLES = {
    "name":"breast_homo_host",
    "namespace": "experiment"
}

HOMO_GUEST_TABLES = {
    "name":"breast_homo_guest",
    "namespace":"experiment"
}

def scale(jobid):

    new_job_id, _ = wrapper.t_(jobid, cmp_nm="FeatureScale", cpn='outs',ml=False)
    return new_job_id


def feature_selection(base_param, selection_param, gst_param=None, hst_param=None):

    job = HeteroFeatureSelectionWrapper(**base_param)
    job.setReader()
    job.exe(selection_param, gst_param, hst_param,asyn=False)


def testcase_manually():
    jobid = "202212141110272631770"#a_jobid()
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'
    selection_param = {
        "name": "hetero_feature_selection_0",
            "select_col_indexes":[],
        "select_names": ["x5","x6","x7","x8"],
        "filter_methods": ["statistic_filter"],
        "iv_param": {
            "threshold": 0.4
        },
        "statistic_param": {
            "metrics": ["skewness"],
            "filter_type": "threshold",
            "threshold": 0.5
        }
    }
    hst_param = {
        10000:{
            "select_col_indexes":[],
        "select_names": ["x0","x5","x6","x7","x8"],
        "filter_methods": ["statistic_filter", "manually"],
        "iv_param": {
            "threshold": 0.4
        },
        "manually_param": {
            "filter_out_indexes": None,
            "filter_out_names": ["x0"],
            "left_col_indexes": None,
            "left_col_names": None
        },
        "statistic_param": {
            "metrics": ["skewness"],
            "filter_type": "threshold",
            "threshold": 0.2
        }
    }}
    feature_selection(base_param, selection_param, hst_param=hst_param)


def testcase_homosbt():
    jobid = a_jobid(HOMO_GUEST_TABLES, HOMO_HOST_TABLES,
                     host_only_param={"with_label": True},
                    do_intersect=False)
    jobid = scale(jobid)
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'

    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "homo_sbt_filter"
        ],
        "sbt_param": {
            "metrics": "feature_importance",
            "filter_type": "threshold",
            "take_high": True,
            "threshold": 0.03
        }
    }
    feature_selection(base_param, selection_param)


def testcase_xgb_hetero(d):

    jobid = a_jobid()
    jobid = scale(jobid)
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'
    
    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "hetero_sbt_filter"
        ],
        "sbt_param": {
            "metrics": "feature_importance",
            "filter_type": "threshold",
            "take_high": True,
            "threshold": 0.03
        }
    }
    feature_selection(base_param, selection_param)


def testcase_xgb_homo():
    jobid = a_jobid(host_only_param={"with_label":True}, do_intersect=False)
    jobid = scale(jobid)
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'
    
    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "homo_sbt_filter"
        ],
        "sbt_param": {
            "metrics": "feature_importance",
            "filter_type": "threshold",
            "take_high": True,
            "threshold": 0.03
        }
    }
    feature_selection(base_param, selection_param)


def testcase_feature_iv():
    jobid = a_jobid()
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'

    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "iv_value_thres"
        ],
        "iv_value_param": {
            "value_threshold": 0.1
        }
    }
    feature_selection(base_param, selection_param)


def testcase_feature_iv_top_k():
    jobid = a_jobid()
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'
    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "iv_top_k"
        ],
        "iv_top_k_param": {
            "k": 7,
            "local_only": False
        }
    }
    feature_selection(base_param, selection_param)


def testcase_feature_statistic():

    jobid = a_jobid()
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'

    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "statistic_filter"
        ],
        "statistic_param": {
            "metrics": ["skewness", "skewness", "kurtosis", "median"],
            "filter_type": "threshold",
            "take_high": [True, False, True, True],
            "threshold": [-10, 10, -1.5, -1.5]
        },
    }
    feature_selection(base_param, selection_param)


def testcase_feature_vif():

    jobid = a_jobid()
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'

    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "vif_filter"
        ],
        "vif_param": {
            "threshold": 5
        }
    }
    feature_selection(base_param, selection_param)


def testcase_feature_correlation():

    jobid = a_jobid()
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'

    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "correlation_filter"
        ]
    }
    feature_selection(base_param, selection_param)


def testcase_feature_psi():

    jobid = a_jobid()
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'

    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "psi_filter"
        ],
        "psi_param": {
            "metrics": "psi",
            "filter_type": "threshold",
            "take_high": False,
            "threshold": -0.1
        },
    }
    feature_selection(base_param, selection_param)


def testcase_feature_all():

    jobid = a_jobid()
    jobid = scale(jobid)
    base_param = copy.deepcopy(BASE_PARAM)
    base_param['jid4reader'] = jobid
    base_param['cpn4reader'] = 'outs'
    base_param['cmp_nm'] = 'HeteroFeatureSelection'
    selection_param = {
        "name": "hetero_feature_selection_0",
        "select_col_indexes": -1,
        "select_names": [],
        "filter_methods": [
            "psi_filter",
            "correlation_filter",
            "vif_filter",
            "statistic_filter",
            "iv_top_k",
            "iv_value_thres",
        ],
        "psi_param": {
            "metrics": "psi",
            "filter_type": "threshold",
            "take_high": False,
            "threshold": -0.1
        },
        "vif_param": {
            "threshold": 5
        },
        "statistic_param": {
            "metrics": ["skewness", "skewness", "kurtosis", "median"],
            "filter_type": "threshold",
            "take_high": [True, False, True, True],
            "threshold": [-10, 10, -1.5, -1.5]
        },
        "iv_top_k_param": {
            "k": 7,
            "local_only": False
        },
        "iv_value_param": {
            "value_threshold": 0.1
        }
    }
    feature_selection(base_param, selection_param)



if __name__ == "__main__":

    #upload(GUEST_TABLE, HOST_TABLES)
    testcase_manually()
    # testcase_homosbt()
    # testcase_feature_iv()
    # testcase_feature_psi()
    # testcase_feature_iv_top_k()
    # testcase_feature_statistic()
    # testcase_feature_vif()
    # testcase_feature_correlation()
    # testcase_feature_all()
    # testcase_xgb_hetero()
