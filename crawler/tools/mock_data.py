# -*- coding: utf-8 -*-
"""生成模拟景点数据用于测试"""
import json
import os
import random

MOCK_DATA = [
    # 北京
    {'name': '故宫博物院', 'city': '北京', 'province': '北京', 'address': '北京市东城区景山前街4号', 'score': 4.8, 'comment_count': 125680, 'price': 60, 'longitude': 116.397026, 'latitude': 39.918058, 'level': '5A', 'image_url': '', 'description': '中国明清两代的皇家宫殿'},
    {'name': '天安门广场', 'city': '北京', 'province': '北京', 'address': '北京市东城区东长安街', 'score': 4.7, 'comment_count': 98520, 'price': 0, 'longitude': 116.397755, 'latitude': 39.903179, 'level': '', 'image_url': '', 'description': '世界上最大的城市广场'},
    {'name': '颐和园', 'city': '北京', 'province': '北京', 'address': '北京市海淀区新建宫门路19号', 'score': 4.7, 'comment_count': 86350, 'price': 30, 'longitude': 116.275045, 'latitude': 39.999908, 'level': '5A', 'image_url': '', 'description': '中国清朝时期皇家园林'},
    {'name': '八达岭长城', 'city': '北京', 'province': '北京', 'address': '北京市延庆区G6京藏高速58号出口', 'score': 4.6, 'comment_count': 75230, 'price': 40, 'longitude': 116.024067, 'latitude': 40.359947, 'level': '5A', 'image_url': '', 'description': '万里长城的精华段'},
    {'name': '天坛公园', 'city': '北京', 'province': '北京', 'address': '北京市东城区天坛东里甲1号', 'score': 4.6, 'comment_count': 52180, 'price': 15, 'longitude': 116.410886, 'latitude': 39.881954, 'level': '5A', 'image_url': '', 'description': '明清两代帝王祭祀皇天的场所'},
]

MOCK_DATA += [
    # 上海
    {'name': '东方明珠', 'city': '上海', 'province': '上海', 'address': '上海市浦东新区世纪大道1号', 'score': 4.5, 'comment_count': 89650, 'price': 199, 'longitude': 121.499718, 'latitude': 31.239703, 'level': '5A', 'image_url': '', 'description': '上海标志性建筑'},
    {'name': '外滩', 'city': '上海', 'province': '上海', 'address': '上海市黄浦区中山东一路', 'score': 4.7, 'comment_count': 112350, 'price': 0, 'longitude': 121.490714, 'latitude': 31.240018, 'level': '', 'image_url': '', 'description': '上海的标志性景观'},
    {'name': '迪士尼乐园', 'city': '上海', 'province': '上海', 'address': '上海市浦东新区川沙镇', 'score': 4.8, 'comment_count': 156890, 'price': 475, 'longitude': 121.668733, 'latitude': 31.143378, 'level': '', 'image_url': '', 'description': '中国内地首座迪士尼主题乐园'},
    {'name': '豫园', 'city': '上海', 'province': '上海', 'address': '上海市黄浦区福佑路168号', 'score': 4.4, 'comment_count': 45680, 'price': 40, 'longitude': 121.492499, 'latitude': 31.227621, 'level': '4A', 'image_url': '', 'description': '江南古典园林'},
    # 杭州
    {'name': '西湖', 'city': '杭州', 'province': '浙江', 'address': '杭州市西湖区龙井路1号', 'score': 4.9, 'comment_count': 186520, 'price': 0, 'longitude': 120.148732, 'latitude': 30.242865, 'level': '5A', 'image_url': '', 'description': '中国十大风景名胜之一'},
    {'name': '灵隐寺', 'city': '杭州', 'province': '浙江', 'address': '杭州市西湖区灵隐路法云弄1号', 'score': 4.6, 'comment_count': 68950, 'price': 75, 'longitude': 120.101258, 'latitude': 30.240128, 'level': '', 'image_url': '', 'description': '中国佛教禅宗十大古刹之一'},
    {'name': '千岛湖', 'city': '杭州', 'province': '浙江', 'address': '杭州市淳安县千岛湖镇', 'score': 4.5, 'comment_count': 52360, 'price': 150, 'longitude': 118.957788, 'latitude': 29.604455, 'level': '5A', 'image_url': '', 'description': '天下第一秀水'},
]

MOCK_DATA += [
    # 成都
    {'name': '大熊猫繁育研究基地', 'city': '成都', 'province': '四川', 'address': '成都市成华区熊猫大道1375号', 'score': 4.7, 'comment_count': 98650, 'price': 55, 'longitude': 104.145868, 'latitude': 30.732758, 'level': '4A', 'image_url': '', 'description': '大熊猫保护研究中心'},
    {'name': '宽窄巷子', 'city': '成都', 'province': '四川', 'address': '成都市青羊区金河路口宽窄巷子', 'score': 4.4, 'comment_count': 75230, 'price': 0, 'longitude': 104.055698, 'latitude': 30.669648, 'level': '4A', 'image_url': '', 'description': '成都历史文化街区'},
    {'name': '都江堰', 'city': '成都', 'province': '四川', 'address': '成都市都江堰市公园路', 'score': 4.6, 'comment_count': 56890, 'price': 80, 'longitude': 103.610729, 'latitude': 31.003956, 'level': '5A', 'image_url': '', 'description': '世界文化遗产'},
    # 西安
    {'name': '秦始皇兵马俑', 'city': '西安', 'province': '陕西', 'address': '西安市临潼区秦陵北路', 'score': 4.8, 'comment_count': 135680, 'price': 120, 'longitude': 109.278348, 'latitude': 34.384431, 'level': '5A', 'image_url': '', 'description': '世界第八大奇迹'},
    {'name': '华清宫', 'city': '西安', 'province': '陕西', 'address': '西安市临潼区华清路38号', 'score': 4.5, 'comment_count': 48960, 'price': 120, 'longitude': 109.214073, 'latitude': 34.366447, 'level': '5A', 'image_url': '', 'description': '唐代皇家温泉宫殿'},
    {'name': '大雁塔', 'city': '西安', 'province': '陕西', 'address': '西安市雁塔区慈恩路1号', 'score': 4.5, 'comment_count': 62350, 'price': 40, 'longitude': 108.959118, 'latitude': 34.218384, 'level': '5A', 'image_url': '', 'description': '唐代著名佛塔'},
]

MOCK_DATA += [
    # 广州
    {'name': '广州塔', 'city': '广州', 'province': '广东', 'address': '广州市海珠区阅江西路222号', 'score': 4.5, 'comment_count': 68520, 'price': 150, 'longitude': 113.324553, 'latitude': 23.106414, 'level': '', 'image_url': '', 'description': '广州新地标'},
    {'name': '长隆野生动物世界', 'city': '广州', 'province': '广东', 'address': '广州市番禺区大石街道', 'score': 4.7, 'comment_count': 125630, 'price': 300, 'longitude': 113.329556, 'latitude': 22.994713, 'level': '5A', 'image_url': '', 'description': '亚洲最大野生动物园'},
    # 深圳
    {'name': '世界之窗', 'city': '深圳', 'province': '广东', 'address': '深圳市南山区深南大道9037号', 'score': 4.4, 'comment_count': 52360, 'price': 220, 'longitude': 113.973129, 'latitude': 22.534756, 'level': '5A', 'image_url': '', 'description': '世界著名景观微缩景区'},
    {'name': '欢乐谷', 'city': '深圳', 'province': '广东', 'address': '深圳市南山区侨城西街1号', 'score': 4.5, 'comment_count': 78960, 'price': 230, 'longitude': 113.981346, 'latitude': 22.541623, 'level': '4A', 'image_url': '', 'description': '大型主题乐园'},
    # 三亚
    {'name': '亚龙湾', 'city': '三亚', 'province': '海南', 'address': '三亚市吉阳区亚龙湾国家旅游度假区', 'score': 4.7, 'comment_count': 86520, 'price': 0, 'longitude': 109.641918, 'latitude': 18.191067, 'level': '4A', 'image_url': '', 'description': '天下第一湾'},
    {'name': '蜈支洲岛', 'city': '三亚', 'province': '海南', 'address': '三亚市海棠区蜈支洲岛', 'score': 4.6, 'comment_count': 75630, 'price': 144, 'longitude': 109.762775, 'latitude': 18.312632, 'level': '5A', 'image_url': '', 'description': '中国的马尔代夫'},
    {'name': '天涯海角', 'city': '三亚', 'province': '海南', 'address': '三亚市天涯区天涯镇', 'score': 4.3, 'comment_count': 45890, 'price': 81, 'longitude': 109.204544, 'latitude': 18.241755, 'level': '4A', 'image_url': '', 'description': '海南标志性景点'},
]

MOCK_DATA += [
    # 南京
    {'name': '中山陵', 'city': '南京', 'province': '江苏', 'address': '南京市玄武区石象路7号', 'score': 4.7, 'comment_count': 68950, 'price': 0, 'longitude': 118.856468, 'latitude': 32.056346, 'level': '5A', 'image_url': '', 'description': '孙中山先生陵墓'},
    {'name': '夫子庙', 'city': '南京', 'province': '江苏', 'address': '南京市秦淮区秦淮河畔', 'score': 4.4, 'comment_count': 52360, 'price': 0, 'longitude': 118.787735, 'latitude': 32.022133, 'level': '5A', 'image_url': '', 'description': '南京历史文化街区'},
    # 苏州
    {'name': '拙政园', 'city': '苏州', 'province': '江苏', 'address': '苏州市姑苏区东北街178号', 'score': 4.6, 'comment_count': 56890, 'price': 80, 'longitude': 120.628319, 'latitude': 31.325808, 'level': '5A', 'image_url': '', 'description': '中国四大名园之一'},
    {'name': '周庄古镇', 'city': '苏州', 'province': '江苏', 'address': '苏州市昆山市周庄镇', 'score': 4.5, 'comment_count': 48650, 'price': 100, 'longitude': 120.854994, 'latitude': 31.114249, 'level': '5A', 'image_url': '', 'description': '中国第一水乡'},
    # 厦门
    {'name': '鼓浪屿', 'city': '厦门', 'province': '福建', 'address': '厦门市思明区鼓浪屿', 'score': 4.6, 'comment_count': 98650, 'price': 0, 'longitude': 118.066173, 'latitude': 24.448512, 'level': '5A', 'image_url': '', 'description': '世界文化遗产'},
    {'name': '南普陀寺', 'city': '厦门', 'province': '福建', 'address': '厦门市思明区思明南路515号', 'score': 4.5, 'comment_count': 35680, 'price': 0, 'longitude': 118.093414, 'latitude': 24.441063, 'level': '4A', 'image_url': '', 'description': '闽南佛教圣地'},
    # 昆明
    {'name': '石林', 'city': '昆明', 'province': '云南', 'address': '昆明市石林彝族自治县', 'score': 4.5, 'comment_count': 45890, 'price': 130, 'longitude': 103.327522, 'latitude': 24.817444, 'level': '5A', 'image_url': '', 'description': '世界自然遗产'},
    {'name': '滇池', 'city': '昆明', 'province': '云南', 'address': '昆明市西山区滇池路', 'score': 4.4, 'comment_count': 32560, 'price': 0, 'longitude': 102.656738, 'latitude': 24.833333, 'level': '', 'image_url': '', 'description': '高原明珠'},
]

MOCK_DATA += [
    # 丽江
    {'name': '丽江古城', 'city': '丽江', 'province': '云南', 'address': '丽江市古城区', 'score': 4.6, 'comment_count': 125680, 'price': 50, 'longitude': 100.233026, 'latitude': 26.872108, 'level': '5A', 'image_url': '', 'description': '世界文化遗产'},
    {'name': '玉龙雪山', 'city': '丽江', 'province': '云南', 'address': '丽江市玉龙纳西族自治县', 'score': 4.7, 'comment_count': 86520, 'price': 180, 'longitude': 100.186947, 'latitude': 27.118763, 'level': '5A', 'image_url': '', 'description': '纳西族神山'},
    # 桂林
    {'name': '漓江', 'city': '桂林', 'province': '广西', 'address': '桂林市灵川县', 'score': 4.8, 'comment_count': 98650, 'price': 210, 'longitude': 110.291195, 'latitude': 25.273566, 'level': '5A', 'image_url': '', 'description': '桂林山水甲天下'},
    {'name': '阳朔西街', 'city': '桂林', 'province': '广西', 'address': '桂林市阳朔县', 'score': 4.4, 'comment_count': 56890, 'price': 0, 'longitude': 110.496593, 'latitude': 24.778963, 'level': '', 'image_url': '', 'description': '洋人街'},
    {'name': '象鼻山', 'city': '桂林', 'province': '广西', 'address': '桂林市象山区滨江路', 'score': 4.3, 'comment_count': 42560, 'price': 70, 'longitude': 110.296389, 'latitude': 25.262222, 'level': '5A', 'image_url': '', 'description': '桂林城徽'},
    # 重庆
    {'name': '洪崖洞', 'city': '重庆', 'province': '重庆', 'address': '重庆市渝中区嘉陵江滨江路88号', 'score': 4.5, 'comment_count': 135680, 'price': 0, 'longitude': 106.578396, 'latitude': 29.562176, 'level': '4A', 'image_url': '', 'description': '重庆网红打卡地'},
    {'name': '武隆天生三桥', 'city': '重庆', 'province': '重庆', 'address': '重庆市武隆区仙女山镇', 'score': 4.7, 'comment_count': 68950, 'price': 125, 'longitude': 107.751389, 'latitude': 29.328611, 'level': '5A', 'image_url': '', 'description': '世界自然遗产'},
    {'name': '磁器口古镇', 'city': '重庆', 'province': '重庆', 'address': '重庆市沙坪坝区磁器口', 'score': 4.3, 'comment_count': 52360, 'price': 0, 'longitude': 106.448611, 'latitude': 29.579722, 'level': '4A', 'image_url': '', 'description': '重庆古镇'},
]


def generate_mock_data():
    """生成模拟数据并保存"""
    os.makedirs('data', exist_ok=True)
    # 注意：写入独立文件名，避免覆盖 spider.py 爬取的真实数据
    with open('data/attractions_mock.json', 'w', encoding='utf-8') as f:
        json.dump(MOCK_DATA, f, ensure_ascii=False, indent=2)
    print(f'已生成 {len(MOCK_DATA)} 条模拟数据')
    print('保存到: data/attractions.json')


if __name__ == '__main__':
    generate_mock_data()
