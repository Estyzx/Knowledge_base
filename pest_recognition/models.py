import os
import requests
import json
from django.db import models
from django.conf import settings
from django.utils import timezone
from gannan_orange.models import Pest

# API配置 - 改为只使用Qwen模型
API_CONFIG = {
    "api_key": "",  # 初始为空，将从settings或环境变量加载
    "api_url": "https://api.siliconflow.cn/v1/chat/completions",
    "enabled": False,  # 默认禁用，直到成功加载密钥
    "timeout": 30,
    "model": "qwen2.5-vl-72b-instruct",
    "available_models": {  # 简化为仅使用Qwen模型
        "qwen2.5-vl-72b-instruct": {
            "name": "通义千问 2.5-VL-72B",
            "description": "大型多模态视觉-语言模型，专为图像识别和分析优化",
            "features": ["高精度视觉理解", "详细中文描述", "专业领域知识"],
            "recommended_for": ["所有场景"]
        }
    }
}

def load_recognition_model():
    """
    初始化API配置
    而不是加载本地模型
    """
    # 直接从settings读取，这样可以确保从项目配置中获取
    api_key = getattr(settings, 'PEST_RECOGNITION_API_KEY', 
                     os.environ.get('PEST_RECOGNITION_API_KEY', 
                     'sk-wyxlabcftrhcqidzsgtpibnjdavfpmvumewocjxddofzaccj'))  # 使用默认硬编码密钥作为备选
    
    api_url = getattr(settings, 'PEST_RECOGNITION_API_URL', 
                     os.environ.get('PEST_RECOGNITION_API_URL', 
                     API_CONFIG['api_url']))
    
    model = getattr(settings, 'PEST_RECOGNITION_MODEL', 
                   os.environ.get('PEST_RECOGNITION_MODEL', 
                   API_CONFIG['model']))
    
    # 更新配置
    if api_key and api_key.startswith('sk-'):
        API_CONFIG['api_key'] = api_key
        API_CONFIG['enabled'] = True
        API_CONFIG['api_url'] = api_url
        API_CONFIG['model'] = model
        print(f"病虫害识别API已成功配置，使用模型: {model}")
    else:
        print("警告：病虫害识别API未配置有效密钥，将使用模拟识别")
        API_CONFIG['enabled'] = False
    
    return API_CONFIG

# 更新模型选择指南
MODEL_SELECTION_GUIDE = """
# 通义千问视觉语言模型使用指南

我们使用的是阿里巴巴达摩院开发的通义千问2.5-VL-72B-Instruct多模态大模型，这是一个强大的视觉-语言模型，专为图像理解和分析优化。

## 模型特点

- **高精度视觉理解**：能够精确识别图像中的物体、场景和细节
- **专业领域知识**：包含农业和植物病理学专业知识
- **详细中文描述**：提供丰富、准确的中文分析结果
- **多模态能力**：能同时处理图像输入和文本输入

## 最佳实践

1. **提供清晰图像**：确保病害部位清晰可见，光线充足
2. **多角度拍摄**：对于复杂病症，提供不同角度的照片可提高识别准确率
3. **包含环境信息**：在可能的情况下，包含植物的整体状况和生长环境

## 识别效果

通义千问2.5-VL拥有7200亿参数，是目前最先进的中文多模态模型之一，对中文农业领域的病虫害识别有特别优化，能够提供专业、准确的诊断结果。
"""

class ModelSelection(models.Model):
    """记录模型选择历史及效果"""
    model_name = models.CharField(max_length=50, verbose_name='模型名称')
    success_rate = models.FloatField(default=0.0, verbose_name='识别成功率')
    avg_confidence = models.FloatField(default=0.0, verbose_name='平均置信度')
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    avg_response_time = models.FloatField(default=0.0, verbose_name='平均响应时间(秒)')
    last_used = models.DateTimeField(auto_now=True, verbose_name='最后使用时间')
    
    class Meta:
        verbose_name = '模型使用统计'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f"{self.model_name} - 成功率: {self.success_rate:.2f}% - 次数: {self.usage_count}"

class RecognitionHistory(models.Model):
    """用户的病虫害识别历史记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='用户')
    image = models.ImageField(upload_to='recognition_images/%Y/%m', verbose_name='图片')
    result_pest = models.ForeignKey('gannan_orange.Pest', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='识别结果')
    confidence = models.FloatField(default=0, verbose_name='置信度')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    api_response = models.JSONField(null=True, blank=True, verbose_name='API响应')
    model_used = models.CharField(max_length=255, null=True, blank=True, verbose_name='使用模型')
    response_time = models.FloatField(default=0, verbose_name='响应时间(秒)')
    
    # 新增字段用于显示AI识别结果
    ai_result_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='AI识别名称')
    has_db_match = models.BooleanField(default=True, verbose_name='数据库匹配')
    
    class Meta:
        verbose_name = '识别历史'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
        
    def __str__(self):
        if self.result_pest:
            return f"{self.result_pest.name} - {self.confidence:.2f}"
        return f"未识别 - {self.create_time}"
    
    def update_model_stats(self):
        """更新模型使用统计"""
        if not self.model_used:
            return
            
        model_stat, created = ModelSelection.objects.get_or_create(
            model_name=self.model_used
        )
        
        # 更新使用次数
        model_stat.usage_count += 1
        
        # 计算成功率
        if model_stat.usage_count > 1:
            success_count = RecognitionHistory.objects.filter(
                model_used=self.model_used,
                result_pest__isnull=False
            ).count()
            model_stat.success_rate = (success_count / model_stat.usage_count) * 100
        
        # 计算平均置信度
        confidence_sum = RecognitionHistory.objects.filter(
            model_used=self.model_used,
            result_pest__isnull=False
        ).values_list('confidence', flat=True)
        
        if confidence_sum:
            model_stat.avg_confidence = sum(confidence_sum) / len(confidence_sum)
        
        # 更新平均响应时间
        if model_stat.avg_response_time == 0:
            model_stat.avg_response_time = self.response_time
        else:
            model_stat.avg_response_time = (model_stat.avg_response_time * (model_stat.usage_count - 1) + 
                                          self.response_time) / model_stat.usage_count
        
        model_stat.save()
