from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView,ListView

from article.forms import PlantingTechArticleForm
from article.models import PlantingTechArticle


# Create your views here.
class PlantingTechCreateView(CreateView):
    model = PlantingTechArticle
    fields = ['title', 'content']
    template_name = 'article/planting_tech_create.html'
    success_url = reverse_lazy()
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PlantingTechDetailView(DetailView):
    model = PlantingTechArticle
    template_name = 'article/planting_tech_detail.html'
    context_object_name = 'article'
    def post (self, request, *args, **kwargs):
        article = self.get_object()
        user = self.request.user
        if user in article.favorite_user.all():
            article.favorite_user.remove(user)
        else:
            article.favorite_user.add(user)
        return self.get(request, *args, **kwargs)

class PlantingTechListView(ListView):
    model = PlantingTechArticle
    template_name = 'article/planting_tech_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-create_time')
        if self.request.GET.get('q'):
            queryset = queryset.filter(Q(title__icontains=self.request.GET.get('q'))|Q(content__icontains=self.request.GET.get('q')))

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_key'] = self.request.GET.get('q')
        return context



