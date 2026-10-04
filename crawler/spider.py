# -*- coding: utf-8 -*-
"""携程景点爬虫 - 修复版"""
import requests
import json
import time
import os
import random
from config import CITIES, HEADERS, REQUEST_DELAY, MAX_PAGES, DATA_DIR


class CtripSpider:
    def __init__(self):
        self.session = requests.Session()
        self.all_attractions = []
        
    def get_attractions(self, city_id, page=1):
        url = 'https://m.ctrip.com/restapi/soa2/18109/json/getAttractionList'
        payload = {
            'index': page, 'count': 20, 'sortType': 1,
            'districtId': city_id, 'scene': 'DISTRICT',
            'head': {'cid': '09031177210123456789', 'ctok': '', 'cver': '1.0', 'lang': '01', 'sid': '8888', 'syscode': '09'}
        }
        headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(100,120)}.0.0.0',
            'Content-Type': 'application/json'
        }
        try:
            r = self.session.post(url, json=payload, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f'  请求失败: {e}')
        return None
    
    def parse_attraction(self, item, city_name, province):
        try:
            card = item.get('card', {})
            if not card:
                return None
            
            # 解析价格
            price = card.get('price', 0)
            if card.get('isFree'):
                price = 0
            
            # 解析坐标
            coord = card.get('coordinate', {})
            
            return {
                'name': card.get('poiName', ''),
                'city': city_name,
                'province': province,
                'address': card.get('zoneName', '') or card.get('distanceStr', ''),
                'score': card.get('commentScore', 0),
                'comment_count': card.get('commentCount', 0),
                'price': price,
                'longitude': coord.get('longitude', 0),
                'latitude': coord.get('latitude', 0),
                'image_url': card.get('coverImageUrl', ''),
                'description': ', '.join(card.get('shortFeatures', [])),
                'level': card.get('sightLevelStr', ''),
                'poi_id': card.get('poiId', ''),
            }
        except Exception as e:
            print(f'  解析失败: {e}')
            return None
    
    def crawl_city(self, city):
        city_id = city['id']
        city_name = city['name']
        province = city['province']
        print(f'\n爬取: {province} - {city_name}')
        city_attractions = []
        
        for page in range(1, MAX_PAGES + 1):
            print(f'  第{page}页...', end=' ')
            data = self.get_attractions(city_id, page)
            
            if not data or 'attractionList' not in data:
                print('无数据')
                break
            
            items = data.get('attractionList', [])
            if not items:
                print('空')
                break
            
            count = 0
            for item in items:
                attr = self.parse_attraction(item, city_name, province)
                if attr and attr['name']:
                    city_attractions.append(attr)
                    count += 1
            
            print(f'{count}条')
            
            if not data.get('hasMore', False):
                break
            
            time.sleep(REQUEST_DELAY + random.uniform(0.5, 1))
        
        print(f'  {city_name}共{len(city_attractions)}个景点')
        return city_attractions
    
    def crawl_all(self):
        print('='*50)
        print('开始爬取携程景点数据')
        print('='*50)
        
        for city in CITIES:
            attractions = self.crawl_city(city)
            self.all_attractions.extend(attractions)
            time.sleep(REQUEST_DELAY)
        
        print('\n' + '='*50)
        print(f'爬取完成，共{len(self.all_attractions)}个景点')
        print('='*50)
        return self.all_attractions
    
    def save_to_json(self, filename='attractions.json'):
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.all_attractions, f, ensure_ascii=False, indent=2)
        print(f'数据已保存到: {filepath}')
        return filepath


if __name__ == '__main__':
    spider = CtripSpider()
    spider.crawl_all()
    spider.save_to_json()
