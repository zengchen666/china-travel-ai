# -*- coding: utf-8 -*-
"""
修复景区等级为nan的数据
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')

import django
django.setup()

from attractions.models import Attraction

# 统计
nan_count = Attraction.objects.filter(level='nan').count()
print(f"等级为nan的景点: {nan_count} 个")

# 将nan改为空字符串
updated = Attraction.objects.filter(level='nan').update(level='')
print(f"已修复: {updated} 个")

# 统计各等级分布
print("\n景区等级分布:")
levels = Attraction.objects.values_list('level', flat=True).distinct()
for level in levels:
    count = Attraction.objects.filter(level=level).count()
    display = level if level else '未评级'
    print(f"  {display}: {count} 个")
