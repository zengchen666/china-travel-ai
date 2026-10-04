from django.db import models


class Province(models.Model):
    """省份"""
    name = models.CharField('省份名称', max_length=50, unique=True)
    
    class Meta:
        verbose_name = '省份'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name


class City(models.Model):
    """城市"""
    name = models.CharField('城市名称', max_length=50)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name='所属省份')
    
    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name


class Attraction(models.Model):
    """景点"""
    name = models.CharField('景点名称', max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='所属城市')
    address = models.CharField('详细地址', max_length=500, blank=True)
    score = models.DecimalField('评分', max_digits=3, decimal_places=1, null=True, blank=True)
    comment_count = models.IntegerField('评论数量', default=0)
    price = models.DecimalField('票价', max_digits=10, decimal_places=2, null=True, blank=True)
    longitude = models.DecimalField('经度', max_digits=10, decimal_places=6, null=True, blank=True)
    latitude = models.DecimalField('纬度', max_digits=10, decimal_places=6, null=True, blank=True)
    image_url = models.URLField('图片链接', max_length=500, blank=True)
    description = models.TextField('景点描述', blank=True)
    open_time = models.CharField('开放时间', max_length=200, blank=True)
    level = models.CharField('景区等级', max_length=50, blank=True)  # 如5A、4A等
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '景点'
        verbose_name_plural = verbose_name
        ordering = ['-comment_count']
    
    def __str__(self):
        return self.name
