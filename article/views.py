from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

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


