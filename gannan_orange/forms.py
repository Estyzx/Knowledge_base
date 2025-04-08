from django import forms
from .models import Variety, PlantingTech, Pest, SoilType, ReviewHistory


class VarietyForm(forms.ModelForm):
    name = forms.CharField(
        label='品种名称',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Variety
        exclude = ['review_status', 'reviewer', 'review_comment', 'review_date']
        

class PlantingTechForm(forms.ModelForm):
    class Meta:
        model = PlantingTech
        exclude = ['review_status', 'reviewer', 'review_comment', 'review_date']


class PestForm(forms.ModelForm):
    class Meta:
        model = Pest
        exclude = ['review_status', 'reviewer', 'review_comment', 'review_date']


class SoilTypeForm(forms.ModelForm):
    class Meta:
        model = SoilType
        exclude = ['review_status', 'reviewer', 'review_comment', 'review_date']


class ReviewForm(forms.ModelForm):
    REVIEW_ACTION_CHOICES = [
        ('approve', '通过'),
        ('reject', '拒绝'),
    ]
    
    action = forms.ChoiceField(
        label='审核操作',
        choices=REVIEW_ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    comment = forms.CharField(
        label='审核意见',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': '请输入审核意见，拒绝时建议填写拒绝原因'
        })
    )
    
    def clean(self):
        # 获取已清理的数据，只在需要时检查
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        
        # 只有在选择拒绝操作时才检查评论
        if action == 'reject':
            comment = cleaned_data.get('comment', '').strip()
            if not comment:
                self.add_error('comment', '拒绝时请填写审核意见，以便内容提交者了解原因并进行修改')
        
        return cleaned_data
        
    class Meta:
        model = ReviewHistory
        fields = ['action', 'comment']
        
    # 修复表单实例化问题，添加正确的__init__方法
    def __init__(self, *args, **kwargs):
        # 简化参数提取，减少处理时间
        instance = kwargs.pop('instance', None)
        content_object = kwargs.pop('content_object', None)
        content_type = kwargs.pop('content_type', None)
        object_id = kwargs.pop('object_id', None)
        
        # 调用父类的__init__方法
        super().__init__(*args, **kwargs)
        
        # 高效地处理实例
        if instance:
            self.instance = instance
            
        # 合并内容对象设置，减少条件判断
        if content_object or (content_type and object_id):
            if content_object:
                self.content_object = content_object
            if content_type:
                self.content_type = content_type
            if object_id:
                self.object_id = object_id
        
        # 一次性设置所有字段属性，减少DOM操作
        self.fields['action'].widget.attrs.update({
            'data-priority': 'high',
            'autocomplete': 'off',
            'onclick': 'this.form.classList.remove("was-validated")'  # 点击时重置验证，避免重复动画
        })
        
        # 优化文本区域渲染，禁用不必要的过渡和动画
        self.fields['comment'].widget.attrs.update({
            'data-priority': 'medium',
            'class': 'form-control no-animation',  # 使用无动画类
            'rows': '4',
            'style': 'transition:none; animation:none;',  # 直接在元素上禁用过渡和动画
            'placeholder': '请输入审核意见，拒绝时建议填写拒绝原因',
            'onblur': 'this.classList.remove("animate-shake")'  # 防止抖动动画残留
        })

