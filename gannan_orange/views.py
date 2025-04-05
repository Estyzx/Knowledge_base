from weakref import ref
import requests
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.contrib import messages
from django.utils import timezone
import datetime

from User.models import CustomUser
from article.models import PlantingTechArticle

from .forms import VarietyForm, PlantingTechForm, PestForm, SoilTypeForm, ReviewForm
from .models import Variety, PlantingTech, SoilType, Pest, ReviewHistory, Category


# 获取最后审核通过的版本
def get_last_approved_version(model_class, instance_id):
    """
    获取指定内容的最后一个审核通过版本
    :param model_class: 模型类
    :param instance_id: 内容ID
    :return: 审核通过的对象或None
    """
    try:
        # 从审核历史中获取最近一次通过的审核记录
        last_approved_history = ReviewHistory.objects.filter(
            content_type=model_class.__name__.lower(),
            content_id=instance_id,
            action='approve'
        ).order_by('-review_date').first()
        
        if last_approved_history:
            # 获取该版本的对象
            return {
                'id': instance_id,
                'review_date': last_approved_history.review_date,
                'reviewer': last_approved_history.reviewer,
                'comment': last_approved_history.comment
            }
        return None
    except Exception as e:
        print(f"Error getting last approved version: {e}")
        return None

# Create your views here.


class HomePage(TemplateView):
    template_name = 'gannan_orange/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 使用缓存减少API调用，缓存3小时
        weather_data = cache.get('weather_data')
        current_weather = cache.get('current_weather')
        
        if weather_data is None or current_weather is None:
            try:
                # 设置较短的超时时间，避免页面加载阻塞
                url = "https://api.seniverse.com/v3/weather/daily.json?key=SsIcJ_YpHt1dJPr1Q&location=baoding&language=zh-Hans&unit=c&start=0&days=5"
                response = requests.get(url, timeout=1.5)
                url1 = "https://api.seniverse.com/v3/weather/now.json?key=SsIcJ_YpHt1dJPr1Q&location=baoding&language=zh-Hans&unit=c"
                response1 = requests.get(url1, timeout=1.5)
                
                if response.status_code == 200 and response1.status_code == 200:
                    data = response.json()
                    data1 = response1.json()
                    
                    update_data = data['results'][0]['last_update'][:10]
                    humidity = data['results'][0]['daily'][0]['humidity']
                    wind_speed = data['results'][0]['daily'][0]['wind_speed']
                    code_day = data['results'][0]['daily'][0]['code_day']
                    
                    # 存入缓存，有效期3小时
                    weather_data = {
                        'update_data': update_data,
                        'humidity': humidity,
                        'wind_speed': wind_speed,
                        'code_day': code_day,
                        'days': data['results'][0]['daily'],
                    }
                    
                    current_weather = {
                        'temperature': data1['results'][0]['now']['temperature'],
                        'text': data1['results'][0]['now']['text'],
                    }
                    
                    cache.set('weather_data', weather_data, 60*60*3)
                    cache.set('current_weather', current_weather, 60*60*3)
            except Exception as e:
                print(f"Error fetching weather data: {e}")
                
                # 设置默认天气数据，避免页面报错
                weather_data = {
                    'update_data': '暂无数据',
                    'humidity': 'N/A',
                    'wind_speed': 'N/A',
                    'code_day': '99',
                    'days': [],
                }
                current_weather = {
                    'temperature': 'N/A',
                    'text': '暂无数据',
                }
        
        context.update({
            'weather': weather_data,
            'current_weather': current_weather,
            'update_time': weather_data.get('update_data', '暂无数据'),
            'humidity': weather_data.get('humidity', 'N/A'),
            'wind_speed': weather_data.get('wind_speed', 'N/A'),
            'code_day': weather_data.get('code_day', '99'),
            'icon_night': f"{weather_data.get('code_day', '99')}.svg",
            'temperature': current_weather.get('temperature', 'N/A'),
        })
        
        # 使用缓存减少数据库查询
        stats_cache_key = 'home_page_stats'
        home_stats = cache.get(stats_cache_key)
        
        if home_stats is None:
            # 优化所有数据库查询
            try:
                # 减少重复查询，只查询必要数据
                varieties_count = Variety.objects.filter(review_status='approved').count()
                techs_count = PlantingTech.objects.filter(review_status='approved').count()
                user_count = CustomUser.objects.count()
                
                # 仅对管理员提供待审核内容统计
                if self.request.user.is_staff:
                    pending_varieties = Variety.objects.filter(review_status='pending').count()
                    pending_planting_techs = PlantingTech.objects.filter(review_status='pending').count()
                    pending_pests = Pest.objects.filter(review_status='pending').count()
                    pending_soil_types = SoilType.objects.filter(review_status='pending').count()
                    total_pending = pending_varieties + pending_planting_techs + pending_pests + pending_soil_types
                else:
                    pending_varieties = pending_planting_techs = pending_pests = pending_soil_types = 0
                    total_pending = 0
                
                # 使用select_related减少数据库查询
                last_varieties = Variety.objects.filter(
                    review_status='approved'
                ).order_by('-create_time')[:3]
                
                tech_articles = PlantingTechArticle.objects.select_related('author').order_by('-create_time')[:3]
                # 调试输出，可以在开发时使用
                print(f"最新品种: {last_varieties.count()}")
                print(f"最新文章: {tech_articles.count()}")
                
                home_stats = {
                    'total_variety': varieties_count,
                    'tech_count': techs_count,
                    'user_count': user_count,
                    'last_variety': list(last_varieties),
                    'tech_articles': list(tech_articles),
                    'total_pending': total_pending,
                    'pending_varieties': pending_varieties,
                    'pending_planting_techs': pending_planting_techs,
                    'pending_pests': pending_pests,
                    'pending_soil_types': pending_soil_types,
                }
                # 设置缓存，有效期减少为30分钟，方便更新内容
                cache.set(stats_cache_key, home_stats, 60*30)
            except Exception as e:
                print(f"Error preparing home stats: {e}")
                home_stats = get_default_home_stats()
        context.update(home_stats)
        return context


def get_default_home_stats():
    """返回默认的首页统计数据"""
    return {
        'total_variety': 0,
        'tech_count': 0,
        'user_count': 0,
        'last_variety': [],
        'tech_articles': [],
        'total_pending': 0,
        'pending_varieties': 0,
        'pending_planting_techs': 0,
        'pending_pests': 0,
        'pending_soil_types': 0,
    }


class VarietyList(ListView):
    model = Variety
    template_name = 'gannan_orange/variety_list.html'
    paginate_by = 6  # 分页
    def get_queryset(self):
        queryset = Variety.objects.order_by('-create_time')
        # 未登录用户或非管理员/专家只能看到已审核通过的内容
        if not self.request.user.is_authenticated or not (self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)):
            queryset = queryset.filter(review_status='approved')
        # 分类过滤
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        # 搜索过滤
        search_key = self.request.GET.get('q')
        if search_key:
            queryset = queryset.filter(Q(name__icontains=search_key) | Q(description__icontains=search_key))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_key'] = self.request.GET.get('q')
        context['category_id'] = self.request.GET.get('category')
        context['categories'] = Category.objects.all().order_by('name')
        return context

class VarietyDetail(DetailView):
    model = Variety
    template_name = 'gannan_orange/variety_detail.html'
    context_object_name = 'variety'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        obj = get_object_or_404(Variety, id=vid)
        # 检查权限：未审核通过的内容只有管理员和专家可以访问
        if obj.review_status != 'approved':
            if not (self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)):
                return redirect('orange:list')
            # 为管理员和专家显示，标记为未审核状态
            obj.is_pending_review = True
            # 获取最后一个审核通过的版本信息
            obj.last_approved = get_last_approved_version(Variety, obj.id)
        return obj
    
    def get_context_data(self, **kwargs):
        # 调用父类的get_context_data方法
        context = super().get_context_data(**kwargs)
        # 获取HTTP_REFERER，如果没有则使用默认的URL
        referer = self.request.META.get('HTTP_REFERER')
        # 安全地处理referer
        if referer:
            # 如果referer包含'edit'，那么返回列表页面
            if 'edit' in referer:
                referer = reverse('orange:list')
        else:
            # 如果没有referer，则返回列表页面
            referer = reverse('orange:list')
        context['referer'] = referer
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        if user.is_authenticated:
            if user not in self.object.favorite_user.all():
                self.object.favorite_user.add(user)
            else:
                self.object.favorite_user.remove(user)
        return self.get(request, *args, **kwargs)

class VarietyEdit(LoginRequiredMixin, UpdateView):
    model = Variety
    form_class = VarietyForm
    template_name = 'gannan_orange/variety_edit.html'
    context_object_name = 'variety'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        obj = get_object_or_404(Variety, id=vid)
        # 检查权限：未审核通过的内容只有管理员和专家可以访问
        if obj.review_status != 'approved' and not (self.request.user.is_staff or self.request.user.is_expert):
            return redirect('orange:list')
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['review_form'] = ReviewForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'review' in request.POST and request.user.is_staff:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                comment = review_form.cleaned_data['comment']
                # 更新审核状态
                self.object.review_status = 'approved' if action == 'approve' else 'rejected'
                self.object.reviewer = request.user
                self.object.review_comment = comment
                self.object.review_date = timezone.now()
                self.object.save()
                # 创建审核历史记录
                ReviewHistory.objects.create(
                    content_type='variety',
                    content_id=self.object.id,
                    reviewer=request.user,
                    action=action,
                    comment=comment
                )
                return redirect('orange:detail', id=self.object.id)
        else:
            # 保存表单前记录当前审核状态
            old_review_status = self.object.review_status
            response = super().post(request, *args, **kwargs)
            # 如果审核状态从已通过变为待审核，显示提示信息
            if old_review_status == 'approved' and self.object.review_status == 'pending':
                messages.warning(request, '内容已被修改，需要重新审核才能生效')
            return response
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('orange:detail', kwargs={'id': self.object.id})
    
    def form_invalid(self, form):
        # 确保表单错误信息正确传递到模板
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    pass
                else:
                    pass
        return super().form_invalid(form)

class VarietyCreate(CreateView):
    model = Variety
    form_class = VarietyForm
    template_name = 'gannan_orange/variety_create.html'
    
    def get_success_url(self):
        return reverse_lazy('orange:detail', kwargs={'id': self.object.id})

    def form_invalid(self, form):
        # 确保表单错误信息正确传递到模板
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    pass
                else:
                    pass
        return super().form_invalid(form)

class VarietyDelete(DeleteView):
    model = Variety
    success_url = reverse_lazy('orange:list')
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(Variety, id=vid)

class PlantingTechList(ListView):
    model = PlantingTech
    template_name = 'gannan_orange/planting_tech_list.html'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = PlantingTech.objects.order_by('-create_time')
        # 只显示审核通过的内容，管理员和专家可以看到所有内容
        if not self.request.user.is_authenticated or not (self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)):
            queryset = queryset.filter(review_status='approved')
        search_key = self.request.GET.get('q')
        if search_key:
            queryset = queryset.filter(Q(name__icontains=search_key) | Q(description__icontains=search_key)).order_by(
                '-create_time')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_key'] = self.request.GET.get('q')
        return context

class PlantingTechDetail(DetailView):
    model = PlantingTech
    template_name = 'gannan_orange/planting_tech_detail.html'
    context_object_name = 'tech'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        obj = get_object_or_404(PlantingTech, id=vid)
        # 检查权限：未审核通过的内容只有管理员和专家可以访问
        if obj.review_status != 'approved':
            if not (self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)):
                return redirect('orange:tech_list')
            # 为管理员和专家显示，标记为未审核状态
            obj.is_pending_review = True
            # 获取最后一个审核通过的版本信息
            obj.last_approved = get_last_approved_version(PlantingTech, obj.id)
        return obj
    
    def get_context_data(self, **kwargs):
        # 调用父类的get_context_data方法
        context = super().get_context_data(**kwargs)
        # 获取HTTP_REFERER，如果没有则使用默认的URL:
        referer = self.request.META.get('HTTP_REFERER')
        # 安全地处理referer
        if referer:
            # 如果referer包含'edit'，那么返回列表页面
            if 'edit' in referer:
                referer = reverse('orange:tech_list')
        else:
            # 如果没有referer，则返回列表页面
            referer = reverse('orange:tech_list')
        context['referer'] = referer
        return context

class PlantingTechEdit(LoginRequiredMixin, UpdateView):
    model = PlantingTech
    template_name = 'gannan_orange/planting_tech_edit.html'
    context_object_name = 'plantingtech'
    form_class = PlantingTechForm
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(PlantingTech, id=vid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['review_form'] = ReviewForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'review' in request.POST and request.user.is_staff:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                comment = review_form.cleaned_data['comment']
                # 更新审核状态
                self.object.review_status = 'approved' if action == 'approve' else 'rejected'
                self.object.reviewer = request.user
                self.object.review_comment = comment
                self.object.review_date = timezone.now()
                self.object.save()
                # 创建审核历史记录
                ReviewHistory.objects.create(
                    content_type='planting_tech',
                    content_id=self.object.id,
                    reviewer=request.user,
                    action=action,
                    comment=comment
                )
                messages.success(request, '审核操作已完成')
                return redirect('orange:tech_detail', id=self.object.id)
        else:
            # 保存表单前记录当前审核状态
            old_review_status = self.object.review_status
            response = super().post(request, *args, **kwargs)
            # 如果审核状态从已通过变为待审核，显示提示信息
            if old_review_status == 'approved' and self.object.review_status == 'pending':
                messages.warning(request, '内容已被修改，需要重新审核才能生效')
            return response
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy("orange:tech_detail", kwargs={'id': self.object.id})

class PlantingTechDelete(DeleteView):
    model = PlantingTech
    success_url = reverse_lazy('orange:tech_list')
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(PlantingTech, id=vid)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)

class PlantingTechCreate(CreateView):
    template_name = 'gannan_orange/planting_tech_creat.html'
    fields = ['name', 'description']
    
    def get_success_url(self):
        return reverse_lazy('orange:detail', kwargs={'id': self.object.id})
    
    def form_invalid(self, form):
        # 确保表单错误信息正确传递到模板
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    pass
                else:
                    pass
        return super().form_invalid(form)

class SoilTypeDetail(DetailView):
    model = SoilType
    template_name = 'gannan_orange/soil_type_detail.html'
    context_object_name = 'soil'
    
    def get_object(self, queryset=None):
        # 获取URL中的id参数
        vid = self.kwargs.get('id')
        # 获取对象
        obj = get_object_or_404(SoilType, id=vid)
        # 检查权限：未审核通过的内容只有管理员和专家可以访问
        if obj.review_status != 'approved':
            if not (self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)):
                return redirect('orange:soil_list')
            # 为管理员和专家显示，标记为未审核状态
            obj.is_pending_review = True
            # 获取最后一个审核通过的版本信息
            obj.last_approved = get_last_approved_version(SoilType, obj.id)
        return obj
    
    def get_context_data(self, **kwargs):
        # 调用父类的get_context_data方法
        context = super().get_context_data(**kwargs)
        # 获取HTTP_REFERER，如果没有则使用默认的URL
        referer = self.request.META.get('HTTP_REFERER')
        # 安全地处理referer
        if referer:
            # 如果referer包含'edit'，那么返回列表页面
            if 'edit' in referer:
                referer = reverse('orange:soil_list')
        else:
            # 如果没有referer，则返回列表页面
            referer = reverse('orange:soil_list')
        context['referer'] = referer
        return context

class SoilTypeEdit(LoginRequiredMixin, UpdateView):
    model = SoilType
    form_class = SoilTypeForm
    template_name = 'gannan_orange/soil_type_edit.html'
    context_object_name = 'soil'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(SoilType, id=vid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['review_form'] = ReviewForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'review' in request.POST and request.user.is_staff:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                comment = review_form.cleaned_data['comment']
                # 更新审核状态
                self.object.review_status = 'approved' if action == 'approve' else 'rejected'
                self.object.reviewer = request.user
                self.object.review_comment = comment
                self.object.review_date = timezone.now()
                self.object.save()
                # 创建审核历史记录
                ReviewHistory.objects.create(
                    content_type='soil_type',
                    content_id=self.object.id,
                    reviewer=request.user,
                    action=action,
                    comment=comment
                )
                messages.success(request, '审核操作已完成')
                return redirect('orange:soil_detail', id=self.object.id)
        else:
            # 保存表单前记录当前审核状态
            old_review_status = self.object.review_status
            response = super().post(request, *args, **kwargs)
            # 如果审核状态从已通过变为待审核，显示提示信息
            if old_review_status == 'approved' and self.object.review_status == 'pending':
                messages.warning(request, '内容已被修改，需要重新审核才能生效')
            return response
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('orange:soil_detail', kwargs={'id': self.object.id})

class SoilTypeList(ListView):
    model = SoilType
    template_name = 'gannan_orange/soil_type_list.html'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = SoilType.objects.order_by('-create_time')
        # 只显示审核通过的内容，管理员和专家可以看到所有内容
        if not self.request.user.is_authenticated or not (self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)):
            queryset = queryset.filter(review_status='approved')
        search_key = self.request.GET.get('q')
        if search_key:
            queryset = queryset.filter(Q(name__icontains=search_key) | Q(description__icontains=search_key)).order_by(
                '-create_time')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_key'] = self.request.GET.get('q')
        return context

class SoilTypeDelete(DeleteView):
    model = SoilType
    success_url = reverse_lazy('orange:soil_list')
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(SoilType, id=vid)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)

class PestDetail(DetailView):
    model = Pest
    template_name = 'gannan_orange/pest_detail.html'
    context_object_name = 'pest'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        pest = get_object_or_404(Pest, id=vid)
        # 检查审核状态和用户权限
        if pest.review_status != 'approved':
            if not (self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)):
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied('该内容尚未通过审核，暂时无法访问。')
            # 为管理员和专家显示，标记为未审核状态
            pest.is_pending_review = True
            # 获取最后一个审核通过的版本信息
            pest.last_approved = get_last_approved_version(Pest, pest.id)
        return pest
    
    def get_context_data(self, **kwargs):
        # 调用父类的get_context_data方法
        context = super().get_context_data(**kwargs)
        # 获取HTTP_REFERER，如果没有则使用默认的URL
        referer = self.request.META.get('HTTP_REFERER')
        # 安全地处理referer
        if referer:
            # 如果referer包含'edit'，那么返回列表页面
            if 'edit' in referer:
                referer = reverse('orange:pest_list')
        else:
            # 如果没有referer，则返回列表页面
            referer = reverse('orange:pest_list')
        context['referer'] = referer
        return context

class PestList(ListView):
    model = Pest
    template_name = 'gannan_orange/pest_list.html'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = Pest.objects.filter(review_status='approved').order_by('-create_time')
        # 只显示审核通过的内容，管理员和专家可以看到所有内容
        if not self.request.user.is_authenticated or not (self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)):
            queryset = queryset.filter(review_status='approved')
        search_key = self.request.GET.get('q')
        if search_key:
            queryset = queryset.filter(Q(name__icontains=search_key) | Q(description__icontains=search_key)).order_by(
                '-create_time')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_key'] = self.request.GET.get('q')
        return context

class PestEdit(LoginRequiredMixin, UpdateView):
    model = Pest
    form_class = PestForm
    template_name = 'gannan_orange/pest_edit.html'
    context_object_name = 'edit'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(Pest, id=vid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['review_form'] = ReviewForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'review' in request.POST and request.user.is_staff:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                comment = review_form.cleaned_data['comment']
                # 更新审核状态
                self.object.review_status = 'approved' if action == 'approve' else 'rejected'
                self.object.reviewer = request.user
                self.object.review_comment = comment
                self.object.review_date = timezone.now()
                self.object.save()
                # 创建审核历史记录
                ReviewHistory.objects.create(
                    content_type='pest',
                    content_id=self.object.id,
                    reviewer=request.user,
                    action=action,
                    comment=comment
                )
                messages.success(request, '审核操作已完成')
                return redirect('orange:pest_detail', id=self.object.id)
        else:
            # 保存表单前记录当前审核状态
            old_review_status = self.object.review_status
            response = super().post(request, *args, **kwargs)
            # 如果审核状态从已通过变为待审核，显示提示信息
            if old_review_status == 'approved' and self.object.review_status == 'pending':
                messages.warning(request, '内容已被修改，需要重新审核才能生效')
            return response
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('orange:pest_detail', kwargs={'id': self.object.id})

class PestDelete(DeleteView):
    model = Pest
    success_url = reverse_lazy('orange:pest_list')
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(Pest, id=vid)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)

class FavoriteVariety(ListView):
    template_name = 'gannan_orange/favorite_variety.html'
    context_object_name = 'favorite_varieties'
    
    def get_queryset(self):
        queryset = self.request.user.favorite_varieties.all()
        search_key = self.request.GET.get('q')
        if search_key:
            queryset = queryset.filter(Q(name__icontains=search_key) | Q(description__icontains=search_key)).order_by(
                '-create_time')
        return queryset

# 专家审核基类
class ExpertReviewMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        return redirect('orange:home')

# 待审核内容列表
class PendingReviewListView(ExpertReviewMixin, TemplateView):
    template_name = 'gannan_orange/pending_review_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取各类型的待审核内容
        context['pending_varieties'] = Variety.objects.filter(review_status='pending').order_by('-create_time')
        context['pending_planting_techs'] = PlantingTech.objects.filter(review_status='pending').order_by('-create_time')
        context['pending_pests'] = Pest.objects.filter(review_status='pending').order_by('-create_time')
        context['pending_soil_types'] = SoilType.objects.filter(review_status='pending').order_by('-create_time')
        return context

# 审核历史记录
class ReviewHistoryListView(ExpertReviewMixin, ListView):
    model = ReviewHistory
    template_name = 'gannan_orange/review_history.html'
    context_object_name = 'review_histories'
    paginate_by = 20
    
    def get_queryset(self):
        return ReviewHistory.objects.filter(reviewer=self.request.user).order_by('-review_date')

# 品种审核视图
class VarietyReviewView(ExpertReviewMixin, UpdateView):
    model = Variety
    template_name = 'gannan_orange/review_form.html'
    form_class = ReviewForm
    context_object_name = 'content'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(Variety, id=vid)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ReviewForm是普通Form而不是ModelForm
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_type'] = '品种'
        return context
    
    def form_valid(self, form):
        variety = self.object
        action = form.cleaned_data['action']
        comment = form.cleaned_data['comment']
        
        # 更新审核状态
        if action == 'approve':
            variety.review_status = 'approved'
        else:
            variety.review_status = 'rejected'
            # 如果是拒绝，可以添加快捷恢复到上一个通过的版本的功能
            messages.warning(self.request, f'您已拒绝"{variety.name}"的内容修改。该内容将不会对普通用户可见，直到再次审核通过。')
        
        variety.reviewer = self.request.user
        variety.review_comment = comment
        variety.review_date = timezone.now()
        variety.save()
        
        # 创建审核历史记录
        ReviewHistory.objects.create(
            content_type='variety',
            content_id=variety.id,
            reviewer=self.request.user,
            action=action,
            comment=comment
        )
        
        messages.success(self.request, f'"{variety.name}" 审核操作已完成')
        return redirect('orange:pending_review')

# 种植技术审核视图
class PlantingTechReviewView(ExpertReviewMixin, UpdateView):
    model = PlantingTech
    template_name = 'gannan_orange/review_form.html'
    form_class = ReviewForm
    context_object_name = 'content'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(PlantingTech, id=vid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_type'] = '种植技术'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ReviewForm是普通Form而不是ModelForm
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs
    
    def form_valid(self, form):
        tech = self.object
        action = form.cleaned_data['action']
        comment = form.cleaned_data['comment']
        
        # 更新审核状态
        if action == 'approve':
            tech.review_status = 'approved'
        else:
            tech.review_status = 'rejected'
            # 如果是拒绝，可以添加快捷恢复到上一个通过的版本的功能
            messages.warning(self.request, f'您已拒绝"{tech.name}"的内容修改。该内容将不会对普通用户可见，直到再次审核通过。')
        
        tech.reviewer = self.request.user
        tech.review_comment = comment
        tech.review_date = timezone.now()
        tech.save()
        
        # 创建审核历史记录
        ReviewHistory.objects.create(
            content_type='planting_tech',
            content_id=tech.id,
            reviewer=self.request.user,
            action=action,
            comment=comment
        )
        
        messages.success(self.request, f'"{tech.name}" 审核操作已完成')
        return redirect('orange:pending_review')

# 病虫害审核视图
class PestReviewView(ExpertReviewMixin, UpdateView):
    model = Pest
    template_name = 'gannan_orange/review_form.html'
    form_class = ReviewForm
    context_object_name = 'content'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(Pest, id=vid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_type'] = '病虫害'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ReviewForm是普通Form而不是ModelForm
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs
    
    def form_valid(self, form):
        pest = self.object
        action = form.cleaned_data['action']
        comment = form.cleaned_data['comment']
        
        # 更新审核状态
        if action == 'approve':
            pest.review_status = 'approved'
        else:
            pest.review_status = 'rejected'
            # 如果是拒绝，可以添加快捷恢复到上一个通过的版本的功能
            messages.warning(self.request, f'您已拒绝"{pest.name}"的内容修改。该内容将不会对普通用户可见，直到再次审核通过。')
        
        pest.reviewer = self.request.user
        pest.review_comment = comment
        pest.review_date = timezone.now()
        pest.save()
        
        # 创建审核历史记录
        ReviewHistory.objects.create(
            content_type='pest',
            content_id=pest.id,
            reviewer=self.request.user,
            action=action,
            comment=comment
        )
        
        messages.success(self.request, f'"{pest.name}" 审核操作已完成')
        return redirect('orange:pending_review')

# 土壤类型审核视图
class SoilTypeReviewView(ExpertReviewMixin, UpdateView):
    model = SoilType
    template_name = 'gannan_orange/review_form.html'
    form_class = ReviewForm
    context_object_name = 'content'
    
    def get_object(self, queryset=None):
        vid = self.kwargs.get('id')
        return get_object_or_404(SoilType, id=vid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_type'] = '土壤类型'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ReviewForm是普通Form而不是ModelForm
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs
    
    def form_valid(self, form):
        soil = self.object
        action = form.cleaned_data['action']
        comment = form.cleaned_data['comment']
        
        # 更新审核状态
        if action == 'approve':
            soil.review_status = 'approved'
        else:
            soil.review_status = 'rejected'
            # 如果是拒绝，可以添加快捷恢复到上一个通过的版本的功能
            messages.warning(self.request, f'您已拒绝"{soil.name}"的内容修改。该内容将不会对普通用户可见，直到再次审核通过。')
        
        soil.reviewer = self.request.user
        soil.review_comment = comment
        soil.review_date = timezone.now()
        soil.save()
        
        # 创建审核历史记录
        ReviewHistory.objects.create(
            content_type='soil_type',
            content_id=soil.id,
            reviewer=self.request.user,
            action=action,
            comment=comment
        )
        
        messages.success(self.request, f'"{soil.name}" 审核操作已完成')
        return redirect('orange:pending_review')



# 创建一个API视图函数来异步获取天气数据
def weather_api(request):
    from django.http import JsonResponse
    
    # 使用缓存减少API调用，缓存3小时
    weather_data = cache.get('weather_data')
    current_weather = cache.get('current_weather')
    
    if weather_data is None or current_weather is None:
        try:
            # 设置较短的超时时间，避免页面加载阻塞
            url = "https://api.seniverse.com/v3/weather/daily.json?key=SsIcJ_YpHt1dJPr1Q&location=ganzhou&language=zh-Hans&unit=c&start=0&days=5"
            response = requests.get(url, timeout=2.0)
            url1 = "https://api.seniverse.com/v3/weather/now.json?key=SsIcJ_YpHt1dJPr1Q&location=ganzhou&language=zh-Hans&unit=c"
            response1 = requests.get(url1, timeout=2.0)
            
            if response.status_code == 200 and response1.status_code == 200:
                data = response.json()
                data1 = response1.json()
                
                update_data = data['results'][0]['last_update'][:10]
                humidity = data['results'][0]['daily'][0]['humidity']
                wind_speed = data['results'][0]['daily'][0]['wind_speed']
                code_day = data['results'][0]['daily'][0]['code_day']
                
                # 存入缓存，有效期3小时
                weather_data = {
                    'update_data': update_data,
                    'humidity': humidity,
                    'wind_speed': wind_speed,
                    'code_day': code_day,
                    'days': data['results'][0]['daily'],
                }
                
                current_weather = {
                    'temperature': data1['results'][0]['now']['temperature'],
                    'text': data1['results'][0]['now']['text'],
                }
                
                cache.set('weather_data', weather_data, 60*60*3)
                cache.set('current_weather', current_weather, 60*60*3)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '天气API响应错误'
                })
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'获取天气数据失败: {str(e)}',
                'weather_data': {'update_data': '暂无数据', 'humidity': 'N/A', 'wind_speed': 'N/A', 'code_day': '99', 'days': []},
                'current_weather': {'temperature': 'N/A', 'text': '暂无数据'},
            })
    
    return JsonResponse({
        'status': 'success',
        'weather_data': weather_data,
        'current_weather': current_weather
    })
