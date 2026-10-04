# -*- coding: utf-8 -*-
"""
修复景点图片URL
"""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')

import django
django.setup()

from attractions.models import Attraction
def fix_images():
    # 读取CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'attractions_cleaned.csv')
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # 检查数据库中图片情况
    total = Attraction.objects.count()
    with_image = Attraction.objects.exclude(image_url='').exclude(image_url__isnull=True).count()
    print(f"数据库景点总数: {total}")
    print(f"有图片的景点: {with_image}")
    print(f"无图片的景点: {total - with_image}")
    
    # 更新图片URL
    updated = 0
    for _, row in df.iterrows():
        if pd.notna(row.get('image_url')) and row['image_url']:
            result = Attraction.objects.filter(name=row['name']).update(image_url=row['image_url'])
            if result:
                updated += result
    
    print(f"\n更新了 {updated} 个景点的图片")
    
    # 再次检查
    with_image = Attraction.objects.exclude(image_url='').exclude(image_url__isnull=True).count()
    print(f"现在有图片的景点: {with_image}")

if __name__ == '__main__':
    fix_images()
