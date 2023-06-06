import requests
import json
headers = {
    'currentChains': '{"key":"explorer_1","name":"seceum","id":"s3sgv8kiq8"}',
}
url = "http://150.158.83.219:58080/v2/tx/store?ledger=s3sgv8kiq8&sync=true"
# response = requests.post('http://150.158.83.219:8001/explorer-b/home/getSummary', cookies=cookies, headers=headers, verify=False)
data={"data":str({"a":1,"b":2,"c":[1,2,3]})}
print(data)
response = requests.post(url ,json=data ,verify=False)
print(response.json())


