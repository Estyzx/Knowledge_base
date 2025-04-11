from django.db import models

class SoilType(models.Model):
    """土壤类型模型"""
    SOIL_TYPE_CHOICES = [
        ('sandy', '砂质土'),
        ('clay', '粘土'),
        ('loam', '壤土'),
        ('silt', '淤泥土'),
        ('peaty', '泥炭土'),
        ('chalky', '石灰质土'),
        ('other', '其他'),
    ]

    TEXTURE_CHOICES = [
        ('coarse', '粗颗粒'),
        ('medium', '中颗粒'),
        ('fine', '细颗粒'),
    ]

    FERTILITY_CHOICES = [
        ('high', '高肥力'),
        ('medium', '中肥力'),
        ('low', '低肥力'),
    ]

    DRAINAGE_CHOICES = [
        ('good', '排水良好'),
        ('medium', '排水一般'),
        ('poor', '排水不良'),
    ]

    name = models.CharField(max_length=100, verbose_name="名称")
    type = models.CharField(max_length=20, choices=SOIL_TYPE_CHOICES, default='other', verbose_name="类型")
    texture = models.CharField(max_length=20, choices=TEXTURE_CHOICES, null=True, blank=True, verbose_name="质地")
    fertility = models.CharField(max_length=20, choices=FERTILITY_CHOICES, null=True, blank=True, verbose_name="肥力")
    drainage = models.CharField(max_length=20, choices=DRAINAGE_CHOICES, null=True, blank=True, verbose_name="排水性")
    description = models.TextField(null=True, blank=True, verbose_name="描述")
    ph_value = models.FloatField(null=True, blank=True, verbose_name="pH值")
    organic_matter = models.FloatField(null=True, blank=True, verbose_name="有机质含量")
    color = models.CharField(max_length=20, null=True, blank=True, verbose_name="颜色")
    color_code = models.CharField(max_length=7, null=True, blank=True, verbose_name="颜色代码")
    water_holding_capacity = models.CharField(max_length=20, null=True, blank=True, verbose_name="保水能力")
    physical_properties = models.TextField(null=True, blank=True, verbose_name="物理性质")
    suitable_crops = models.TextField(null=True, blank=True, verbose_name="适宜作物")
    management_recommendations = models.TextField(null=True, blank=True, verbose_name="管理建议")
    nutrients = models.TextField(null=True, blank=True, verbose_name="营养成分")
    nitrogen_content = models.FloatField(null=True, blank=True, verbose_name="氮含量")
    phosphorus_content = models.FloatField(null=True, blank=True, verbose_name="磷含量")
    potassium_content = models.FloatField(null=True, blank=True, verbose_name="钾含量")
    image = models.ImageField(upload_to='soil_images/', null=True, blank=True, verbose_name="图片")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def get_type_display(self):
        """确保类型显示正确"""
        try:
            return dict(self.SOIL_TYPE_CHOICES)[self.type]
        except (KeyError, AttributeError):
            return "未知类型"

    def get_texture_display(self):
        """确保质地显示正确"""
        try:
            return dict(self.TEXTURE_CHOICES)[self.texture]
        except (KeyError, AttributeError):
            return "未知质地"

    def get_fertility_display(self):
        """确保肥力显示正确"""
        try:
            return dict(self.FERTILITY_CHOICES)[self.fertility]
        except (KeyError, AttributeError):
            return "未知肥力"

    def get_drainage_display(self):
        """确保排水性显示正确"""
        try:
            return dict(self.DRAINAGE_CHOICES)[self.drainage]
        except (KeyError, AttributeError):
            return "未知排水性"

    def __str__(self):
        return self.name