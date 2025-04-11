from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from article.forms import PlantingTechArticleForm
from article.models import PlantingTechArticle, Comment, UserArticleView,Category,Tag
from .forms import CommentForm

# Create your views here.
class PlantingTechCreateView(LoginRequiredMixin, CreateView):
    model = PlantingTechArticle
    form_class = PlantingTechArticleForm
    template_name = 'article/planting_tech_create.html'
    success_url = reverse_lazy('article:list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        # 保存文章
        response = super().form_valid(form)
        
        # 处理标签
        tags = form.cleaned_data.get('tags', [])
        self.object.tags.set(tags)
        
        return response



class PlantingTechDetailView(DetailView):
    model = PlantingTechArticle
    template_name = 'article/planting_tech_detail.html'
    context_object_name = 'article'

    def get(self, request, *args, **kwargs):
        # 直接返回父类方法结果
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # 增加浏览次数
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取文章的评论，不包括回复
        context['comments'] = Comment.objects.filter(article=self.object, parent=None).order_by('-create_time')
        context['comment_form'] = CommentForm()
        
        # 获取HTTP_REFERER，如果没有则使用默认的URL
        referer = self.request.META.get('HTTP_REFERER')
        # 安全地处理referer
        if referer:
            # 如果referer包含'edit'，那么返回列表页面
            if 'edit' in referer:
                referer = reverse('article:list')
        else:
            # 如果没有referer，则返回列表页面
            referer = reverse('article:list')
        context['referer'] = referer
        
        # 记录用户浏览历史
        if self.request.user.is_authenticated:
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
            
            # 处理回复评论
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                new_comment.parent = parent_comment
                
            new_comment.save()
            
            # 返回完整的评论数据，使用更一致的时间格式
            from django.utils.timezone import localtime
            
            # 构建评论数据字典
            comment_data = {
                'id': new_comment.id,
                'content': new_comment.content,
                'author_name': new_comment.author.username,
                'created_time': localtime(new_comment.create_time).strftime('%Y-%m-%d %H:%M'),
                'is_author': new_comment.author == self.object.author,
                'can_delete': True,  # 新评论的作者就是当前用户
                'parent_id': new_comment.parent.id if new_comment.parent else None
            }
            
            # 如果是回复评论，添加父评论作者名称
            if new_comment.parent:
                parent_author_name = new_comment.parent.author.username
                comment_data['parent_author_name'] = parent_author_name
            
            return JsonResponse({
                'status': 'success',
                'comment': comment_data
            })
        else:
            
            return JsonResponse({
                'status': 'error',
                'message': '评论提交失败，请检查输入内容！'
            }, status=400)


class PlantingTechListView(ListView):
    model = PlantingTechArticle
    template_name = 'article/planting_tech_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get(self, request, *args, **kwargs):
        # 直接返回父类方法结果
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-create_time')
        
        # 搜索功能
        if self.request.GET.get('q'):
            search_key = self.request.GET.get('q')
            queryset = queryset.filter(Q(title__icontains=search_key) | Q(content__icontains=search_key))
        
        # 分类筛选
        if self.request.GET.get('category'):
            queryset = queryset.filter(category_id=self.request.GET.get('category'))
        
        # 标签筛选
        if self.request.GET.get('tag'):
            queryset = queryset.filter(tags__id=self.request.GET.get('tag'))

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_key'] = self.request.GET.get('q')
        context['category_id'] = self.request.GET.get('category')
        context['tag_id'] = self.request.GET.get('tag')
        
        # 获取所有分类和标签供筛选使用
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        
        return context


def favorite_article(request, pk):
    article = PlantingTechArticle.objects.get(pk=pk)
    is_favorite = False
    
    if request.user in article.favorite_user.all():
        article.favorite_user.remove(request.user)
    else:
        article.favorite_user.add(request.user)
        is_favorite = True
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite,
            'favorite_count': article.favorite_user.count()
        })
    
    # 否则重定向到文章详情页
    return redirect('article:detail', pk=pk)


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class PlantingTechEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PlantingTechArticle
    form_class = PlantingTechArticleForm
    template_name = 'article/planting_tech_edit.html'
    context_object_name = 'article'
    
    def test_func(self):
        # 确保只有文章作者才能编辑
        article = self.get_object()
        return self.request.user == article.author
    
    def get_success_url(self):
        return reverse('article:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # 保存文章
        response = super().form_valid(form)
        
        # 处理标签
        tags = form.cleaned_data.get('tags', [])
        self.object.tags.set(tags)
        
        return response


from django.views.generic.edit import DeleteView

class PlantingTechDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PlantingTechArticle
    template_name = 'article/planting_tech_delete_confirm.html'
    context_object_name = 'article'
    success_url = reverse_lazy('article:list')
    
    def test_func(self):
        # 确保只有文章作者才能删除
        article = self.get_object()
        return self.request.user == article.author


from django.http import JsonResponse


def comment_delete(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': '请先登录！'}, status=403)

    comment = get_object_or_404(Comment, pk=pk)

    # 验证权限：只有评论作者可以删除评论
    if request.user != comment.author:
        return JsonResponse({'status': 'error', 'message': '您没有权限删除此评论！'}, status=403)
    
    # 删除评论
    author = comment.author.username  # 获取评论作者的用户名
    comment.delete()
    

    
    return JsonResponse({
        'status': 'success',
        'message': '评论已成功删除！',
        'author': author  # 返回评论作者信息
    })

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



