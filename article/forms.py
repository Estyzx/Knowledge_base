from django import forms
from .models import PlantingTechArticle, Comment, Category, Tag

class PlantingTechArticleForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select mb-3'}),
        required=False,
        label='分类'
    )
    tags = forms.CharField(
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2-tags',
            'data-placeholder': '选择或创建标签',
            'multiple': 'multiple'
        }),
        required=False,
        label='标签'
    )
    
    def clean_tags(self):
        tags_data = self.cleaned_data.get('tags', [])
        if isinstance(tags_data, str):
            tags_data = tags_data.split(',')
        
        tags = []
        for tag_name in tags_data:
            tag_name = tag_name.strip()
            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
        return tags
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # 如果是编辑现有文章，预先选中已有标签
            self.initial['tags'] = self.instance.tags.all()
    
    class Meta:
        model = PlantingTechArticle
        fields = ['title', 'content', 'category', 'tags']  # 添加分类和标签字段
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # 用户只需要填写评论内容
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
