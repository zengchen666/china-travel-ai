# -*- coding: utf-8 -*-
import requests
import json

url = 'https://m.ctrip.com/restapi/soa2/18109/json/getAttractionList'
payload = {
    'index': 1,
    'count': 5,
    'sortType': 1,
    'districtId': 1,
    'scene': 'DISTRICT',
    'head': {'cid': '09031177210123456789', 'ctok': '', 'cver': '1.0', 'lang': '01', 'sid': '8888', 'syscode': '09'}
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

r = requests.post(url, json=payload, headers=headers, timeout=15)
data = r.json()

print('Response keys:', list(data.keys()))
print()

# 保存完整响应用于分析
with open('data/api_response.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Response saved to data/api_response.json')
