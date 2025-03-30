from weakref import ref
import requests
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from User.models import CustomUser
from article.models import PlantingTechArticle

from .forms import VarietyForm, PlantingTechForm, PestForm, SoilTypeForm, ReviewForm
from .models import Variety, PlantingTech, SoilType, Pest, ReviewHistory


# Create your views here.


class HomePage(TemplateView):
    template_name = 'gannan_orange/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        url = "https://api.seniverse.com/v3/weather/daily.json?key=SsIcJ_YpHt1dJPr1Q&location=ganzhou&language=zh-Hans&unit=c&start=0&days=5"
        url1 = "https://api.seniverse.com/v3/weather/now.json?key=SsIcJ_YpHt1dJPr1Q&location=ganzhou&language=zh-Hans&unit=c"
        response = requests.get(url)
        response1 = requests.get(url1)
        if response.status_code == 200:
            data = response.json()
            update_data = data['results'][0]['last_update'][:10]
            humidity = data['results'][0]['daily'][0]['humidity']
            wind_speed = data['results'][0]['daily'][0]['wind_speed']
            code_day = data['results'][0]['daily'][0]['code_day']
            if response1.status_code == 200:
                temperature = response1.json()['results'][0]['now']['temperature']
                update_data = data['results'][0]['last_update'][12:19]
            else:
                temperature = '暂无数据'

            context.update({
                'update_time': update_data,
                'temperature': temperature,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'icon_night': code_day+'@1x.png',
            })
        # 获取待审核内容的数量
        pending_varieties = Variety.objects.filter(review_status='pending').count()
        pending_planting_techs = PlantingTech.objects.filter(review_status='pending').count()
        pending_pests = Pest.objects.filter(review_status='pending').count()
        pending_soil_types = SoilType.objects.filter(review_status='pending').count()
        total_pending = pending_varieties + pending_planting_techs + pending_pests + pending_soil_types

        context.update({
            'total_variety': Variety.objects.count(),
            'tech_count': PlantingTech.objects.count(),
            'last_variety': Variety.objects.order_by('-create_time')[:3],
            'user_count': CustomUser.objects.count(),
            'tech_articles': PlantingTechArticle.objects.order_by('-create_time')[:3],
            'total_pending': total_pending,
            'pending_varieties': pending_varieties,
            'pending_planting_techs': pending_planting_techs,
            'pending_pests': pending_pests,
            'pending_soil_types': pending_soil_types,
        })

        # if self.request.user.is_authenticated:
        #     context['user'] = self.request.user
        #     user_data = self.get_user_recommend()

        return context

"""
    def get_user_recommend(self):
        user = self.request.user
        context = {}
        if user.region:
            context['region'] = user.region
        if user.variety:
            context['variety'] = user.variety

        return context
"""

class VarietyList(ListView):
    model = Variety
    template_name = 'gannan_orange/variety_list.html'
    paginate_by = 6  # 分页

    def get_queryset(self):
        queryset = Variety.objects.order_by('-create_time')

        # 未登录用户或非管理员/专家只能看到已审核通过的内容
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

class VarietyDetail(DetailView):
    model = Variety
    template_name = 'gannan_orange/variety_detail.html'
    context_object_name = 'variety'

    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        obj = get_object_or_404(Variety, id=vid)
        
        # 检查权限：未审核通过的内容只有管理员和专家可以访问
        if obj.review_status != 'approved' and not (self.request.user.is_staff or self.request.user.is_expert):
            messages.error(self.request, '该内容正在审核中，暂时无法访问')
            return redirect('orange:list')
        return obj

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

    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        obj = get_object_or_404(Variety, id=vid)
        
        # 检查权限：未审核通过的内容只有管理员和专家可以访问
        if obj.review_status != 'approved' and not (self.request.user.is_staff or self.request.user.is_expert):
            messages.error(self.request, '该内容正在审核中，暂时无法访问')
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
                
                messages.success(request, '审核操作已完成')
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

    def form_invalid(self, form):
        # 详细显示每个字段的错误信息
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"错误: {error}")
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('orange:detail', kwargs={'id': self.object.id})
        
    def form_invalid(self, form):
        # 确保表单错误信息正确传递到模板
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"错误: {error}")
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)
        
    def form_invalid(self, form):
        # 确保表单错误信息正确传递到模板
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"错误: {error}")
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")
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
                    messages.error(self.request, f"错误: {error}")
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)
        
    def form_invalid(self, form):
        # 确保表单错误信息正确传递到模板
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"错误: {error}")
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")
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

    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        return get_object_or_404(PlantingTech, id=vid)
    def get_context_data(self, **kwargs):
        # 调用父类的get_context_data方法
        context = super().get_context_data(**kwargs)
        # 获取HTTP_REFERER，如果没有则使用默认的URL
        referer = self.request.META.get('HTTP_REFERER')
        if 'edit' in referer:
            referer = reverse('orange:soil_list')
        if not referer:
            referer = reverse('orange:tech_list')
        context['referer'] = referer
        return context

class PlantingTechEdit(LoginRequiredMixin, UpdateView):
    model = PlantingTech
    template_name = 'gannan_orange/planting_tech_edit.html'
    context_object_name = 'plantingtech'
    form_class = PlantingTechForm

    def get_object(self, queryset=...):
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
    model = PlantingTech
    template_name = 'gannan_orange/planting_tech_creat.html'
    fields = ['name', 'description']

    def get_success_url(self):
        return reverse_lazy('orange:detail', kwargs={'id': self.object.id})
        
    def form_invalid(self, form):
        # 确保表单错误信息正确传递到模板
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"错误: {error}")
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)
        
    def form_invalid(self, form):
        # 确保表单错误信息正确传递到模板
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"错误: {error}")
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)

class SoilTypeDetail(DetailView):
    model = SoilType
    template_name = 'gannan_orange/soil_type_detail.html'
    context_object_name = 'soil'

    def get_object(self, queryset=None):
        # 获取URL中的id参数
        vid = self.kwargs.get('id')
        # 获取对象
        return get_object_or_404(SoilType, id=vid)

    def get_context_data(self, **kwargs):
        # 调用父类的get_context_data方法
        context = super().get_context_data(**kwargs)
        # 获取HTTP_REFERER，如果没有则使用默认的URL
        referer = self.request.META.get('HTTP_REFERER')
        # 如果是从编辑页面返回的，则返回列表页面
        if 'edit' in referer:
            referer = reverse('orange:soil_list')
        if not referer:
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
    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        pest = get_object_or_404(Pest, id=vid)
        # 检查审核状态和用户权限
        if pest.review_status != 'approved' and not (self.request.user.is_staff or self.request.user.is_expert):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied('该内容尚未通过审核，暂时无法访问。')
        return pest
    def get_context_data(self, **kwargs):
        # 调用父类的get_context_data方法
        context = super().get_context_data(**kwargs)
        # 获取HTTP_REFERER，如果没有则使用默认的URL
        referer = self.request.META.get('HTTP_REFERER')
        if 'edit' in referer:
            referer = reverse('orange:soil_list')
        if not referer:
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ReviewForm是普通Form而不是ModelForm
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs
    
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
    model = Variety
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
        messages.error(self.request, '只有专家用户才能访问审核功能')
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
        
        messages.success(self.request, f'品种 {variety.name} 审核{"通过" if action == "approve" else "拒绝"}成功')
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
    
    def form_valid(self, form):
        tech = self.object
        action = form.cleaned_data['action']
        comment = form.cleaned_data['comment']
        
        # 更新审核状态
        if action == 'approve':
            tech.review_status = 'approved'
        else:
            tech.review_status = 'rejected'
        
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
        
        messages.success(self.request, f'种植技术 {tech.name} 审核{"通过" if action == "approve" else "拒绝"}成功')
        return redirect('orange:pending_review')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ReviewForm是普通Form而不是ModelForm
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs


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
    
    def form_valid(self, form):
        pest = self.object
        action = form.cleaned_data['action']
        comment = form.cleaned_data['comment']
        
        # 更新审核状态
        if action == 'approve':
            pest.review_status = 'approved'
        else:
            pest.review_status = 'rejected'
        
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
        
        messages.success(self.request, f'病虫害 {pest.name} 审核{"通过" if action == "approve" else "拒绝"}成功')
        return redirect('orange:pending_review')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ReviewForm是普通Form而不是ModelForm
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs


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
    
    def form_valid(self, form):
        soil = self.object
        action = form.cleaned_data['action']
        comment = form.cleaned_data['comment']
        
        # 更新审核状态
        if action == 'approve':
            soil.review_status = 'approved'
        else:
            soil.review_status = 'rejected'
        
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
        
        messages.success(self.request, f'土壤类型 {soil.name} 审核{"通过" if action == "approve" else "拒绝"}成功')
        return redirect('orange:pending_review')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ReviewForm是普通Form而不是ModelForm
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs
