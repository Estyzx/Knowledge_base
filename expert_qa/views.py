from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Question, Answer, ExpertProfile

def question_list(request):
    questions = Question.objects.all().order_by('-created_at')
    
    # 搜索功能
    query = request.GET.get('q')
    if query:
        questions = questions.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__icontains=query)
        )
    
    # 分类筛选
    category = request.GET.get('category')
    if category:
        questions = questions.filter(category=category)
    
    # 分页
    paginator = Paginator(questions, 10)
    page = request.GET.get('page')
    questions = paginator.get_page(page)
    
    return render(request, 'expert_qa/question_list.html', {
        'questions': questions,
        'query': query,
        'category': category
    })

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    
    # 增加浏览量
    question.views += 1
    question.save()
    
    # 获取排序方式
    sort_by = request.GET.get('sort', 'time')  # 默认按时间排序
    
    # 获取回答列表并排序
    answers = question.answers.all()
    answers = answers.order_by('-created_at')
    
    # 获取相关问题
    related_questions = Question.objects.filter(
        Q(category=question.category) | 
        Q(tags__icontains=question.tags)
    ).exclude(id=question.id).order_by('-vote_count', '-created_at')[:5]
    
    # 检查用户是否已投票
    user_voted = False
    if request.user.is_authenticated:
        user_voted = question.votes.filter(id=request.user.id).exists()
    
    # 获取HTTP_REFERER，如果没有则使用默认的URL
    referer = request.META.get('HTTP_REFERER')
    # 安全地处理referer
    if referer:
        # 如果referer包含特定关键词，返回相应列表页面
        if 'edit' in referer or 'answer' in referer:
            referer = reverse('expert_qa:question_list')
    else:
        # 如果没有referer，则返回问题列表页面
        referer = reverse('expert_qa:question_list')
    
    return render(request, 'expert_qa/question_detail.html', {
        'question': question,
        'answers': answers,
        'related_questions': related_questions,
        'user_voted': user_voted,
        'sort_by': sort_by,
        'referer': referer
    })

@login_required
def ask_question(request, expert_id=None):
    expert = None
    if expert_id:
        expert = get_object_or_404(ExpertProfile, id=expert_id)
        # 检查专家是否已认证
        if not expert.is_verified:
            messages.error(request, '该专家尚未认证，无法向其提问！')
            return redirect('expert_qa:expert_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        tags = request.POST.get('tags', '')
        
        if title and content and category:
            question = Question.objects.create(
                title=title,
                content=content,
                category=category,
                author=request.user,
                expert=expert.user if expert else None,
                tags=tags
            )
            messages.success(request, '问题提交成功！')
            return redirect('expert_qa:question_detail', pk=question.pk)
        else:
            messages.error(request, '请填写所有必填字段！')
    
    # 获取问题类别选项
    from .models import QUESTION_CATEGORIES
    
    return render(request, 'expert_qa/ask_question.html', {
        'expert': expert,
        'categories': QUESTION_CATEGORIES
    })

@login_required
def post_answer(request, question_id):
    if not hasattr(request.user, 'expert_profile'):
        messages.error(request, '只有专家才能回答问题！')
        return redirect('expert_qa:question_detail', pk=question_id)
    
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            answer = Answer.objects.create(
                question=question,
                content=content,
                expert=request.user
            )
            request.user.expert_profile.update_answer_stats()
            return redirect('expert_qa:question_detail', pk=question_id)
    
    return render(request, 'expert_qa/post_answer.html', {'question': question})

@login_required
def accept_answer(request, answer_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '不支持的请求方法'}, status=405)
        
    try:

        answer = get_object_or_404(Answer, pk=answer_id)
        
        if request.user != answer.question.author:
            return JsonResponse({'success': False, 'message': '只有问题作者可以采纳回答'}, status=403)
        
        # 检查回答是否已被采纳
        if answer.is_accepted:
            return JsonResponse({'success': False, 'message': '该回答已经被采纳'}, status=400)
        
        # 检查问题是否已有采纳的回答
        if answer.question.answers.filter(is_accepted=True).exists():
            return JsonResponse({'success': False, 'message': '该问题已有采纳的回答'}, status=400)
        
        answer.is_accepted = True
        answer.save()
        
        answer.expert.expert_profile.update_answer_stats(is_accepted=True)
        answer.question.is_answered = True
        answer.question.save()
        
        return JsonResponse({
            'success': True,
            'message': '回答已成功采纳'
        })
    except Answer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '回答不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
def vote_question(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '不支持的请求方法'}, status=405)
    
    question = get_object_or_404(Question, pk=pk)
    
    try:
        # 检查用户是否已投票
        if question.votes.filter(id=request.user.id).exists():
            question.votes.remove(request.user)
            message = '已取消投票'
        else:
            question.votes.add(request.user)
            message = '投票成功'
        
        question.update_vote_count()
        return JsonResponse({
            'success': True,
            'message': message,
            'votes_count': question.votes.count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def vote_answer(request, answer_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '不支持的请求方法'}, status=405)
    
    answer = get_object_or_404(Answer, pk=answer_id)
    
    try:
        # 检查用户是否已投票
        if answer.votes.filter(id=request.user.id).exists():
            answer.votes.remove(request.user)
            message = '已取消投票'
        else:
            answer.votes.add(request.user)
            message = '投票成功'
        
        answer.update_vote_count()
        return JsonResponse({
            'success': True,
            'message': message,
            'votes_count': answer.votes.count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def expert_list(request):
    experts = ExpertProfile.objects.filter(is_verified=True)
    
    # 分类筛选
    category = request.GET.get('category')
    if category:
        experts = experts.filter(category=category)
    
    # 搜索功能
    query = request.GET.get('q')
    if query:
        experts = experts.filter(
            Q(user__username__icontains=query) |
            Q(expertise__icontains=query) |
            Q(bio__icontains=query)
        )
    
    # 排序功能
    sort_by = request.GET.get('sort', 'rating')  # 默认按评分排序
    if sort_by == 'rating':
        experts = experts.order_by('-rating')
    elif sort_by == 'answers':
        experts = experts.order_by('-total_answers')
    elif sort_by == 'accepted':
        experts = experts.order_by('-accepted_answers')
    elif sort_by == 'newest':
        experts = experts.order_by('-verified_at')
    
    # 分页
    paginator = Paginator(experts, 12)
    page = request.GET.get('page')
    experts = paginator.get_page(page)
    
    # 获取类别选项列表
    categories = ExpertProfile.CATEGORY_CHOICES
    
    return render(request, 'expert_qa/expert_list.html', {
        'experts': experts,
        'category': category,
        'query': query,
        'sort_by': sort_by,
        'categories': categories
    })

@login_required
def expert_detail(request, expert_id):
    expert = get_object_or_404(ExpertProfile, id=expert_id)
    
    # 获取专家的回答
    answers = Answer.objects.filter(expert=expert.user).order_by('-vote_count', '-created_at')
    
    # 获取专家回答的问题
    questions = Question.objects.filter(answers__expert=expert.user).distinct().order_by('-created_at')
    
    # 分页
    paginator = Paginator(answers, 5)
    page = request.GET.get('page')
    answers_page = paginator.get_page(page)
    
    # 获取HTTP_REFERER，如果没有则使用默认的URL
    referer = request.META.get('HTTP_REFERER')
    # 安全地处理referer
    if referer:
        pass  # 保留原始返回链接
    else:
        # 如果没有referer，则返回专家列表页面
        referer = reverse('expert_qa:expert_list')
    
    return render(request, 'expert_qa/expert_detail.html', {
        'expert': expert,
        'answers': answers_page,
        'questions': questions,
        'total_questions': questions.count(),
        'referer': referer
    })

@login_required
def verify_expert(request, expert_id):
    if not request.user.is_staff:
        messages.error(request, '只有管理员可以进行专家认定！')
        return redirect('expert_qa:expert_list')
    
    expert = get_object_or_404(ExpertProfile, pk=expert_id)
    
    if request.method == 'POST':
        expert.verify()
        messages.success(request, f'已成功认定{expert.user.username}为专家！')
        return redirect('expert_qa:expert_list')
    
    return render(request, 'expert_qa/verify_expert.html', {'expert': expert})

@login_required
def follow_up_question(request, pk):
    parent_question = get_object_or_404(Question, pk=pk)
    
    # 只有原问题的提问者才能追问
    if request.user != parent_question.author:
        messages.error(request, '只有原问题的提问者才能追问！')
        return redirect('expert_qa:question_detail', pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        tags = request.POST.get('tags', '')
        
        if title and content:
            follow_up = Question.objects.create(
                title=title,
                content=content,
                category=category or parent_question.category,
                author=request.user,
                expert=parent_question.expert,
                parent_question=parent_question,
                is_follow_up=True,
                tags=tags
            )
            messages.success(request, '追问提交成功！')
            return redirect('expert_qa:question_detail', pk=follow_up.pk)
        else:
            messages.error(request, '请填写所有必填字段！')
    
    # 获取问题类别选项
    from .models import QUESTION_CATEGORIES
    
    return render(request, 'expert_qa/follow_up_question.html', {
        'parent_question': parent_question,
        'categories': QUESTION_CATEGORIES
    })
