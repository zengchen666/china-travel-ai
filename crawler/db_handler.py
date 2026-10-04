# -*- coding: utf-8 -*-
"""
数据库操作模块
将清洗后的数据存入MySQL数据库
"""

import pandas as pd
import pymysql
import os
import sys

# 添加Django项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')

import django
django.setup()

from attractions.models import Province, City, Attraction
from config import DATA_DIR


def import_to_database(csv_file='attractions_cleaned.csv'):
    """将CSV数据导入数据库"""
    filepath = os.path.join(DATA_DIR, csv_file)
    
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        print("请先运行 cleaner.py 生成清洗后的数据")
        return
    
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    print(f"读取数据: {len(df)} 条")
    
    # 统计
    created_provinces = 0
    created_cities = 0
    created_attractions = 0
    updated_attractions = 0
    
    # 缓存已创建的省份和城市
    province_cache = {}
    city_cache = {}
    
    for _, row in df.iterrows():
        # 1. 创建或获取省份
        province_name = row['province']
        if province_name not in province_cache:
            province, created = Province.objects.get_or_create(name=province_name)
            province_cache[province_name] = province
            if created:
                created_provinces += 1
        else:
            province = province_cache[province_name]
        
        # 2. 创建或获取城市
        city_key = f"{province_name}_{row['city']}"
        if city_key not in city_cache:
            city, created = City.objects.get_or_create(
                name=row['city'],
                province=province
            )
            city_cache[city_key] = city
            if created:
                created_cities += 1
        else:
            city = city_cache[city_key]
        
        # 3. 创建或更新景点
        attraction, created = Attraction.objects.update_or_create(
            name=row['name'],
            city=city,
            defaults={
                'address': row.get('address', ''),
                'score': row.get('score', 0) or None,
                'comment_count': int(row.get('comment_count', 0)),
                'price': row.get('price', 0) or None,
                'longitude': row.get('longitude', 0) or None,
                'latitude': row.get('latitude', 0) or None,
                'image_url': row.get('image_url', ''),
                'description': row.get('description', ''),
                'level': row.get('level', ''),
            }
        )
        
        if created:
            created_attractions += 1
        else:
            updated_attractions += 1
    
    print("\n" + "=" * 50)
    print("数据导入完成")
    print("=" * 50)
    print(f"新增省份: {created_provinces}")
    print(f"新增城市: {created_cities}")
    print(f"新增景点: {created_attractions}")
    print(f"更新景点: {updated_attractions}")
    print(f"总计: {created_attractions + updated_attractions} 条")


def show_statistics():
    """显示数据库统计"""
    print("\n" + "=" * 50)
    print("数据库统计")
    print("=" * 50)
    print(f"省份数量: {Province.objects.count()}")
    print(f"城市数量: {City.objects.count()}")
    print(f"景点数量: {Attraction.objects.count()}")
    
    print("\n各省份景点数:")
    for province in Province.objects.all():
        count = Attraction.objects.filter(city__province=province).count()
        print(f"  {province.name}: {count}")


def main():
    import_to_database()
    show_statistics()


if __name__ == '__main__':
    main()
