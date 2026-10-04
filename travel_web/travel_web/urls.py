from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('attractions.urls')),
    path('users/', include('users.urls')),
    path('visualization/', include('visualization.urls')),
    path('recommend/', include('ai_recommend.urls')),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin站点配置
admin.site.site_header = '旅游景点推荐系统'
admin.site.site_title = '旅游景点推荐系统'
admin.site.index_title = '后台管理'
