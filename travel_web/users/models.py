from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """自定义用户模型"""
    phone = models.CharField('手机号', max_length=11, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.username


class Favorite(models.Model):
    """用户收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    attraction = models.ForeignKey('attractions.Attraction', on_delete=models.CASCADE, verbose_name='景点')
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'attraction']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.attraction.name}"


class TravelHistory(models.Model):
    """用户旅游推荐历史"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    city = models.CharField('目标城市', max_length=50)
    season = models.CharField('旅游季节', max_length=20)
    days = models.IntegerField('行程天数')
    budget = models.DecimalField('预算', max_digits=10, decimal_places=2)
    recommendation = models.TextField('AI推荐结果')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '推荐历史'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.city} - {self.created_at.strftime('%Y-%m-%d')}"
