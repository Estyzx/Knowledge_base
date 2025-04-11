import os
import django

# 设置Django项目的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Knowledge_base.settings')  # 替换为你的项目名称
django.setup()

from gannan_orange.models import SoilType  # 替换为你的应用名称和模型


clay_soil, created = SoilType.objects.update_or_create(
    name='黏土',
    defaults={
        'texture': 'clay',
        'ph_range': '6.0-7.0',
        'organic_matter': 4.5,
        'drainage': 'poor',
        'water_retention': 'high',
        'fertility': 'high',
        'nitrogen_content': 0.40,
        'phosphorus_content': 30.00,
        'potassium_content': 200.00,
        'cation_exchange': 25.00,
        'suitable_crops': '水稻、莲藕等耐湿作物',
        'improvement_methods': '排水、增施有机肥、深翻土壤',
        'description': '黏土质地细腻，黏粒含量高，保水保肥能力强，但通气性和透水性较差。',
    }
)
if created:
    print("黏土数据已创建。")
else:
    print("黏土数据已更新。")