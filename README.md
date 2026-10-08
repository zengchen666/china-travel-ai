# 基于 RAG 的旅游景点智能推荐系统

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![RAG](https://img.shields.io/badge/RAG-ChromaDB%20%2B%20TF--IDF-blueviolet)
![LLM](https://img.shields.io/badge/LLM-DeepSeek-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> 本科毕业设计项目 —《基于 RAG 的旅游景点智能推荐系统设计与实现》

系统以 **RAG（检索增强生成）** 为核心：先用 ChromaDB 向量检索 + jieba TF-IDF 关键词检索
从 1300+ 真实景点库中混合召回相关景点，再交由 DeepSeek 大模型生成逐日行程，
有效抑制大模型幻觉、保证推荐结果有事实依据。

整体技术栈为 **Django + MySQL + ECharts + 百度地图 + DeepSeek**：
爬取携程 15 个热门城市景点数据，经 Pandas 清洗入库，提供景点浏览、
数据可视化大屏、AI 智能行程规划与用户收藏的一站式服务。

---

## ✨ 核心功能

| 模块 | 功能 |
|------|------|
| 🕷️ 数据采集 | 携程景点爬虫（15 城 × 5 页分页抓取）、Pandas 清洗去重、ORM 批量入库、图片本地化与压缩去重 |
| 🌐 景点服务 | 首页热门推荐、列表筛选/排序/分页、详情页（地图定位 + 同城推荐）、全文搜索 |
| 📊 数据可视化 | 评分分布、票价区间、省份景点数、景区等级、评论 TOP10、省份均分对比 + 百度地图全国散点 |
| 🤖 AI 行程推荐 | **RAG 混合检索**（ChromaDB 向量 + jieba TF-IDF 加权融合）召回相关景点 → DeepSeek 生成逐日行程；支持自由文本偏好（如"喜欢历史古迹和美食"），城市选填，推荐不再局限于固定城市；正则回查景点经纬度并在地图标注，历史落库 |
| 👤 用户体系 | 注册/登录/个人中心、景点收藏（AJAX）、推荐历史 |
| 🔧 后台管理 | SimpleUI 定制的 Django Admin（景点/用户/收藏/菜单定制） |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        数据 Pipeline                          │
│  携程 API ──► spider.py ──► attractions.json (1400 条原始)   │
│                  │                                          │
│              cleaner.py (Pandas 去重/清洗)                   │
│                  ▼                                          │
│           attractions_cleaned.csv                           │
│                  │                                          │
│   db_handler.py (Django ORM)      download_images.py        │
│                  ▼                          ▼               │
│            MySQL travel_db      media/attractions/ (本地图床)│
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     Django Web 层 (travel_web)                │
│  attractions     景点三级模型 Province → City → Attraction   │
│  users           自定义 User / Favorite / TravelHistory      │
│  visualization   9 个 JSON API ──► ECharts + 百度地图大屏     │
│  ai_recommend    用户偏好 ──► RAG 混合检索 ──► DeepSeek       │
│                  ├─ ChromaDB 向量召回（本地 ONNX Embedding）  │
│                  ├─ jieba + TF-IDF 关键词召回（0.4/0.6 融合） │
│                  └─ 检索结果构造 Prompt ──► 行程 + 地图标注   │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ 技术栈

| 层次 | 技术 |
|------|------|
| 后端框架 | Django 4.2 / django-simpleui |
| 数据库 | MySQL 8.0（PyMySQL 驱动） |
| 数据处理 | Pandas / NumPy |
| 爬虫 | Requests（携程移动端 API，2s 限速） |
| 前端 | Bootstrap 5 / Font Awesome / jQuery（CDN） |
| 可视化 | ECharts 5.4 / 百度地图 JavaScript API |
| AI | DeepSeek API（deepseek-chat，3 次重试 + 90s 超时） |
| RAG 检索 | ChromaDB（向量召回）+ jieba / scikit-learn（TF-IDF 关键词召回）混合融合 |

## 📁 项目结构

```
china-travel-ai/
├── crawler/                     # 数据采集与处理（独立运行）
│   ├── config.py                # 爬取配置：15 城市、请求头、限速
│   ├── spider.py                # 携程 API 分页爬虫
│   ├── cleaner.py               # Pandas 数据清洗
│   ├── db_handler.py            # 清洗结果入库 MySQL
│   ├── download_images.py       # 景点图片本地化
│   ├── data/                    # 原始数据与清洗产物（不入库 git）
│   └── tools/                   # 一次性修复 / 调试 / 运维脚本
│       ├── optimize_images.py   # 图片 MD5 去重 + 压缩（3.6GB → 300MB）
│       ├── fix_images.py / fix_nan_images.py / fix_level.py
│       ├── add_missing_images.py / check_image.py
│       ├── test_api.py / test_api2.py / test_db.py / mock_data.py
│
├── travel_web/                  # Django 项目
│   ├── manage.py
│   ├── travel_web/              # settings（密钥全部走 .env）/ urls / wsgi
│   ├── attractions/             # 景点模块（模型 + 4 视图）
│   ├── users/                   # 用户模块（自定义 User / 收藏 / 历史）
│   ├── visualization/           # 可视化模块（dashboard + 9 个 JSON API）
│   ├── ai_recommend/            # AI 推荐模块（DeepSeek 调用）
│   ├── templates/               # 12 个模板（Bootstrap 5）
│   ├── media/attractions/       # 景点图片（不入库 git，脚本重新生成）
│   ├── .env                     # 环境变量（不入库 git）
│   └── .env.example             # 环境变量模板
│
├── requirements.txt
└── README.md
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- MySQL 8.0+

### 1. 克隆与依赖安装

```bash
git clone https://github.com/zengchen666/china-travel-ai.git
cd china-travel-ai
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 2. 初始化数据库

```sql
CREATE DATABASE travel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 配置环境变量

```bash
cd travel_web
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux
```

编辑 `.env` 填入数据库密码、DeepSeek API Key 与百度地图 AK（获取方式见文末）。

### 4. 数据库迁移与管理员

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. 数据 Pipeline（可选，重新生成数据与图片）

```bash
cd ..\crawler
python spider.py               # ① 爬取 15 城景点 → data/attractions.json
python cleaner.py              # ② 清洗 → data/attractions_cleaned.csv
python db_handler.py           # ③ 入库 MySQL
python download_images.py      # ④ 图片本地化
python tools\optimize_images.py # ⑤ 图片去重压缩（可选）
```

> `tools/` 下的脚本为一次性修复/调试工具，需在 `crawler/` 目录下运行
> （如 `python tools\fix_level.py`）。

### 6. 启动服务

```bash
cd ..\travel_web
python manage.py rebuild_rag     # 首次/数据更新后构建 RAG 检索索引（可选，首次请求也会自动构建）
python manage.py runserver
```

> RAG 索引默认存储在 `~/.cache/travel_rag_storage`（ChromaDB 对非 ASCII 路径兼容性差，
> 项目路径含中文时请勿改回项目目录；可用 `.env` 中 `RAG_STORAGE` 指定纯英文路径）。

| 入口 | 地址 |
|------|------|
| 前台首页 | http://127.0.0.1:8000/ |
| 数据可视化 | http://127.0.0.1:8000/visualization/ |
| AI 推荐 | http://127.0.0.1:8000/recommend/ |
| 后台管理 | http://127.0.0.1:8000/admin/ |

## 📊 数据规模

- 景点总数：**1300+**（清洗后；已剔除携程接口混入的 110 条演出/票务条目，并修正 52 条城市错位）
- 覆盖城市：15 个（北京/上海/广州/深圳/杭州/成都/西安/重庆/南京/苏州/武汉/厦门/青岛/长沙/三亚）
- 覆盖省份：12 个
- 本地图片：约 1300 张（经 MD5 去重 + 压缩，1200px / JPEG q80）

## 🧠 RAG 检索说明

| 特性 | 说明 |
|------|------|
| 混合召回 | ChromaDB 向量相似度（0.4）+ jieba TF-IDF 关键词得分（0.6），min-max 归一化后加权融合 |
| 中文优化 | 中文查询以关键词为主，故 TF-IDF 权重更高；ChromaDB 不可用时自动降级为纯 TF-IDF |
| 索引构建 | 惰性构建（首次请求）或 `python manage.py rebuild_rag` 手动重建 |
| 降级链 | 混合检索 → 纯 TF-IDF → 数据库评分 TOP15（三层兜底，推荐功能永可用） |

## 🔌 内部 API（visualization）

| 端点 | 说明 |
|------|------|
| `GET /visualization/api/score-distribution/` | 评分分布 |
| `GET /visualization/api/province-avg-score/` | 各省平均评分 |
| `GET /visualization/api/top-comments/` | 评论数 TOP10 |
| `GET /visualization/api/city-hot/` | 城市热门景点 |
| `GET /visualization/api/province-count/` | 各省景点数量 |
| `GET /visualization/api/price-distribution/` | 票价区间分布 |
| `GET /visualization/api/level-distribution/` | 景区等级分布 |
| `GET /visualization/api/map-data/` | 全国景点经纬度 |
| `GET /visualization/api/stats/` | 综合统计 |
| `POST /recommend/api/recommend/` | AI 行程推荐（JSON） |

## 🔑 API 密钥获取

- **DeepSeek API**：https://platform.deepseek.com/ → 注册 → 创建 API Key
- **百度地图 AK**：https://lbsyun.baidu.com/ → 创建应用 → 启用 JavaScript API

## ⚠️ 注意事项

1. 爬虫请遵守目标网站 robots 协议，脚本已内置 2s 请求限速
2. `.env`、景点图片、爬虫原始数据均已在 `.gitignore` 中，不会提交
3. 生产部署前请将 `.env` 中 `DEBUG=False`、配置 `ALLOWED_HOSTS`，并更换 `SECRET_KEY`
4. 模板中的 `<img>` 均带 `onerror` 兜底图，本地图片缺失不影响页面渲染

## 👨‍💻 作者

**曾晨** — 本科毕业设计 / 个人学习项目

## 📄 许可证

MIT License，仅供学习交流使用。爬取数据版权归原平台所有，请勿用于商业用途。
