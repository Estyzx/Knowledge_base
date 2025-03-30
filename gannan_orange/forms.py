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


class ReviewForm(forms.Form):
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
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )

