# Generated by Django 5.1.5 on 2025-04-11 10:58

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='分类名称')),
                ('description', models.TextField(blank=True, verbose_name='分类描述')),
            ],
            options={
                'verbose_name': '品种分类',
                'verbose_name_plural': '品种分类',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Pest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='病虫害名称')),
                ('scientific_name', models.CharField(blank=True, max_length=100, verbose_name='学名')),
                ('type', models.CharField(choices=[('disease', '病害'), ('insect', '虫害'), ('mite', '螨害'), ('weed', '杂草'), ('other', '其他')], default='disease', max_length=10, verbose_name='类型')),
                ('severity', models.CharField(choices=[('mild', '轻微'), ('moderate', '中等'), ('severe', '严重'), ('devastating', '毁灭性')], default='moderate', max_length=12, verbose_name='危害程度')),
                ('occurrence_season', models.CharField(blank=True, help_text='如：春季、夏季或具体月份', max_length=50, verbose_name='发生季节')),
                ('affected_parts', models.CharField(blank=True, help_text='如：叶片、果实、根系等', max_length=100, verbose_name='受害部位')),
                ('symptoms', models.TextField(blank=True, verbose_name='症状特征')),
                ('life_cycle', models.TextField(blank=True, verbose_name='生活史')),
                ('prevention_methods', models.TextField(blank=True, verbose_name='预防方法')),
                ('chemical_control', models.TextField(blank=True, help_text='推荐药剂及使用方法', verbose_name='化学防治')),
                ('biological_control', models.TextField(blank=True, verbose_name='生物防治')),
                ('physical_control', models.TextField(blank=True, verbose_name='物理防治')),
                ('description', models.TextField(blank=True, verbose_name='病虫害描述')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('review_status', models.CharField(choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已拒绝')], default='pending', max_length=10, verbose_name='审核状态')),
                ('review_comment', models.TextField(blank=True, verbose_name='审核意见')),
                ('review_date', models.DateTimeField(blank=True, null=True, verbose_name='审核时间')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_pests', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
            ],
            options={
                'verbose_name': '病虫害',
                'verbose_name_plural': '病虫害',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='PlantingTech',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='种植技术名称')),
                ('category', models.CharField(choices=[('planting', '栽培管理'), ('pruning', '修剪整形'), ('fertilization', '施肥技术'), ('irrigation', '灌溉技术'), ('pest_control', '病虫害防治'), ('harvest', '采收技术'), ('storage', '贮藏保鲜'), ('other', '其他技术')], default='planting', max_length=20, verbose_name='技术类别')),
                ('difficulty', models.CharField(choices=[('beginner', '初级'), ('intermediate', '中级'), ('advanced', '高级'), ('expert', '专家')], default='intermediate', max_length=15, verbose_name='难度级别')),
                ('applicable_season', models.CharField(choices=[('spring', '春季'), ('summer', '夏季'), ('autumn', '秋季'), ('winter', '冬季'), ('all', '全年')], default='all', max_length=10, verbose_name='适用季节')),
                ('estimated_cost', models.CharField(blank=True, help_text='如：低/中/高或具体金额范围', max_length=50, verbose_name='预估成本')),
                ('labor_intensity', models.CharField(choices=[('low', '低'), ('medium', '中'), ('high', '高')], default='medium', max_length=10, verbose_name='劳动强度')),
                ('equipment_needed', models.TextField(blank=True, verbose_name='所需设备工具')),
                ('expected_outcome', models.TextField(blank=True, verbose_name='预期效果')),
                ('description', models.TextField(blank=True, verbose_name='种植技术描述')),
                ('precautions', models.TextField(blank=True, verbose_name='注意事项')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('review_status', models.CharField(choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已拒绝')], default='pending', max_length=10, verbose_name='审核状态')),
                ('review_comment', models.TextField(blank=True, verbose_name='审核意见')),
                ('review_date', models.DateTimeField(blank=True, null=True, verbose_name='审核时间')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_planting_techs', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
            ],
            options={
                'verbose_name': '种植技术',
                'verbose_name_plural': '种植技术',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='ReviewHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(choices=[('variety', '品种'), ('planting_tech', '种植技术'), ('pest', '病虫害'), ('soil_type', '土壤类型')], max_length=15, verbose_name='内容类型')),
                ('content_id', models.PositiveIntegerField(verbose_name='内容ID')),
                ('action', models.CharField(choices=[('approve', '通过'), ('reject', '拒绝'), ('comment', '评论')], max_length=10, verbose_name='审核操作')),
                ('comment', models.TextField(blank=True, verbose_name='审核意见')),
                ('review_date', models.DateTimeField(auto_now_add=True, verbose_name='审核时间')),
                ('content_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='内容名称')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_histories', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
            ],
            options={
                'verbose_name': '审核历史',
                'verbose_name_plural': '审核历史',
                'ordering': ['-review_date'],
            },
        ),
        migrations.CreateModel(
            name='SoilType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='土壤名称')),
                ('texture', models.CharField(choices=[('sandy', '砂质'), ('loamy', '壤质'), ('clay', '粘质'), ('silty', '粉质'), ('peaty', '泥炭质'), ('chalky', '石灰质'), ('mixed', '混合质')], default='loamy', max_length=10, verbose_name='土壤质地')),
                ('ph_range', models.CharField(max_length=10, verbose_name='pH范围')),
                ('organic_matter', models.DecimalField(decimal_places=1, max_digits=3, verbose_name='有机质含量(%)')),
                ('drainage', models.CharField(choices=[('excellent', '优'), ('good', '良'), ('moderate', '中'), ('poor', '差')], default='good', max_length=10, verbose_name='排水性')),
                ('water_retention', models.CharField(choices=[('high', '强'), ('medium', '中'), ('low', '弱')], default='medium', max_length=10, verbose_name='保水性')),
                ('fertility', models.CharField(choices=[('high', '高'), ('medium', '中'), ('low', '低')], default='medium', max_length=10, verbose_name='肥力')),
                ('nitrogen_content', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='氮含量(%)')),
                ('phosphorus_content', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='磷含量(mg/kg)')),
                ('potassium_content', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='钾含量(mg/kg)')),
                ('cation_exchange', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='阳离子交换量(cmol/kg)')),
                ('suitable_crops', models.TextField(blank=True, verbose_name='适宜作物')),
                ('improvement_methods', models.TextField(blank=True, verbose_name='改良方法')),
                ('description', models.TextField(verbose_name='特征描述')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('review_status', models.CharField(choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已拒绝')], default='pending', max_length=10, verbose_name='审核状态')),
                ('review_comment', models.TextField(blank=True, verbose_name='审核意见')),
                ('review_date', models.DateTimeField(blank=True, null=True, verbose_name='审核时间')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_soil_types', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
            ],
            options={
                'verbose_name': '土壤类型',
                'verbose_name_plural': '土壤类型',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Variety',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='品种名称')),
                ('scientific_name', models.CharField(blank=True, max_length=150, verbose_name='学名')),
                ('origin', models.CharField(default='中国', max_length=50, verbose_name='原产地')),
                ('registration_number', models.CharField(blank=True, help_text='国家或地方品种登记编号', max_length=50, verbose_name='品种登记号')),
                ('review_status', models.CharField(choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已拒绝')], default='pending', max_length=10, verbose_name='审核状态')),
                ('review_comment', models.TextField(blank=True, verbose_name='审核意见')),
                ('review_date', models.DateTimeField(blank=True, null=True, verbose_name='审核时间')),
                ('maturity_type', models.CharField(choices=[('early', '早熟'), ('mid', '中熟'), ('late', '晚熟')], default='mid', max_length=10, verbose_name='成熟类型')),
                ('harvest_season', models.CharField(blank=True, help_text='如：10-12月', max_length=50, verbose_name='采收季节')),
                ('growth_cycle', models.PositiveSmallIntegerField(default=90, validators=[django.core.validators.MinValueValidator(90), django.core.validators.MaxValueValidator(365)], verbose_name='生长周期(天)')),
                ('chill_requirement', models.PositiveSmallIntegerField(default=0, help_text='7.2℃以下低温累计时长', verbose_name='需冷量(小时)')),
                ('altitude_range', models.CharField(blank=True, help_text='如：200-800米', max_length=50, verbose_name='适宜海拔范围(米)')),
                ('annual_yield', models.DecimalField(blank=True, decimal_places=1, max_digits=7, null=True, verbose_name='平均亩产(kg)')),
                ('tree_shape', models.CharField(blank=True, help_text='如：开心形、自然圆头形等', max_length=50, verbose_name='树形')),
                ('pollination_type', models.CharField(blank=True, help_text='如：自花授粉、虫媒授粉等', max_length=50, verbose_name='授粉类型')),
                ('fruit_shape', models.CharField(choices=[('round', '圆形'), ('oblate', '扁圆形'), ('oval', '椭圆形'), ('pear', '梨形'), ('irregular', '不规则形')], default='round', max_length=20, verbose_name='果实形状')),
                ('fruit_color', models.CharField(blank=True, max_length=50, verbose_name='果皮颜色')),
                ('fruit_weight', models.DecimalField(decimal_places=1, default=50, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)], verbose_name='平均单果重(g)')),
                ('brix', models.DecimalField(decimal_places=1, default=10, max_digits=4, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(25)], verbose_name='可溶性固形物(%)')),
                ('peel_thickness', models.DecimalField(decimal_places=1, default=0.5, max_digits=3, verbose_name='果皮厚度(mm)')),
                ('seed_count', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='平均种子数')),
                ('juice_content', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True, verbose_name='果汁含量(%)')),
                ('acidity', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='酸度(%)')),
                ('sugar_acid_ratio', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='糖酸比')),
                ('shelf_life', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='保鲜期(天)')),
                ('cold_tolerance', models.CharField(choices=[('high', '强'), ('medium', '中'), ('low', '弱')], default='medium', max_length=10, verbose_name='耐寒性')),
                ('drought_tolerance', models.CharField(choices=[('high', '强'), ('medium', '中'), ('low', '弱')], default='medium', max_length=10, verbose_name='耐旱性')),
                ('disease_resistance', models.CharField(choices=[('high', '强'), ('medium', '中'), ('low', '弱')], default='medium', max_length=10, verbose_name='抗病性')),
                ('waterlogging_tolerance', models.CharField(choices=[('high', '强'), ('medium', '中'), ('low', '弱')], default='medium', max_length=10, verbose_name='耐涝性')),
                ('description', models.TextField(blank=True, verbose_name='品种描述')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='varieties', to='gannan_orange.category', verbose_name='品种分类')),
                ('favorite_user', models.ManyToManyField(blank=True, related_name='favorite_varieties', to=settings.AUTH_USER_MODEL, verbose_name='收藏用户')),
                ('pest', models.ManyToManyField(blank=True, to='gannan_orange.pest', verbose_name='病虫害')),
                ('planting_tech', models.ManyToManyField(blank=True, to='gannan_orange.plantingtech', verbose_name='种植技术')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_varieties', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
                ('soil_preference', models.ManyToManyField(blank=True, to='gannan_orange.soiltype', verbose_name='适宜土壤类型')),
            ],
            options={
                'verbose_name': '品种',
                'verbose_name_plural': '品种',
                'ordering': ['-create_time'],
            },
        ),
    ]
