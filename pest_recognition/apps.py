from django.apps import AppConfig
import os
from pathlib import Path

class PestRecognitionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pest_recognition'
    verbose_name = '病虫害识别'
    
    def ready(self):
        # 创建必要的目录结构
        from django.conf import settings
        
        # 确保媒体根目录存在
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            os.makedirs(media_root)
            print(f"已创建媒体根目录: {media_root}")
            
        # 创建临时识别图像目录
        temp_recognition_dir = os.path.join(media_root, 'temp_recognition')
        if not os.path.exists(temp_recognition_dir):
            os.makedirs(temp_recognition_dir)
            print(f"已创建临时识别图像目录: {temp_recognition_dir}")
        
        # 创建按年月组织的识别图像目录
        from datetime import datetime
        current_date = datetime.now()
        year_month_dir = os.path.join(media_root, 'recognition_images', 
                                     str(current_date.year), 
                                     str(current_date.month).zfill(2))
        if not os.path.exists(year_month_dir):
            os.makedirs(year_month_dir)
            print(f"已创建识别图像存储目录: {year_month_dir}")
            
        # 应用启动时加载API配置
        from .models import load_recognition_model
        # 确保配置被加载
        try:
            config = load_recognition_model()
            if config.get('enabled'):
                print(f"✅ 病虫害识别API成功启用: {config.get('model')}")
            else:
                print("❌ 病虫害识别API未启用，将使用模拟数据")
        except Exception as e:
            print(f"❌ 加载识别模型配置出错: {str(e)}")
