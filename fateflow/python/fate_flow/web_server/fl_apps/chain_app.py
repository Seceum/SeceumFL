import json, re
from flask_login import login_required
import os
from flask import request
from fate_arch.common import file_utils
from fate_flow.settings import stat_logger
from fate_flow.utils.api_utils import get_json_result
import requests

try:
    config_path = os.path.join("conf", "chain_config.yaml")
    conf = file_utils.load_yaml_conf(config_path)
    headers = {
        'currentChains': json.dumps({'key': conf["key"], 'name': conf["name"], 'id': conf["id"]}),
    }
    conf["b-explore"] = re.sub("home/getSummary", "", conf["summary_url"])
except Exception as e:
    stat_logger.exception(e)
    conf = {}
    headers = {}


@manager.route('/summary', methods=['POST'])
@login_required
def summary():
    """区块链统计"""
    try:
        response = requests.post(conf["summary_url"], verify=False, headers=headers).json()
        if response["code"] == 200:
            return get_json_result(data=response["data"])
        else:
            return get_json_result(data=[], retcode=100, retmsg=response["msg"])
    except:
        return get_json_result(data=[], retcode=100, retmsg="backend clain config error")


@manager.route('/recentStatistics', methods=['POST'])
@login_required
def recent_statistics():
    """区块链最近统计"""
    try:
        response = requests.post(conf["recentStatistics_url"], verify=False, headers=headers).json()
        if response["code"] == 200:
            return get_json_result(data=response["data"])
        else:
            return get_json_result(data=[], retcode=100, retmsg=response["msg"])
    except:
        return get_json_result(data=[], retcode=100, retmsg="backend clain config error")


@manager.route('/getBlockList', methods=['POST'])
@login_required
def get_block_list():
    try:
        response = requests.post(conf["b-explore"] + "block/getBlockList", data=request.json, verify=False,
                                 headers=headers).json()
        if response["code"] == 200:
            return get_json_result(data=response["data"])
        else:
            return get_json_result(data=[], retcode=100, retmsg=response["msg"])
    except:
        return get_json_result(data=[], retcode=100, retmsg="backend clain config error")


@manager.route('/getBlockDetail', methods=['POST'])
@login_required
def get_block_detail():
    try:
        response = requests.post(conf["b-explore"] + "block/getBlockDetail", data=request.json, verify=False,
                                 headers=headers).json()
        if response["code"] == 200:
            return get_json_result(data=response["data"])
        else:
            return get_json_result(data=[], retcode=100, retmsg=response["msg"])
    except:
        return get_json_result(data=[], retcode=100, retmsg="backend clain config error")


@manager.route('/getNodeList', methods=['POST'])
@login_required
def get_node_list():
    try:
        response = requests.post(conf["b-explore"] + "node/getNodeList", data=request.json, verify=False,
                                 headers=headers).json()
        if response["code"] == 200:
            return get_json_result(data=response["data"])
        else:
            return get_json_result(data=[], retcode=100, retmsg=response["msg"])
    except:
        return get_json_result(data=[], retcode=100, retmsg="backend clain config error")


@manager.route('/getTxList', methods=['POST'])
@login_required
def get_tx_list():
    try:
        response = requests.post(conf["b-explore"] + "tx/getTxList", data=request.json, verify=False,
                                 headers=headers).json()
        if response["code"] == 200:
            return get_json_result(data=response["data"])
        else:
            return get_json_result(data=[], retcode=100, retmsg=response["msg"])
    except:
        return get_json_result(data=[], retcode=100, retmsg="backend clain config error")


@manager.route('/getTxDetail', methods=['POST'])
@login_required
def get_tx_detail():
    try:
        response = requests.post(conf["b-explore"] + "tx/getTxDetail", data=request.json, verify=False,
                                 headers=headers).json()
        if response["code"] == 200:
            return get_json_result(data=response["data"])
        else:
            return get_json_result(data=[], retcode=100, retmsg=response["msg"])
    except:
        return get_json_result(data=[], retcode=100, retmsg="backend clain config error")
