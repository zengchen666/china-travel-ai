# -*- coding: utf-8 -*-
"""
数据质量修复（在 crawler/ 目录下运行：python tools/fix_city_mismatch.py）

针对携程接口混入的脏数据：
1. 删除「城市 · 活动名」形式的演出/票务条目（非景点）
2. 城市错位修正：地址明确指向另一个已知城市时，以地址为准

修复完成后请重建 RAG 索引：python manage.py rebuild_rag
"""
import os
import sys
import io
import json

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE, 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')

import django
django.setup()

from attractions.models import Attraction, City

REPORT = os.path.join(BASE, '.workbuddy', 'fix_city_report.json')


def main():
    report = {}

    # 1. 删除演出/活动类条目
    events = list(Attraction.objects.filter(name__contains=' · ').values('id', 'name'))
    Attraction.objects.filter(name__contains=' · ').delete()
    report['events_removed'] = len(events)
    report['events_sample'] = [e['name'] for e in events[:20]]

    # 2. 城市错位修正
    cities = {c.name: c for c in City.objects.select_related('province').all()}
    fixed = []
    for a in Attraction.objects.select_related('city').iterator():
        addr = (a.address or '').strip()
        if not addr or not a.city:
            continue
        for name in sorted(cities, key=len, reverse=True):
            if name != a.city.name and (addr.startswith(name) or (name + '市') in addr):
                fixed.append({'id': a.id, 'name': a.name,
                              'from': a.city.name, 'to': name})
                a.city = cities[name]
                a.save(update_fields=['city'])
                break
    report['city_fixed'] = len(fixed)
    report['city_fixed_items'] = fixed

    report['remaining_total'] = Attraction.objects.count()

    with io.open(REPORT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
