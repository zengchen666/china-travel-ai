# -*- coding: utf-8 -*-
"""
景点 RAG 检索模块

把景点库（名称 + 城市 + 省份 + 等级 + 地址 + 描述）建成检索索引，
根据用户的自由文本偏好召回最相关的景点，再交给 DeepSeek 生成行程，
使推荐不再局限于「某城市评分 TOP15」。

双后端策略（自动选择）：
1. ChromaDB 向量检索（本地持久化，默认 ONNX Embedding，离线可用）
2. jieba 分词 + TF-IDF 余弦相似度（ChromaDB 初始化失败时自动降级）

索引重建：
    python manage.py rebuild_rag
"""
import logging
import os

logger = logging.getLogger(__name__)

# ChromaDB rust 引擎对非 ASCII 存储路径兼容性差（索引重载会失败），
# 默认放到用户缓存目录（纯 ASCII 路径），可用环境变量 RAG_STORAGE 覆盖
RAG_STORAGE = os.getenv('RAG_STORAGE') or os.path.join(
    os.path.expanduser('~'), '.cache', 'travel_rag_storage'
)
COLLECTION_NAME = 'attractions'
INDEX_VERSION = 'v1'

_retriever = None


def _queryset():
    from attractions.models import Attraction
    return (
        Attraction.objects.select_related('city__province')
        .exclude(name='')
        .order_by('id')
    )


def _doc_text(a):
    """拼接检索文档：名称权重最高，放在最前并重复一次"""
    city = a.city.name if a.city else ''
    province = a.city.province.name if a.city and a.city.province else ''
    parts = [
        a.name, a.name,
        city, province,
        a.level or '',
        a.address or '',
        (a.description or '')[:200],
    ]
    return ' '.join(p for p in parts if p).strip()


def _ordered_attractions(ids):
    """按召回顺序取回 Attraction 对象"""
    from attractions.models import Attraction
    objs = {a.id: a for a in Attraction.objects.select_related('city').filter(id__in=ids)}
    return [objs[i] for i in ids if i in objs]


class ChromaRetriever:
    """ChromaDB 向量检索后端"""

    name = 'chromadb'

    def __init__(self):
        import chromadb
        os.makedirs(RAG_STORAGE, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=RAG_STORAGE,
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
        self.col = self.client.get_or_create_collection(
            COLLECTION_NAME, metadata={'hnsw:space': 'cosine'}
        )

    def ensure_index(self, qs):
        expected = qs.count()
        if self.col.count() == expected and expected > 0:
            return
        self.rebuild(qs)

    def rebuild(self, qs):
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self.col = self.client.get_or_create_collection(
            COLLECTION_NAME, metadata={'hnsw:space': 'cosine'}
        )
        batch = 500
        buf_ids, buf_docs, buf_meta = [], [], []
        for a in qs.iterator():
            buf_ids.append(str(a.id))
            buf_docs.append(_doc_text(a))
            buf_meta.append({'city': a.city.name if a.city else '', 'name': a.name})
            if len(buf_ids) >= batch:
                self.col.add(ids=buf_ids, documents=buf_docs, metadatas=buf_meta)
                buf_ids, buf_docs, buf_meta = [], [], []
        if buf_ids:
            self.col.add(ids=buf_ids, documents=buf_docs, metadatas=buf_meta)
        logger.info('ChromaDB 索引重建完成：%s 条', self.col.count())

    def search(self, query, city=None, top_k=15):
        """返回 [(attraction_id, 相似度)]，相似度 = 1 - 余弦距离"""
        kwargs = {'query_texts': [query], 'n_results': top_k, 'include': ['distances']}
        if city:
            kwargs['where'] = {'city': city}
        res = self.col.query(**kwargs)
        return [
            (int(i), 1.0 - float(d))
            for i, d in zip(res['ids'][0], res['distances'][0])
        ]

    def retrieve(self, query, city=None, top_k=15):
        ids = [i for i, _ in self.search(query, city, top_k)]
        return _ordered_attractions(ids)


class TfidfRetriever:
    """jieba + TF-IDF 降级后端（纯离线、中文效果好）"""

    name = 'tfidf'

    def __init__(self):
        self.matrix = None
        self.vectorizer = None
        self.ids = []
        self.cities = []

    def ensure_index(self, qs):
        import jieba
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.ids, self.cities, docs = [], [], []
        for a in qs.iterator():
            self.ids.append(a.id)
            self.cities.append(a.city.name if a.city else '')
            docs.append(_doc_text(a))
        self.vectorizer = TfidfVectorizer(tokenizer=jieba.lcut, token_pattern=None)
        self.matrix = self.vectorizer.fit_transform(docs)
        logger.info('TF-IDF 索引构建完成：%s 条', len(self.ids))

    def search(self, query, city=None, top_k=15):
        """返回 [(attraction_id, 余弦相似度)]"""
        import jieba
        from sklearn.metrics.pairwise import cosine_similarity

        q = self.vectorizer.transform([' '.join(jieba.lcut(query))])
        sims = cosine_similarity(q, self.matrix)[0]
        ranked = sims.argsort()[::-1]
        picked = []
        for idx in ranked:
            if city and self.cities[idx] != city:
                continue
            picked.append((self.ids[idx], float(sims[idx])))
            if len(picked) >= top_k:
                break
        return picked

    def retrieve(self, query, city=None, top_k=15):
        ids = [i for i, _ in self.search(query, city, top_k)]
        return _ordered_attractions(ids)


class HybridRetriever:
    """混合检索：ChromaDB 向量相似度 + jieba TF-IDF 关键词得分加权融合

    中文景点查询以关键词为主，故 TF-IDF 权重高于向量（0.6 / 0.4）。
    """

    name = 'hybrid(chromadb+tfidf)'
    VECTOR_WEIGHT = 0.4
    KEYWORD_WEIGHT = 0.6

    def __init__(self, chroma, tfidf):
        self.chroma = chroma
        self.tfidf = tfidf

    @staticmethod
    def _norm(pairs):
        if not pairs:
            return {}
        values = [s for _, s in pairs]
        lo, hi = min(values), max(values)
        span = hi - lo or 1.0
        return {i: (s - lo) / span for i, s in pairs}

    def retrieve(self, query, city=None, top_k=15):
        vec = self._norm(self.chroma.search(query, city, top_k * 3))
        kw = self._norm(self.tfidf.search(query, city, top_k * 3))
        fused = [
            (i, self.VECTOR_WEIGHT * vec.get(i, 0.0) + self.KEYWORD_WEIGHT * kw.get(i, 0.0))
            for i in set(vec) | set(kw)
        ]
        fused.sort(key=lambda x: x[1], reverse=True)
        return _ordered_attractions([i for i, _ in fused[:top_k]])


def get_retriever():
    """获取检索器单例：优先「向量 + 关键词」混合检索，ChromaDB 不可用时降级纯 TF-IDF"""
    global _retriever
    if _retriever is None:
        qs = _queryset()
        tfidf = TfidfRetriever()
        tfidf.ensure_index(qs)
        try:
            chroma = ChromaRetriever()
            chroma.ensure_index(qs)  # 首次会下载 Embedding 模型，可能抛网络异常
            _retriever = HybridRetriever(chroma, tfidf)
            logger.info('RAG 后端：%s', _retriever.name)
        except Exception:
            logger.warning('ChromaDB 不可用，降级为纯 TF-IDF 检索', exc_info=True)
            _retriever = tfidf
    return _retriever


def retrieve(query, city=None, top_k=15):
    """按用户偏好召回相关景点（返回 Attraction 列表，按相关度排序）"""
    try:
        return get_retriever().retrieve(query, city=city, top_k=top_k)
    except Exception:
        logger.exception('RAG 检索失败')
        return []


def rebuild_index():
    """强制重建索引（数据更新后调用），返回实际使用的后端名"""
    global _retriever
    qs = _queryset()
    tfidf = TfidfRetriever()
    tfidf.ensure_index(qs)
    try:
        chroma = ChromaRetriever()
        chroma.rebuild(qs)
        _retriever = HybridRetriever(chroma, tfidf)
    except Exception:
        logger.warning('ChromaDB 重建失败，降级为纯 TF-IDF', exc_info=True)
        _retriever = tfidf
    return _retriever.name
