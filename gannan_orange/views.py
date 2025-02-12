from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from User.models import CustomUser

from .forms import VarietyForm
from .models import Variety, PlantingTech,SoilType,Pest


# Create your views here.


class HomePage(TemplateView):
    template_name = 'gannan_orange/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'total_variety': Variety.objects.count(),
            'tech_count': PlantingTech.objects.count(),
            'last_variety': Variety.objects.order_by('-create_time')[:3],
            'last_planting_tech': PlantingTech.objects.order_by('-create_time')[:3],
            'user_count': CustomUser.objects.count(),
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
