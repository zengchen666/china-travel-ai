from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, TravelHistory, Favorite


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'email', 'phone', 'favorite_count', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone']
    list_per_page = 20
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('phone', 'avatar')}),
    )
    
    def favorite_count(self, obj):
        count = obj.favorite_set.count()
        return format_html('<span style="color:#e74c3c;">{}</span>', count)
    favorite_count.short_description = '收藏数'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'attraction', 'attraction_city', 'created_at']
    list_filter = ['created_at', 'attraction__city__province']
    search_fields = ['user__username', 'attraction__name']
    list_per_page = 20
    autocomplete_fields = ['user', 'attraction']
    
    def attraction_city(self, obj):
        return f"{obj.attraction.city.province.name} - {obj.attraction.city.name}"
    attraction_city.short_description = '所在城市'


@admin.register(TravelHistory)
class TravelHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'city', 'season', 'days', 'show_budget', 'created_at']
    list_filter = ['season', 'city', 'created_at']
    search_fields = ['user__username', 'city']
    readonly_fields = ['recommendation', 'created_at']
    list_per_page = 20
    
    def show_budget(self, obj):
        return format_html('<span style="color:#28a745;">¥{}</span>', int(obj.budget))
    show_budget.short_description = '预算'
