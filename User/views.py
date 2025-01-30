from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import CreateView
from .forms import CustomUserCreationForm


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        # 登录成功后重定向到的页面
        return reverse_lazy('orange:home')

    def form_invalid(self, form):
        messages.error(self.request, "用户名或密码错误")
        return super().form_invalid(form)


class CustomRegisterView(CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('user:login')

    form_class = CustomUserCreationForm

