import requests

from fate_flow.web_server.fl_config import get_cf

cf = get_cf()
params= {
    'query': 'node_memory_MemTotal_bytes{instance="10.0.12.9:9100",job="node"}',
    'start': '1680168600',
    'end': '1680255000',
    'step': '120',
}
cookies= ""
def get_grafana_cookies():
    json_data = {
        'user': cf.get("grafana_user"),
        'password': cf.get("grafana_passwd"),
    }
    response = requests.post('http://%s/login'%cf.get("grafana_url"), json=json_data, verify=False)
    return response.cookies

def request_grafana(params,cookies):
    url = 'http://%s/api/datasources/proxy/1/api/v1/query_range' % cf.get("grafana_url")
    try:
        response = requests.get(
            url,
            params=params,
            cookies=cookies,
            verify=False,
            timeout=3
        )
    except requests.exceptions.ConnectionError as e:
        return False, "grafana url错误或网络不通", cookies
    except Exception as e:
        return False, str(e), cookies
    if response.status_code==200:
        return True,response.json()["data"],cookies
    else:
        cookies = get_grafana_cookies()
        response = requests.get(
            url,
            params=params,
            cookies=cookies,
            verify=False,
        )
        if response.status_code == 200:
            return True, response.json()["data"], cookies
        return False,response.json()["message"],cookies
if __name__ == '__main__':
    # flag,data,cookies =request_grafana(params,cookies)
    # print("data",data)
    print(cf.get("prometheus_instance"))