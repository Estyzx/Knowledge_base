from django import forms
from django.contrib.auth.forms import UserCreationForm

from User.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='用户名',max_length=50)
    phone = forms.CharField(label='手机号', max_length=11)
    password1 = forms.CharField(label='密码',)
    password2 = forms.CharField(label='确认密码')
    role = forms.ChoiceField(label='角色',choices=[('farmer','农民'),('expert','专家')])

    class Meta:
        model = CustomUser
        fields = ['username','password1','password2','phone','role']


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'location', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': '用户名',
            'phone': '手机号',
            'location': '所在地区',
            'email': '电子邮箱',
        }