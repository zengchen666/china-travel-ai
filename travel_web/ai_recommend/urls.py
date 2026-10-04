from django.urls import path
from ai_recommend import views

app_name = 'ai_recommend'

urlpatterns = [
    path('', views.recommend_page, name='page'),
    path('api/recommend/', views.get_recommendation, name='api'),
    path('history/', views.history_page, name='history'),
]
