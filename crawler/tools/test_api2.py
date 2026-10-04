# -*- coding: utf-8 -*-
import requests
import json

url = 'https://m.ctrip.com/restapi/soa2/18109/json/getAttractionList'
payload = {
    'index': 1,
    'count': 3,
    'sortType': 1,
    'districtId': 2,
    'scene': 'DISTRICT',
    'head': {'cid': '09031177210123456789', 'ctok': '', 'cver': '1.0', 'lang': '01', 'sid': '8888', 'syscode': '09'}
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0', 'Content-Type': 'application/json'}

r = requests.post(url, json=payload, headers=headers, timeout=15)
data = r.json()

print('Status:', r.status_code)
print('Keys:', list(data.keys()))

with open('data/api_test.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Saved to data/api_test.json')
