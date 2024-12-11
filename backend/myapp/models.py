from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
import os

def get_file_path(instance, filename):
    """自定义文件上传路径"""
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 使用当前时间作为文件名
    filename = f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    # 返回 survey_files/年/月/文件名 格式的路径
    return os.path.join('survey_files', 
                       timezone.now().strftime('%Y'),
                       timezone.now().strftime('%m'),
                       filename)

class UserManager(BaseUserManager):
    def create_user(self, username, display_name, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名必须提供')
        user = self.model(
            username=username,
            display_name=display_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, display_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        return self.create_user(username, display_name, password, **extra_fields)

class UserProfile(AbstractUser):
    """自定义用户模型"""
    USER_TYPES = (
        ('user', '普通用户'),
        ('admin', '管理员'),
    )
    
    username = models.CharField('用户ID', max_length=20, unique=True)
    display_name = models.CharField('显示名称', max_length=50,default='')
    user_type = models.CharField('用户类型', max_length=20, choices=USER_TYPES, default='user')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['display_name']

    def __str__(self):
        return f'{self.username} ({self.display_name})'

    def save(self, *args, **kwargs):
        if not self.pk:  # 如果是新创建的对象
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        swappable = 'AUTH_USER_MODEL'

class Survey(models.Model):
    """调查记录模型"""
    name = models.CharField(max_length=100, verbose_name='调查名称')
    longitude = models.FloatField(verbose_name='经度')
    latitude = models.FloatField(verbose_name='纬度')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    investigator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='调查人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

class MediaItem(models.Model):
    """媒体资料模型"""
    MEDIA_TYPES = (
        ('IMAGE', '图片'),
        ('AUDIO', '音频'),
        ('VIDEO', '视频'),
        ('DOCUMENT', '文档'),
    )
    
    CATEGORY_TYPES = (
        ('FOLKLORE', '风土人情'),
        ('INTERVIEW', '访谈记录'),
        ('LITERATURE', '文献资料'),
    )

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='media_items', verbose_name='所属调查')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, verbose_name='媒体类型')
    category = models.CharField(max_length=10, choices=CATEGORY_TYPES, verbose_name='资料分类')
    file_path = models.FileField(upload_to=get_file_path, verbose_name='文件路径')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    def __str__(self):
        return self.title
