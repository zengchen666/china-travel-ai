# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')

import django
django.setup()

from attractions.models import Attraction

# 检查兵马俑
attrs = Attraction.objects.filter(name__icontains='兵马俑')
for a in attrs:
    print(f"ID: {a.id}, 名称: {a.name}, 图片: {a.image_url}")

# 统计没有有效图片的景点
no_img = Attraction.objects.filter(image_url__in=['', 'nan']).count()
has_nan = Attraction.objects.filter(image_url='nan').count()
print(f"\n空图片: {no_img}, nan图片: {has_nan}")
