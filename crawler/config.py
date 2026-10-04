# 爬虫配置

# 要爬取的城市列表（携程城市ID和名称）
CITIES = [
    {'id': 1, 'name': '北京', 'province': '北京'},
    {'id': 2, 'name': '上海', 'province': '上海'},
    {'id': 17, 'name': '杭州', 'province': '浙江'},
    {'id': 28, 'name': '成都', 'province': '四川'},
    {'id': 32, 'name': '西安', 'province': '陕西'},
    {'id': 7, 'name': '广州', 'province': '广东'},
    {'id': 9, 'name': '深圳', 'province': '广东'},
    {'id': 21, 'name': '南京', 'province': '江苏'},
    {'id': 4, 'name': '重庆', 'province': '重庆'},
    {'id': 125, 'name': '三亚', 'province': '海南'},
    {'id': 20, 'name': '苏州', 'province': '江苏'},
    {'id': 148, 'name': '厦门', 'province': '福建'},
    {'id': 39, 'name': '昆明', 'province': '云南'},
    {'id': 38, 'name': '丽江', 'province': '云南'},
    {'id': 158, 'name': '桂林', 'province': '广西'},
]

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://you.ctrip.com/',
}

# 请求间隔（秒）
REQUEST_DELAY = 2

# 每个城市爬取的页数
MAX_PAGES = 5

# 数据保存路径
DATA_DIR = 'data'
