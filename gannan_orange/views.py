import requests
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from User.models import CustomUser
from article.models import PlantingTechArticle

from .forms import VarietyForm
from .models import Variety, PlantingTech,SoilType,Pest


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
        context.update({
            'total_variety': Variety.objects.count(),
            'tech_count': PlantingTech.objects.count(),
            'last_variety': Variety.objects.order_by('-create_time')[:3],
            'user_count': CustomUser.objects.count(),
            'tech_articles': PlantingTechArticle.objects.order_by('-create_time')[:3],
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
        return get_object_or_404(Variety, id=vid)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        if user.is_authenticated:
            if user not in self.object.favorite_user.all():
                self.object.favorite_user.add(user)
            else:
                self.object.favorite_user.remove(user)
        return self.get(request, *args, **kwargs)

class VarietyEdit(UpdateView):
    model = Variety
    form_class = VarietyForm
    template_name = 'gannan_orange/variety_edit.html'
    context_object_name = 'variety'

    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        return get_object_or_404(Variety, id=vid)

    def get_success_url(self):
        return reverse_lazy('orange:detail', kwargs={'id': self.object.id})

class VarietyCreate(CreateView):
    model = Variety
    form_class = VarietyForm
    template_name = 'gannan_orange/variety_create.html'

    def get_success_url(self):
        return reverse_lazy('orange:detail', kwargs={'id': self.object.id})

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

class PlantingTechEdit(UpdateView):
    model = PlantingTech
    template_name = 'gannan_orange/planting_tech_edit.html'
    context_object_name = 'plantingtech'
    fields = ['name', 'description']

    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        return get_object_or_404(PlantingTech, id=vid)

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

class SoilTypeDetail(DetailView):
    mobile = SoilType
    template_name = 'gannan_orange/soil_type_detail.html'
    context_object_name = 'soil'
    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        return get_object_or_404(SoilType, id=vid)

class SoilTypeEdit(UpdateView):
    model = SoilType
    template_name = 'gannan_orange/soil_type_edit.html'
    context_object_name = 'soil'
    fields = ['name', 'description', 'organic_matter', 'ph_range']
    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        return get_object_or_404(SoilType, id=vid)
    def get_success_url(self):
        return reverse_lazy("orange:soil_detail", kwargs={'id': self.object.id})


class SoilTypeList(ListView):
    model = SoilType
    template_name = 'gannan_orange/soil_type_list.html'
    paginate_by = 6
    def get_queryset(self):
        queryset = SoilType.objects.order_by('-create_time')
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
        return get_object_or_404(Pest, id=vid)


class PestList(ListView):
    model = Pest
    template_name = 'gannan_orange/pest_list.html'
    paginate_by = 6
    def get_queryset(self):
        queryset = Pest.objects.order_by('-create_time')
        search_key = self.request.GET.get('q')
        if search_key:
            queryset = queryset.filter(Q(name__icontains=search_key) | Q(description__icontains=search_key)).order_by(
                '-create_time')
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_key'] = self.request.GET.get('q')
        return context


class PestEdit(UpdateView):
    model = Pest
    template_name = 'gannan_orange/pest_edit.html'
    context_object_name = 'edit'
    fields = ['name', 'description']
    def get_object(self, queryset=...):
        vid = self.kwargs.get('id')
        return get_object_or_404(Pest, id=vid)


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
