# -*- coding: utf-8 -*-
"""
修复图片URL为nan的景点，从CSV重新获取正确的图片URL并下载
"""
import os
import sys
import pandas as pd
import requests
import hashlib
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')

import django
django.setup()

from attractions.models import Attraction

IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'travel_web', 'media', 'attractions')

def fix_nan_images():
    # 读取CSV获取原始图片URL
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'attractions_cleaned.csv')
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # 创建名称到图片URL的映射
    name_to_img = {}
    for _, row in df.iterrows():
        if pd.notna(row.get('image_url')) and str(row['image_url']).startswith('http'):
            name_to_img[row['name']] = row['image_url']
    
    print(f"CSV中有效图片: {len(name_to_img)} 个")
    
    # 找出需要修复的景点（图片URL为nan或不是本地路径）
    to_fix = Attraction.objects.filter(image_url='nan') | Attraction.objects.filter(image_url__startswith='http')
    print(f"需要修复的景点: {to_fix.count()} 个\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.ctrip.com/',
    }
    
    fixed = 0
    for attr in to_fix:
        # 从CSV获取图片URL
        img_url = name_to_img.get(attr.name)
        if not img_url:
            print(f"跳过 {attr.name} - CSV中无图片")
            continue
        
        # 生成文件名
        filename = f"{attr.id}_{hashlib.md5(attr.name.encode()).hexdigest()[:8]}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # 如果本地已存在，直接更新数据库
        if os.path.exists(filepath):
            attr.image_url = f'/media/attractions/{filename}'
            attr.save(update_fields=['image_url'])
            print(f"已存在 {attr.name}")
            fixed += 1
            continue
        
        # 下载图片
        try:
            resp = requests.get(img_url, headers=headers, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 1000:
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                attr.image_url = f'/media/attractions/{filename}'
                attr.save(update_fields=['image_url'])
                print(f"下载成功 {attr.name}")
                fixed += 1
            else:
                print(f"下载失败 {attr.name}")
        except Exception as e:
            print(f"错误 {attr.name}: {str(e)[:30]}")
        
        time.sleep(0.3)
    
    print(f"\n修复完成: {fixed} 个")

if __name__ == '__main__':
    fix_nan_images()
