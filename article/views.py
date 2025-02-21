from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView,ListView

from article.forms import PlantingTechArticleForm
from article.models import PlantingTechArticle, Comment


# Create your views here.
class PlantingTechCreateView(CreateView):
    model = PlantingTechArticle
    fields = ['title', 'content']
    template_name = 'article/planting_tech_create.html'
    success_url = reverse_lazy()
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PlantingTechArticle, Comment
from .forms import CommentForm

class PlantingTechDetailView(DetailView):
    model = PlantingTechArticle
    template_name = 'article/planting_tech_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(article=self.object).order_by('-create_time')
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = self.object
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "评论已成功发布！")
        else:
            messages.error(request, "评论提交失败，请检查输入内容！")

        return redirect('article:detail', pk=self.object.pk)

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


def favorite_article(request, pk):
    article = PlantingTechArticle.objects.get(pk=pk)
    if request.user in article.favorite_user.all():
        article.favorite_user.remove(request.user)
    else:
        article.favorite_user.add(request.user)
    return redirect('article:detail', pk=pk)



