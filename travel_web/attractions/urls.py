from django.urls import path
from attractions import views

app_name = 'attractions'

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.attraction_list, name='list'),
    path('detail/<int:pk>/', views.attraction_detail, name='detail'),
    path('search/', views.search, name='search'),
]
