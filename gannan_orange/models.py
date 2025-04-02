from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from User.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# 审核历史记录
class ReviewHistory(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('variety', '品种'),
        ('planting_tech', '种植技术'),
        ('pest', '病虫害'),
        ('soil_type', '土壤类型'),
    ]
    
    REVIEW_ACTION_CHOICES = [
        ('approve', '通过'),
        ('reject', '拒绝'),
        ('comment', '评论'),
    ]
    
    content_type = models.CharField('内容类型', max_length=15, choices=CONTENT_TYPE_CHOICES)
    content_id = models.PositiveIntegerField('内容ID')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='review_histories', verbose_name='审核人')
    action = models.CharField('审核操作', max_length=10, choices=REVIEW_ACTION_CHOICES)
    comment = models.TextField('审核意见', blank=True)
    review_date = models.DateTimeField('审核时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '审核历史'
        verbose_name_plural = verbose_name
        ordering = ['-review_date']
    
    def __str__(self):
        return f"{self.get_content_type_display()}({self.content_id}) - {self.get_action_display()} by {self.reviewer.username}"


# Create your models here.


# 品种库
class Variety(models.Model):
    # 审核状态选项
    REVIEW_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    # 基础信息
    name = models.CharField('品种名称', max_length=50, unique=False, blank=False)
    scientific_name = models.CharField('学名', max_length=150, blank=True)
    origin = models.CharField('原产地', max_length=50, default='中国')
    registration_number = models.CharField('品种登记号', max_length=50, blank=True, help_text='国家或地方品种登记编号')
    
    # 审核信息
    review_status = models.CharField('审核状态', max_length=10, choices=REVIEW_STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_varieties', verbose_name='审核人')
    review_comment = models.TextField('审核意见', blank=True)
    review_date = models.DateTimeField('审核时间', null=True, blank=True)
    
    # 生长特性
    MATURITY_CHOICES = [
        ('early', '早熟'),
        ('mid', '中熟'),
        ('late', '晚熟'),
    ]
    maturity_type = models.CharField('成熟类型', max_length=10, choices=MATURITY_CHOICES, default='mid')
    harvest_season = models.CharField('采收季节', max_length=50, blank=True, help_text='如：10-12月')
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
    altitude_range = models.CharField('适宜海拔范围(米)', max_length=50, blank=True, help_text='如：200-800米')
    annual_yield = models.DecimalField('平均亩产(kg)', max_digits=7, decimal_places=1, null=True, blank=True)
    tree_shape = models.CharField('树形', max_length=50, blank=True, help_text='如：开心形、自然圆头形等')
    pollination_type = models.CharField('授粉类型', max_length=50, blank=True, help_text='如：自花授粉、虫媒授粉等')
    
    # 果实特性
    FRUIT_SHAPE_CHOICES = [
        ('round', '圆形'),
        ('oblate', '扁圆形'),
        ('oval', '椭圆形'),
        ('pear', '梨形'),
        ('irregular', '不规则形'),
    ]
    fruit_shape = models.CharField('果实形状', max_length=20, choices=FRUIT_SHAPE_CHOICES, default='round')
    fruit_color = models.CharField('果皮颜色', max_length=50, blank=True)
    fruit_weight = models.DecimalField(
        '平均单果重(g)',
        max_digits=5, decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        default=50
    )
    brix = models.DecimalField(
        '可溶性固形物(%)',
        max_digits=4, decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        default=10
    )
    peel_thickness = models.DecimalField(
        '果皮厚度(mm)',
        max_digits=3, decimal_places=1,default=0.5
    )
    seed_count = models.PositiveSmallIntegerField('平均种子数', null=True, blank=True)
    juice_content = models.DecimalField('果汁含量(%)', max_digits=4, decimal_places=1, null=True, blank=True)
    acidity = models.DecimalField('酸度(%)', max_digits=3, decimal_places=2, null=True, blank=True)
    sugar_acid_ratio = models.DecimalField('糖酸比', max_digits=5, decimal_places=2, null=True, blank=True)
    shelf_life = models.PositiveSmallIntegerField('保鲜期(天)', null=True, blank=True)
    
    # 抗性特征
    TOLERANCE_CHOICES = [
        ('high', '强'),
        ('medium', '中'),
        ('low', '弱'),
    ]
    cold_tolerance = models.CharField(
        '耐寒性',
        max_length=10,
        choices=TOLERANCE_CHOICES,
        default='medium'
    )
    drought_tolerance = models.CharField(
        '耐旱性',
        max_length=10,
        choices=TOLERANCE_CHOICES,
        default='medium'
    )
    disease_resistance = models.CharField(
        '抗病性',
        max_length=10,
        choices=TOLERANCE_CHOICES,
        default='medium'
    )
    waterlogging_tolerance = models.CharField(
        '耐涝性',
        max_length=10,
        choices=TOLERANCE_CHOICES,
        default='medium'
    )

    soil_preference = models.ManyToManyField(
        'SoilType',
        verbose_name='适宜土壤类型',
        blank=True
    )
    favorite_user = models.ManyToManyField(
        CustomUser,
        verbose_name='收藏用户',
        related_name='favorite_varieties',
        blank=True
    )

    description = models.TextField('品种描述', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    planting_tech = models.ManyToManyField('PlantingTech', verbose_name='种植技术', blank=True)
    pest = models.ManyToManyField('Pest', verbose_name='病虫害', blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='品种分类', related_name='varieties')

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        # 检查是否是已存在的对象（更新操作）
        if self.pk is not None:
            # 获取数据库中当前对象的状态
            old_instance = Variety.objects.get(pk=self.pk)
            # 如果已审核通过，检查关键字段是否有变动
            if old_instance.review_status == 'approved':
                # 定义需要监控变动的关键字段列表
                key_fields = ['name', 'scientific_name', 'origin', 'maturity_type', 'fruit_shape', 
                              'fruit_weight', 'brix', 'description', 'cold_tolerance', 'disease_resistance']
                # 检查关键字段是否有变动
                for field in key_fields:
                    if getattr(old_instance, field) != getattr(self, field):
                        # 如果有变动，重置审核状态为待审核
                        self.review_status = 'pending'
                        self.review_comment = '内容已修改，需要重新审核'
                        self.review_date = None
                        self.reviewer = None
                        break
        # 调用父类的save方法保存对象
        super().save(*args, **kwargs)

    class Meta:
        # 显示名称
        verbose_name = '品种'
        verbose_name_plural = verbose_name
        # 排序方式
        ordering = ['-create_time']

# 种植技术库
class PlantingTech(models.Model):
    # 审核状态选项
    REVIEW_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    CATEGORY_CHOICES = [
        ('planting', '栽培管理'),
        ('pruning', '修剪整形'),
        ('fertilization', '施肥技术'),
        ('irrigation', '灌溉技术'),
        ('pest_control', '病虫害防治'),
        ('harvest', '采收技术'),
        ('storage', '贮藏保鲜'),
        ('other', '其他技术'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
        ('expert', '专家'),
    ]
    
    SEASON_CHOICES = [
        ('spring', '春季'),
        ('summer', '夏季'),
        ('autumn', '秋季'),
        ('winter', '冬季'),
        ('all', '全年'),
    ]
    
    name = models.CharField('种植技术名称', max_length=50, unique=False, blank=False)
    category = models.CharField('技术类别', max_length=20, choices=CATEGORY_CHOICES, default='planting')
    difficulty = models.CharField('难度级别', max_length=15, choices=DIFFICULTY_CHOICES, default='intermediate')
    applicable_season = models.CharField('适用季节', max_length=10, choices=SEASON_CHOICES, default='all')
    estimated_cost = models.CharField('预估成本', max_length=50, blank=True, help_text='如：低/中/高或具体金额范围')
    labor_intensity = models.CharField('劳动强度', max_length=10, choices=[('low', '低'), ('medium', '中'), ('high', '高')], default='medium')
    equipment_needed = models.TextField('所需设备工具', blank=True)
    expected_outcome = models.TextField('预期效果', blank=True)
    description = models.TextField('种植技术描述', blank=True)
    precautions = models.TextField('注意事项', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    
    # 审核信息
    review_status = models.CharField('审核状态', max_length=10, choices=REVIEW_STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_planting_techs', verbose_name='审核人')
    review_comment = models.TextField('审核意见', blank=True)
    review_date = models.DateTimeField('审核时间', null=True, blank=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        # 检查是否是已存在的对象（更新操作）
        if self.pk is not None:
            # 获取数据库中当前对象的状态
            old_instance = PlantingTech.objects.get(pk=self.pk)
            # 如果已审核通过，检查关键字段是否有变动
            if old_instance.review_status == 'approved':
                # 定义需要监控变动的关键字段列表
                key_fields = ['name', 'category', 'difficulty', 'applicable_season', 
                              'description', 'equipment_needed', 'expected_outcome', 'precautions']
                # 检查关键字段是否有变动
                for field in key_fields:
                    if getattr(old_instance, field) != getattr(self, field):
                        # 如果有变动，重置审核状态为待审核
                        self.review_status = 'pending'
                        self.review_comment = '内容已修改，需要重新审核'
                        self.review_date = None
                        self.reviewer = None
                        break
        # 调用父类的save方法保存对象
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '种植技术'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']


# 病虫害库
class Pest(models.Model):
    # 审核状态选项
    REVIEW_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    TYPE_CHOICES = [
        ('disease', '病害'),
        ('insect', '虫害'),
        ('mite', '螨害'),
        ('weed', '杂草'),
        ('other', '其他'),
    ]
    
    SEVERITY_CHOICES = [
        ('mild', '轻微'),
        ('moderate', '中等'),
        ('severe', '严重'),
        ('devastating', '毁灭性'),
    ]
    
    name = models.CharField('病虫害名称', max_length=50, unique=False, blank=False)
    scientific_name = models.CharField('学名', max_length=100, blank=True)
    type = models.CharField('类型', max_length=10, choices=TYPE_CHOICES, default='disease')
    severity = models.CharField('危害程度', max_length=12, choices=SEVERITY_CHOICES, default='moderate')
    occurrence_season = models.CharField('发生季节', max_length=50, blank=True, help_text='如：春季、夏季或具体月份')
    affected_parts = models.CharField('受害部位', max_length=100, blank=True, help_text='如：叶片、果实、根系等')
    symptoms = models.TextField('症状特征', blank=True)
    life_cycle = models.TextField('生活史', blank=True)
    prevention_methods = models.TextField('预防方法', blank=True)
    chemical_control = models.TextField('化学防治', blank=True, help_text='推荐药剂及使用方法')
    biological_control = models.TextField('生物防治', blank=True)
    physical_control = models.TextField('物理防治', blank=True)
    description = models.TextField('病虫害描述', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    
    # 审核信息
    review_status = models.CharField('审核状态', max_length=10, choices=REVIEW_STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_pests', verbose_name='审核人')
    review_comment = models.TextField('审核意见', blank=True)
    review_date = models.DateTimeField('审核时间', null=True, blank=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        # 检查是否是已存在的对象（更新操作）
        if self.pk is not None:
            # 获取数据库中当前对象的状态
            old_instance = Pest.objects.get(pk=self.pk)
            # 如果已审核通过，检查关键字段是否有变动
            if old_instance.review_status == 'approved':
                # 定义需要监控变动的关键字段列表
                key_fields = ['name', 'scientific_name', 'type', 'severity', 'symptoms', 
                              'life_cycle', 'prevention_methods', 'chemical_control', 
                              'biological_control', 'physical_control', 'description']
                # 检查关键字段是否有变动
                for field in key_fields:
                    if getattr(old_instance, field) != getattr(self, field):
                        # 如果有变动，重置审核状态为待审核
                        self.review_status = 'pending'
                        self.review_comment = '内容已修改，需要重新审核'
                        self.review_date = None
                        self.reviewer = None
                        break
        # 调用父类的save方法保存对象
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '病虫害'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

# 土壤类型库
class SoilType(models.Model):
    # 审核状态选项
    REVIEW_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    TEXTURE_CHOICES = [
        ('sandy', '砂质'),
        ('loamy', '壤质'),
        ('clay', '粘质'),
        ('silty', '粉质'),
        ('peaty', '泥炭质'),
        ('chalky', '石灰质'),
        ('mixed', '混合质'),
    ]
    
    DRAINAGE_CHOICES = [
        ('excellent', '优'),
        ('good', '良'),
        ('moderate', '中'),
        ('poor', '差'),
    ]
    
    FERTILITY_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]
    
    name = models.CharField('土壤名称', max_length=50, unique=True)
    texture = models.CharField('土壤质地', max_length=10, choices=TEXTURE_CHOICES, default='loamy')
    ph_range = models.CharField('pH范围', max_length=10)  # 5.5-6.5
    organic_matter = models.DecimalField(
        '有机质含量(%)',
        max_digits=3,
        decimal_places=1
    )
    drainage = models.CharField('排水性', max_length=10, choices=DRAINAGE_CHOICES, default='good')
    water_retention = models.CharField('保水性', max_length=10, choices=[('high', '强'), ('medium', '中'), ('low', '弱')], default='medium')
    fertility = models.CharField('肥力', max_length=10, choices=FERTILITY_CHOICES, default='medium')
    nitrogen_content = models.DecimalField('氮含量(%)', max_digits=4, decimal_places=2, null=True, blank=True)
    phosphorus_content = models.DecimalField('磷含量(mg/kg)', max_digits=6, decimal_places=2, null=True, blank=True)
    potassium_content = models.DecimalField('钾含量(mg/kg)', max_digits=6, decimal_places=2, null=True, blank=True)
    cation_exchange = models.DecimalField('阳离子交换量(cmol/kg)', max_digits=5, decimal_places=2, null=True, blank=True)
    suitable_crops = models.TextField('适宜作物', blank=True)
    improvement_methods = models.TextField('改良方法', blank=True)
    description = models.TextField('特征描述')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    
    # 审核信息
    review_status = models.CharField('审核状态', max_length=10, choices=REVIEW_STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_soil_types', verbose_name='审核人')
    review_comment = models.TextField('审核意见', blank=True)
    review_date = models.DateTimeField('审核时间', null=True, blank=True)

    def __str__(self):
        return f"{self.name} (pH {self.ph_range})"
        
    def save(self, *args, **kwargs):
        # 检查是否是已存在的对象（更新操作）
        if self.pk is not None:
            # 获取数据库中当前对象的状态
            old_instance = SoilType.objects.get(pk=self.pk)
            # 如果已审核通过，检查关键字段是否有变动
            if old_instance.review_status == 'approved':
                # 定义需要监控变动的关键字段列表
                key_fields = ['name', 'texture', 'ph_range', 'organic_matter', 'drainage', 
                              'water_retention', 'fertility', 'nitrogen_content', 'phosphorus_content', 
                              'potassium_content', 'suitable_crops', 'improvement_methods', 'description']
                # 检查关键字段是否有变动
                for field in key_fields:
                    if getattr(old_instance, field) != getattr(self, field):
                        # 如果有变动，重置审核状态为待审核
                        self.review_status = 'pending'
                        self.review_comment = '内容已修改，需要重新审核'
                        self.review_date = None
                        self.reviewer = None
                        break
        # 调用父类的save方法保存对象
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = '土壤类型'
        verbose_name_plural = verbose_name
        ordering = ['name']

class Category(models.Model):
    name = models.CharField('分类名称', max_length=50, unique=True)
    description = models.TextField('分类描述', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name ='品种分类'
        verbose_name_plural = verbose_name
        ordering = ['name']