from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models



# Create your models here.


# 品种库
class Variety(models.Model):
    # 基础信息
    name = models.CharField('品种名称', max_length=50, unique=False, blank=False)
    scientific_name = models.CharField('学名', max_length=150, blank=True)
    origin = models.CharField('原产地', max_length=50, default='中国')

    # 生长特性
    growth_cycle = models.PositiveSmallIntegerField(
        '生长周期(天)',
        validators=[MinValueValidator(90), MaxValueValidator(365)],
        default=90
    )
    chill_requirement = models.PositiveSmallIntegerField(
        '需冷量(小时)',
        help_text="7.2℃以下低温累计时长",
        default=0
    )

    # 果实特性
    fruit_weight = models.DecimalField(
        '平均单果重(g)',
        max_digits=5, decimal_places=1,
        validators=[MinValueValidator(50), MaxValueValidator(1000)],
        default=50
    )
    brix = models.DecimalField(
        '可溶性固形物(%)',
        max_digits=4, decimal_places=1,
        validators=[MinValueValidator(8), MaxValueValidator(25)],
        default=10
    )
    peel_thickness = models.DecimalField(
        '果皮厚度(mm)',
        max_digits=3, decimal_places=1,default=0.5
    )

    cold_tolerance = models.CharField(
        '耐寒性',
        max_length=10,
        choices=[('high', '强'), ('medium', '中'), ('low', '弱')],
        default='medium'
    )
    drought_tolerance = models.CharField(
        '耐旱性',
        max_length=10,
        choices=[('high', '强'), ('medium', '中'), ('low', '弱')],
        default='medium'
    )

    soil_preference = models.ManyToManyField(
        'SoilType',
        verbose_name='适宜土壤类型'
    )

    description = models.TextField('品种描述', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    planting_tech = models.ManyToManyField('PlantingTech', verbose_name='种植技术', blank=True)
    pest = models.ManyToManyField('Pest', verbose_name='病虫害', blank=True)

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
    name = models.CharField('种植技术名称', max_length=50, unique=False, blank=False)
    description = models.TextField('种植技术描述', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '种植技术'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']


# 病虫害库
class Pest(models.Model):
    name = models.CharField('病虫害名称', max_length=50, unique=False, blank=False)
    description = models.TextField('病虫害描述', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '病虫害'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

# 土壤类型库
class SoilType(models.Model):
    name = models.CharField('土壤类型', max_length=50, unique=True)
    ph_range = models.CharField('pH范围', max_length=10)  # 5.5-6.5
    organic_matter = models.DecimalField(
        '有机质含量(%)',
        max_digits=3,
        decimal_places=1
    )
    description = models.TextField('特征描述')

    def __str__(self):
        return f"{self.name} (pH {self.ph_range})"
    class Meta:
        verbose_name = '土壤类型'
        verbose_name_plural = verbose_name
        ordering = ['name']

class FavoriteVariety(models.Model):
    user = models.ForeignKey('User.CustomUser',verbose_name='用户', on_delete=models.CASCADE)
    variety = models.ForeignKey('Variety',verbose_name= '品种' ,on_delete=models.CASCADE)
    favorite_time = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        verbose_name = '品种收藏'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'variety')
        ordering = ['-favorite_time']

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.variety.name}"

class FavoritePlantingTech(models.Model):
    user = models.ForeignKey('User.CustomUser',verbose_name='用户', on_delete=models.CASCADE)
    planting_tech = models.ForeignKey('PlantingTech',verbose_name= '种植技术' ,on_delete=models.CASCADE)
    favorite_time = models.DateTimeField('收藏时间', auto_now_add=True)
    class Meta:
        verbose_name = '种植技术收藏'
        verbose_name_plural = verbose_name
        ordering = ['-favorite_time']
        unique_together = ('user', 'planting_tech')

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.planting_tech.name}"

class FavoritePest(models.Model):
    user = models.ForeignKey('User.CustomUser',verbose_name='用户', on_delete=models.CASCADE)
    pest = models.ForeignKey('Pest',verbose_name= '病虫害' ,on_delete=models.CASCADE)
    favorite_time = models.DateTimeField('收藏时间', auto_now_add=True)
    class Meta:
        verbose_name = '病虫害收藏'
        verbose_name_plural = verbose_name
        ordering = ['-favorite_time']
        unique_together = ('user', 'pest')

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.pest.name}"