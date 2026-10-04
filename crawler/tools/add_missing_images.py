# -*- coding: utf-8 -*-
"""
为缺失图片的热门景点手动添加图片
"""
import os
import sys
import requests
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'travel_web'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')

import django
django.setup()

from attractions.models import Attraction

IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'travel_web', 'media', 'attractions')

# 使用unsplash的免费图片作为替代（按景点类型选择相关图片）
BACKUP_IMAGES = {
    '西湖': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
    '迪士尼乐园': 'https://images.unsplash.com/photo-1597466599360-3b9775841aec?w=800',
    '秦始皇兵马俑': 'https://images.unsplash.com/photo-1591122947157-26bad3a117d2?w=800',
    '洪崖洞': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
    '长隆野生动物世界': 'https://images.unsplash.com/photo-1474511320723-9a56873571b7?w=800',
    '大熊猫繁育研究基地': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800',
    '漓江': 'https://images.unsplash.com/photo-1537531383496-f4749b8032cf?w=800',
    '亚龙湾': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800',
    '欢乐谷': 'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?w=800',
    '蜈支洲岛': 'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=800',
    '宽窄巷子': 'https://images.unsplash.com/photo-1470004914212-05527e49370b?w=800',
    '灵隐寺': 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800',
    '中山陵': 'https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=800',
    '广州塔': 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=800',
    '都江堰': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
    '拙政园': 'https://images.unsplash.com/photo-1513415564515-763d91423bdd?w=800',
    '千岛湖': 'https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=800',
    '世界之窗': 'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?w=800',
    '周庄古镇': 'https://images.unsplash.com/photo-1528164344705-47542687000d?w=800',
    '天涯海角': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800',
    '石林': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800',
    '象鼻山': 'https://images.unsplash.com/photo-1537531383496-f4749b8032cf?w=800',
    '滇池': 'https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=800',
}

def add_missing_images():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    for name, img_url in BACKUP_IMAGES.items():
        attr = Attraction.objects.filter(name=name).first()
        if not attr:
            print(f"未找到: {name}")
            continue
        
        # 检查是否已有本地图片
        if attr.image_url and attr.image_url.startswith('/media/'):
            print(f"已有图片: {name}")
            continue
        
        # 下载图片
        filename = f"{attr.id}_{hashlib.md5(name.encode()).hexdigest()[:8]}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        try:
            resp = requests.get(img_url, headers=headers, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 1000:
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                attr.image_url = f'/media/attractions/{filename}'
                attr.save(update_fields=['image_url'])
                print(f"成功: {name}")
            else:
                print(f"下载失败: {name} - {resp.status_code}")
        except Exception as e:
            print(f"错误: {name} - {str(e)[:50]}")

if __name__ == '__main__':
    add_missing_images()
