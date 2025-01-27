from django import forms
from .models import Variety, PlantingTech, Pest


class VarietyForm(forms.ModelForm):
    class Meta:
        model = Variety
        fields = ['name', 'description', 'planting_tech', 'pest']

    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '品种名称'}),
        label='品种名称'
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '品种描述'}),
        label='品种描述',
        required=False
    )

    # 使用 SelectMultiple 渲染 ManyToMany 字段，显示为多选下拉框
    planting_tech = forms.ModelMultipleChoiceField(
        queryset=PlantingTech.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),  # size 决定显示多少项
        required=False,
        label='种植技术'
    )

    pest = forms.ModelMultipleChoiceField(
        queryset=Pest.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),  # size 决定显示多少项
        required=False,
        label='病虫害'
    )
