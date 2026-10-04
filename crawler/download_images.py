# -*- coding: utf-8 -*-
"""
下载景点图片到本地
"""
import os
import sys
import requests
import time
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')

import django
django.setup()

from attractions.models import Attraction

# 图片保存目录
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'travel_web', 'media', 'attractions')

def download_images():
    # 创建目录
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        print(f"创建目录: {IMAGES_DIR}")
    
    # 获取所有有图片URL的景点
    attractions = Attraction.objects.exclude(image_url='').exclude(image_url__isnull=True)
    total = attractions.count()
    print(f"共有 {total} 个景点需要下载图片\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.ctrip.com/',
    }
    
    success = 0
    failed = 0
    skipped = 0
    
    for i, attr in enumerate(attractions, 1):
        # 生成文件名
        ext = '.jpg'
        if '.png' in attr.image_url.lower():
            ext = '.png'
        filename = f"{attr.id}_{hashlib.md5(attr.name.encode()).hexdigest()[:8]}{ext}"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # 如果已存在则跳过
        if os.path.exists(filepath):
            skipped += 1
            print(f"[{i}/{total}] 跳过 {attr.name} (已存在)")
            continue
        
        try:
            # 下载图片
            resp = requests.get(attr.image_url, headers=headers, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 1000:
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                
                # 更新数据库中的图片路径
                attr.image_url = f'/media/attractions/{filename}'
                attr.save(update_fields=['image_url'])
                
                success += 1
                print(f"[{i}/{total}] ✓ {attr.name}")
            else:
                failed += 1
                print(f"[{i}/{total}] ✗ {attr.name} (下载失败)")
        except Exception as e:
            failed += 1
            print(f"[{i}/{total}] ✗ {attr.name} ({str(e)[:30]})")
        
        # 避免请求过快
        if i % 10 == 0:
            time.sleep(0.5)
    
    print(f"\n{'='*50}")
    print(f"下载完成!")
    print(f"成功: {success}")
    print(f"失败: {failed}")
    print(f"跳过: {skipped}")
    print(f"{'='*50}")

if __name__ == '__main__':
    download_images()
