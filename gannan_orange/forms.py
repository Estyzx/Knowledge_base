from django import forms
from .models import Variety, PlantingTech, Pest


class VarietyForm(forms.ModelForm):
    name = forms.CharField(
        label='品种名称',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


    class Meta:
        model = Variety
        fields = '__all__'

