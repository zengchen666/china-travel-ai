# -*- coding: utf-8 -*-
"""重建景点 RAG 检索索引：python manage.py rebuild_rag"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '重建景点 RAG 向量检索索引（景点数据更新后执行）'

    def handle(self, *args, **options):
        from ai_recommend.rag import rebuild_index
        backend = rebuild_index()
        self.stdout.write(self.style.SUCCESS(f'RAG 索引重建完成（后端：{backend}）'))
