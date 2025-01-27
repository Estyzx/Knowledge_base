from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    username = models.CharField('用户名',max_length=50,unique=True)
    phone = models.CharField('手机号',max_length=11,unique=True)
    location = models.CharField('地址',max_length=50,blank=True)


    class Meta:

        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
