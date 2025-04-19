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


# 获取内容最后一个审核通过的版本
def get_last_approved_version(model_class, instance_id):
    """获取指定内容的最后一个审核通过版本"""
    try:
        last_approved_history = ReviewHistory.objects.filter(
            content_type=model_class.__name__.lower(),
            content_id=instance_id,
            action='approve'
        ).order_by('-review_date').first()
        
        if last_approved_history:
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


class HomePage(TemplateView):
    template_name = 'gannan_orange/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 天气数据获取 - 使用缓存提高性能
        weather_data = cache.get('weather_data')
        current_weather = cache.get('current_weather')
        
        if weather_data is None or current_weather is None:
            try:
                weather_result = self.fetch_weather_data()
                if weather_result:
                    weather_data, current_weather = weather_result
                    # 3小时缓存
                    cache.set('weather_data', weather_data, 60*60*3)
                    cache.set('current_weather', current_weather, 60*60*3)
                else:
                    weather_data, current_weather = self.get_default_weather()
            except Exception as e:
                print(f"Error fetching weather data: {e}")
                weather_data, current_weather = self.get_default_weather()
        
        # 只添加必要的天气数据
        context.update({
            'weather': weather_data,
            'current_weather': current_weather,
        })
        
        # 首页统计数据缓存
        stats_cache_key = 'home_page_stats'
        home_stats = cache.get(stats_cache_key)
        
        if home_stats is None:
            try:
                # 统计数据查询优化
                varieties_count = Variety.objects.filter(review_status='approved').count()
                techs_count = PlantingTech.objects.filter(review_status='approved').count()
                user_count = CustomUser.objects.count()
                
                # 管理员查看待审核内容
                if self.request.user.is_staff:
                    pending_varieties = Variety.objects.filter(review_status='pending').count()
                    pending_planting_techs = PlantingTech.objects.filter(review_status='pending').count()
                    pending_pests = Pest.objects.filter(review_status='pending').count()
                    pending_soil_types = SoilType.objects.filter(review_status='pending').count()
                    total_pending = pending_varieties + pending_planting_techs + pending_pests + pending_soil_types
                else:
                    pending_varieties = pending_planting_techs = pending_pests = pending_soil_types = 0
                    total_pending = 0
                
                # 最新内容推荐
                last_varieties = Variety.objects.filter(
                    review_status='approved'
                ).order_by('-create_time')[:3]
                
                tech_articles = PlantingTechArticle.objects.select_related('author').order_by('-create_time')[:3]
                
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
                # 30分钟缓存以保持数据更新
                cache.set(stats_cache_key, home_stats, 60*30)
            except Exception as e:
                print(f"Error preparing home stats: {e}")
                home_stats = get_default_home_stats()
        context.update(home_stats)
        return context
    
    def fetch_weather_data(self):
        """并行获取天气数据以提高性能"""
        try:
            timeout = 2.0
            location = "baoding"
            api_key = "SsIcJ_YpHt1dJPr1Q"
            
            url = f"https://api.seniverse.com/v3/weather/daily.json?key={api_key}&location={location}&language=zh-Hans&unit=c&start=0&days=5"
            url_now = f"https://api.seniverse.com/v3/weather/now.json?key={api_key}&location={location}&language=zh-Hans&unit=c"
            
            # 并行请求提高效率
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_forecast = executor.submit(requests.get, url, timeout=timeout)
                future_now = executor.submit(requests.get, url_now, timeout=timeout)
                
                response = future_forecast.result()
                response_now = future_now.result()
            
            if response.status_code == 200 and response_now.status_code == 200:
                data = response.json()
                data_now = response_now.json()
                
                daily = data['results'][0]['daily'][0]
                now = data_now['results'][0]['now']
                
                weather_data = {
                    'update_data': data['results'][0]['last_update'][:10],
                    'humidity': daily['humidity'],
                    'wind_speed': daily['wind_speed'],
                    'code_day': daily['code_day'],
                    'days': data['results'][0]['daily'],
                }
                
                current_weather = {
                    'temperature': now['temperature'],
                    'text': now['text'],
                }
                
                return weather_data, current_weather
            return None
        except Exception as e:
            print(f"Error in fetch_weather_data: {e}")
            return None
    
    def get_default_weather(self):
        """默认天气数据 - 防止API故障"""
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
        return weather_data, current_weather


def get_default_home_stats():
    """首页默认统计数据 - 防止查询错误"""
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
        if (referer):
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
        # 修改：对所有管理员和专家用户提供审核表单，而不仅是管理员
        if self.request.user.is_staff or getattr(self.request.user, 'is_expert', False):
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
                create_review_history(
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
        # 修改：对所有管理员和专家用户提供审核表单，而不仅是管理员
        if self.request.user.is_staff or getattr(self.request.user, 'is_expert', False):
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
                create_review_history(
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
        # 修改：对所有管理员和专家用户提供审核表单，而不仅是管理员
        if self.request.user.is_staff or getattr(self.request.user, 'is_expert', False):
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
                create_review_history(
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
        # 修改：对所有管理员和专家用户提供审核表单，而不仅是管理员
        if self.request.user.is_staff or getattr(self.request.user, 'is_expert', False):
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
                create_review_history(
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
    template_name = 'gannan_orange/review_history.html'
    context_object_name = 'review_histories'
    paginate_by = 10
    
    def get_queryset(self):
        histories = ReviewHistory.objects.select_related('reviewer').order_by('-review_date')
        
        # 尝试为每条历史记录添加内容名称（如果数据库中已有该字段）
        for history in histories:
            try:
                # 获取对应的内容对象
                content_object = self.get_content_object(history.content_type, history.content_id)
                if content_object and hasattr(content_object, 'name'):
                    # 使用安全的方式设置内容名称
                    try:
                        if hasattr(history, 'content_name'):
                            if not history.content_name:  # 如果字段存在但为空
                                history.content_name = content_object.name
                        else:
                            # 字段不存在时，我们使用一个临时属性（不会保存到数据库）
                            history.temp_content_name = content_object.name
                    except Exception as e:
                        print(f"设置内容名称时出错: {e}")
            except Exception as e:
                print(f"获取内容对象时出错: {e}")
                
        return histories
    
    def get_content_object(self, content_type, content_id):
        """获取对应的内容对象"""
        model_map = {
            'variety': Variety,
            'planting_tech': PlantingTech,
            'pest': Pest,
            'soil_type': SoilType,
        }
        
        if content_type in model_map:
            Model = model_map[content_type]
            try:
                return Model.objects.get(id=content_id)
            except Model.DoesNotExist:
                return None
        return None

# 在 ExpertReviewMixin 中添加更多检查
class ExpertReviewMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        # 检查用户是否有审核权限(管理员或专家)
        return self.request.user.is_staff or getattr(self.request.user, 'is_expert', False)
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有审核权限')
        return redirect('orange:home')

# 统一审核功能基类
class BaseReviewView(ExpertReviewMixin, UpdateView):
    template_name = 'gannan_orange/review_form.html'
    form_class = ReviewForm
    
    def get_content_type_display(self):
        """返回内容类型的中文显示名称"""
        raise NotImplementedError("Subclass must implement this method")
    
    def get_success_url(self):
        return reverse('orange:pending_review')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content'] = self.object
        context['content_type'] = self.get_content_type_display()
        return context
    
    def form_valid(self, form):
        obj = self.object
        action = form.cleaned_data['action']
        comment = form.cleaned_data['comment']
        
        # 检查操作是否合理
        if action == 'reject' and not comment:
            messages.error(self.request, '拒绝操作必须填写审核意见')
            return self.form_invalid(form)
        
        # 更新审核状态
        if action == 'approve':
            obj.review_status = 'approved'
            success_message = f'"{obj.name}" 审核已通过'
        else:
            obj.review_status = 'rejected'
            success_message = f'"{obj.name}" 已被拒绝'
        
        obj.reviewer = self.request.user
        obj.review_comment = comment
        obj.review_date = timezone.now()
        obj.save()
        
        # 记录审核历史
        self.create_review_history(action, comment)
        
        messages.success(self.request, success_message)
        return redirect(self.get_success_url())
    
    def create_review_history(self, action, comment):
        """创建审核历史记录"""
        create_review_history(
            content_type=self.get_content_type(),
            content_id=self.object.id,
            reviewer=self.request.user,
            action=action,
            comment=comment,
            content_name=self.object.name  # 添加内容名称
        )
    
    def get_content_type(self):
        """返回内容类型的代码"""
        raise NotImplementedError("Subclass must implement this method")

# 品种审核视图
class VarietyReviewView(BaseReviewView):
    model = Variety
    pk_url_kwarg = 'id'
    
    def get_content_type_display(self):
        return '品种'
    
    def get_content_type(self):
        return 'variety'

# 种植技术审核视图
class PlantingTechReviewView(BaseReviewView):
    model = PlantingTech
    pk_url_kwarg = 'id'
    
    def get_content_type_display(self):
        return '种植技术'
    
    def get_content_type(self):
        return 'planting_tech'

# 病虫害审核视图
class PestReviewView(BaseReviewView):
    model = Pest
    pk_url_kwarg = 'id'
    
    def get_content_type_display(self):
        return '病虫害'
    
    def get_content_type(self):
        return 'pest'

# 土壤类型审核视图
class SoilTypeReviewView(BaseReviewView):
    model = SoilType
    pk_url_kwarg = 'id'
    
    def get_content_type_display(self):
        return '土壤类型'
    
    def get_content_type(self):
        return 'soil_type'

# 天气API接口 - 提供异步数据获取
def weather_api(request):
    from django.http import JsonResponse
    
    # 使用缓存提高性能
    weather_data = cache.get('weather_data')
    current_weather = cache.get('current_weather')
    
    if weather_data is None or current_weather is None:
        try:
            # 重用通用天气获取方法
            home_page = HomePage()
            weather_result = home_page.fetch_weather_data()
            
            if (weather_result):
                weather_data, current_weather = weather_result
                cache.set('weather_data', weather_data, 60*60*3)
                cache.set('current_weather', current_weather, 60*60*3)
            else:
                # 错误响应
                return JsonResponse({
                    'status': 'error',
                    'message': '天气API响应错误',
                    'weather_data': {'update_data': '数据获取失败', 'humidity': 'N/A', 'wind_speed': 'N/A', 'code_day': '99', 'days': []},
                    'current_weather': {'temperature': '--', 'text': '数据获取中'},
                })
        except Exception as e:
            # 异常响应
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'weather_data': {'update_data': '数据获取失败', 'humidity': 'N/A', 'wind_speed': 'N/A', 'code_day': '99', 'days': []},
                'current_weather': {'temperature': '--', 'text': '数据获取中'},
            })
    
    # 成功响应
    return JsonResponse({
        'status': 'success',
        'weather_data': weather_data,
        'current_weather': current_weather
    })

# 创建审核历史记录
def create_review_history(content_type, content_id, reviewer, action, comment, content_name=None):
    """创建内容审核历史记录"""
    try:
        history = ReviewHistory(
            content_type=content_type,
            content_id=content_id,
            reviewer=reviewer,
            action=action,
            comment=comment
        )
        
        # 可选保存内容名称
        if content_name and hasattr(history, 'content_name'):
            history.content_name = content_name
                
        history.save()
        return history
    except Exception as e:
        print(f"创建审核历史记录失败: {e}")
        return None
