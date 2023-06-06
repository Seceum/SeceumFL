import requests
headers = {
    'currentChains': '{"key":"explorer_1","name":"seceum","id":"s3sgv8kiq8"}',
}

# response = requests.post('http://150.158.83.219:8001/explorer-b/home/getSummary', cookies=cookies, headers=headers, verify=False)
response = requests.post('http://150.158.83.219:8001/explorer-b/home/recentStatistics', verify=False,headers=headers)
print(response.json())