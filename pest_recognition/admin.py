from django.contrib import admin
from .models import RecognitionHistory, ModelSelection

class RecognitionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'result_pest', 'confidence', 'model_used', 'create_time', 'user')
    list_filter = ('create_time', 'result_pest', 'model_used')
    search_fields = ('api_response', 'user__username')
    readonly_fields = ('create_time', 'ip_address', 'response_time', 'model_used', 'matching_details')
    date_hierarchy = 'create_time'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'image', 'create_time', 'ip_address')
        }),
        ('识别结果', {
            'fields': ('result_pest', 'confidence', 'matching_details')
        }),
        ('模型信息', {
            'fields': ('model_used', 'response_time')
        }),
        ('API详情', {
            'fields': ('api_response',),
            'classes': ('collapse',)
        })
    )
    
    def matching_details(self, obj):
        """显示匹配详情"""
        if not obj.api_response or not obj.api_response.get('extracted_info'):
            return "无匹配详情"
            
        extracted = obj.api_response.get('extracted_info', {})
        pest_name = extracted.get('pest_name', '')
        
        if obj.result_pest:
            return f"AI识别: {pest_name} → 匹配到: {obj.result_pest.name}"
        return f"AI识别: {pest_name} → 未找到匹配"
    
    matching_details.short_description = "匹配详情"
    
class ModelSelectionAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'success_rate', 'avg_confidence', 'usage_count', 'avg_response_time', 'last_used')
    search_fields = ('model_name',)
    readonly_fields = ('usage_count', 'success_rate', 'avg_confidence', 'avg_response_time', 'last_used')
    
    fieldsets = (
        ('模型信息', {
            'fields': ('model_name', 'usage_count', 'last_used')
        }),
        ('性能统计', {
            'fields': ('success_rate', 'avg_confidence', 'avg_response_time')
        })
    )

admin.site.register(RecognitionHistory, RecognitionHistoryAdmin)
admin.site.register(ModelSelection, ModelSelectionAdmin)
