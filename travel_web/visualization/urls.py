from django.urls import path
from visualization import views

app_name = 'visualization'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/score-distribution/', views.score_distribution, name='score_distribution'),
    path('api/province-avg-score/', views.province_avg_score, name='province_avg_score'),
    path('api/top-comments/', views.top_comments, name='top_comments'),
    path('api/city-hot/', views.city_hot_attractions, name='city_hot'),
    path('api/province-count/', views.province_count, name='province_count'),
    path('api/price-distribution/', views.price_distribution, name='price_distribution'),
    path('api/level-distribution/', views.level_distribution, name='level_distribution'),
    path('api/map-data/', views.map_data, name='map_data'),
    path('api/stats/', views.stats_data, name='stats'),
]
