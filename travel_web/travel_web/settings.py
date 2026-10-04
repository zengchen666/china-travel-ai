"""
Django settings for travel_web project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-zx*unjoz&2sxn&1teck0m-3c-fzy@c%ew6h-hc5b-^q-*bpguv')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# 应用配置
INSTALLED_APPS = [
    'simpleui',  # SimpleUI后台美化，必须放在admin之前
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 自定义应用
    'users',
    'attractions',
    'visualization',
    'ai_recommend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'travel_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'travel_web.wsgi.application'

# 数据库配置 - MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travel_db',
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# PyMySQL作为MySQL驱动
import pymysql
pymysql.install_as_MySQLdb()

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 中文配置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 媒体文件
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SimpleUI配置
SIMPLEUI_HOME_INFO = False  # 隐藏首页服务器信息
SIMPLEUI_ANALYSIS = False   # 关闭使用分析
SIMPLEUI_LOGO = None        # 使用默认Logo

# SimpleUI主题配置
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'  # 主题样式

# 首页配置
SIMPLEUI_HOME_PAGE = '/visualization/'  # 首页跳转到数据可视化
SIMPLEUI_HOME_TITLE = '数据分析'
SIMPLEUI_HOME_ICON = 'fa fa-chart-bar'

# 自定义菜单
SIMPLEUI_CONFIG = {
    'system_keep': False,  # 关闭系统菜单
    'menu_display': ['景点管理', '用户管理', '系统管理'],
    'dynamic': True,  # 动态菜单
    'menus': [
        {
            'name': '景点管理',
            'icon': 'fa fa-mountain',
            'models': [
                {'name': '景点列表', 'icon': 'fa fa-list', 'url': '/admin/attractions/attraction/'},
                {'name': '省份管理', 'icon': 'fa fa-map', 'url': '/admin/attractions/province/'},
                {'name': '城市管理', 'icon': 'fa fa-city', 'url': '/admin/attractions/city/'},
            ]
        },
        {
            'name': '用户管理',
            'icon': 'fa fa-users',
            'models': [
                {'name': '用户列表', 'icon': 'fa fa-user', 'url': '/admin/users/user/'},
                {'name': '收藏记录', 'icon': 'fa fa-heart', 'url': '/admin/users/favorite/'},
            ]
        },
        {
            'name': '系统管理',
            'icon': 'fa fa-cog',
            'models': [
                {'name': '数据分析', 'icon': 'fa fa-chart-bar', 'url': '/visualization/', 'newTab': True},
                {'name': '前台首页', 'icon': 'fa fa-home', 'url': '/', 'newTab': True},
            ]
        },
    ]
}

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'

# 百度地图API配置
BAIDU_MAP_AK = os.getenv('BAIDU_MAP_AK', '')


# 自定义用户模型
AUTH_USER_MODEL = 'users.User'

# Session设置：保持登录1天
SESSION_COOKIE_AGE = 86400
