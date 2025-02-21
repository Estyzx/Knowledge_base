from django import forms
from .models import PlantingTechArticle,Comment

class PlantingTechArticleForm(forms.ModelForm):
    class Meta:
        model = PlantingTechArticle
        fields = ['title', 'content']  # 指定需要的字段
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # 用户只需要填写评论内容
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
