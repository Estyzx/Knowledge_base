from django.db import models

# Create your models here.


# 品种库
class Variety(models.Model):
    name = models.CharField('品种名称',max_length=50,unique=False,blank=False)
    description = models.TextField('品种描述',blank=True)
    
    create_time = models.DateTimeField('创建时间',auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True)
    planting_tech = models.ManyToManyField('PlantingTech',verbose_name='种植技术',blank=True)
    pest = models.ManyToManyField('Pest',verbose_name='病虫害',blank=True)
    def __str__(self):
        return self.name
    class Meta:
        # 显示名称
        verbose_name = '品种'
        verbose_name_plural = verbose_name
        # 排序方式
        ordering = ['-create_time']


# 种植技术库
class PlantingTech(models.Model):
    name = models.CharField('种植技术名称',max_length=50,unique=False,blank=False)
    description = models.TextField('种植技术描述',blank=True)
    create_time = models.DateTimeField('创建时间',auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True)

    class Meta:
        verbose_name = '种植技术'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']



# 病虫害库
class Pest(models.Model):
    name = models.CharField('病虫害名称',max_length=50,unique=False,blank=False)
    description = models.TextField('病虫害描述',blank=True)
    create_time = models.DateTimeField('创建时间',auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True)

    class Meta:
        verbose_name = '病虫害'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']


