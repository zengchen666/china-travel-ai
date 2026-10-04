import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')
django.setup()

from attractions.models import Attraction, Province, City

print(f"景点数量: {Attraction.objects.count()}")
print(f"省份数量: {Province.objects.count()}")
print(f"城市数量: {City.objects.count()}")

# 测试有经纬度的景点
with_coords = Attraction.objects.exclude(longitude__isnull=True).exclude(latitude__isnull=True).count()
print(f"有经纬度的景点: {with_coords}")
