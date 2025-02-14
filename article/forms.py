from django import forms
from .models import PlantingTechArticle

class PlantingTechArticleForm(forms.ModelForm):
    class Meta:
        model = PlantingTechArticle
        fields = ['title', 'content']  # 指定需要的字段
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }