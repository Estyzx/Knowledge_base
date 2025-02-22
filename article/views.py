from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from article.forms import PlantingTechArticleForm
from article.models import PlantingTechArticle, Comment, UserArticleView
from .forms import CommentForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(article=self.object).order_by('-create_time')
        context['comment_form'] = CommentForm()
        user = self.request.user
        UserArticleView.objects.create(user=user, article=self.object)
        user_views = UserArticleView.objects.filter(user=user)
        if user_views.exists():
            most_viewed_article = user_views.latest('view_time').article
            recommended_articles = get_similar_articles(most_viewed_article)
            context['recommended_articles'] = recommended_articles
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


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_similar_articles(article):
    articles = list(PlantingTechArticle.objects.all())  # 将 QuerySet 转换为列表
    article_id_to_index = {art.id: idx for idx, art in enumerate(articles)}  # 创建 id 到索引的映射

    # 找到目标文章的索引
    try:
        article_index = article_id_to_index[article.id]
    except KeyError:
        raise ValueError("Target article not found in the articles list.")

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([art.content for art in articles])
    cos_sim = cosine_similarity(tfidf_matrix)

    # 计算相似度分数
    sim_scores = list(enumerate(cos_sim[article_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # 排除目标文章本身

    article_indices = [i[0] for i in sim_scores]
    return [articles[i] for i in article_indices]
