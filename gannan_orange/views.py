from django.db.models import Q
from django.shortcuts import render
from django.views.generic import TemplateView,ListView
from .models import Variety, PlantingTech
# Create your views here.


class HomePage(TemplateView):
    template_name = 'gannan_orange/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'total_variety' : Variety.objects.count(),
            'last_variety': Variety.objects.order_by('-create_time')[:3],
            'last_planting_tech': PlantingTech.objects.order_by('-create_time')[:3],
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
    paginate_by = 4 # 分页

    def get_queryset(self):
        queryset = Variety.objects.order_by('-create_time')

        search_key = self.request.GET.get('q')
        if search_key:
            queryset = queryset.filter(Q(name__icontains=search_key)|Q(description__icontains=search_key)).order_by('-create_time')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_key'] = self.request.GET.get('q')
        return context


