from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # 定义角色选项
    ROLE_CHOICES = [
        ('farmer', '农民'),
        ('expert', '专家'),
        ('admin', '管理员'),
    ]

    username = models.CharField('用户名', max_length=50, unique=True)
    phone = models.CharField('手机号', max_length=11, unique=True)
    location = models.CharField('地址', max_length=50, blank=True)
    role = models.CharField('角色', max_length=10, choices=ROLE_CHOICES, default='farmer')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    @property
    def is_expert(self):
        return self.role == 'expert'

    @property
    def is_farmer(self):
        return self.role == 'farmer'
