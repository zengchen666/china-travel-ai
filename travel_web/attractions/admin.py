from django.contrib import admin
from django.utils.html import format_html
from .models import Province, City, Attraction


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city_count', 'attraction_count']
    search_fields = ['name']
    
    def city_count(self, obj):
        return obj.city_set.count()
    city_count.short_description = '城市数量'
    
    def attraction_count(self, obj):
        count = Attraction.objects.filter(city__province=obj).count()
        return count
    attraction_count.short_description = '景点数量'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'province', 'attraction_count']
    list_filter = ['province']
    search_fields = ['name']
    
    def attraction_count(self, obj):
        return obj.attraction_set.count()
    attraction_count.short_description = '景点数量'


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city', 'show_score', 'comment_count', 'show_price', 'level', 'show_image']
    list_filter = ['city__province', 'city', 'level']
    search_fields = ['name', 'address']
    list_per_page = 20
    list_editable = ['level']
    readonly_fields = ['show_large_image', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'city', 'address', 'description')
        }),
        ('评价信息', {
            'fields': ('score', 'comment_count', 'price', 'level')
        }),
        ('位置信息', {
            'fields': ('longitude', 'latitude')
        }),
        ('图片', {
            'fields': ('image_url', 'show_large_image')
        }),
        ('其他', {
            'fields': ('open_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def show_score(self, obj):
        if obj.score:
            color = '#28a745' if obj.score >= 4.5 else '#ffc107' if obj.score >= 4 else '#dc3545'
            return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, obj.score)
        return '-'
    show_score.short_description = '评分'
    
    def show_price(self, obj):
        if obj.price and obj.price > 0:
            return format_html('<span style="color:#e74c3c;">¥{}</span>', int(obj.price))
        return format_html('<span style="color:#28a745;">免费</span>')
    show_price.short_description = '票价'
    
    def show_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="60" height="40" style="object-fit:cover;border-radius:4px;"/>', obj.image_url)
        return '-'
    show_image.short_description = '图片'
    
    def show_large_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="300" style="border-radius:8px;"/>', obj.image_url)
        return '暂无图片'
    show_large_image.short_description = '图片预览'
