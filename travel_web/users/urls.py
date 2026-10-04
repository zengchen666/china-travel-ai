from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('favorite/add/<int:attraction_id>/', views.add_favorite, name='add_favorite'),
    path('favorite/remove/<int:attraction_id>/', views.remove_favorite, name='remove_favorite'),
    path('favorites/', views.favorite_list, name='favorites'),
]
