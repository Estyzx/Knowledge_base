from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max

from .forms import CustomUserCreationForm
from .models import CustomUser
from gannan_orange.models import Variety
from article.models import PlantingTechArticle, UserArticleView


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        # 登录成功后重定向到的页面
        return reverse_lazy('orange:home')

    def form_invalid(self, form):
        return super().form_invalid(form)
        
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomRegisterView(CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('user:login')

    form_class = CustomUserCreationForm
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@login_required
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    
    # 检查当前用户是否是请求的用户
    is_self = request.user.pk == user.pk
    
    # 获取用户收藏的品种
    favorite_varieties = Variety.objects.filter(favorite_user=user)
    
    # 获取用户浏览历史，确保每篇文章只显示一次
    # 使用values和annotate获取每篇文章的最近浏览时间
    recent_views = UserArticleView.objects.filter(user=user)\
        .values('article')\
        .annotate(latest_view=Max('view_time'))\
        .order_by('-latest_view')[:5]
    
    # 获取文章对象
    article_ids = [view['article'] for view in recent_views]
    viewed_articles = []
    for article_id in article_ids:
        try:
            article = PlantingTechArticle.objects.get(id=article_id)
            viewed_articles.append(article)
        except PlantingTechArticle.DoesNotExist:
            continue
    
    # 如果用户是专家，获取他们的专家资料（如果有）
    expert_profile = None
    if hasattr(user, 'expert_profile'):
        expert_profile = user.expert_profile
    
    context = {
        'user_profile': user,
        'is_self': is_self,
        'favorite_varieties': favorite_varieties,
        'viewed_articles': viewed_articles,
        'expert_profile': expert_profile,
    }
    
    return render(request, 'users/user_detail.html', context)


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'users/user_edit.html'
    fields = ['username', 'phone', 'location', 'email']
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        messages.success(self.request, '个人信息更新成功！')
        return reverse_lazy('user:user_detail', kwargs={'pk': self.request.user.pk})
