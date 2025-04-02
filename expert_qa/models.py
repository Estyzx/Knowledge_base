from django.db import models
from User.models import CustomUser
from django.utils import timezone

class ExpertProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='expert_profile',verbose_name='账号')
    expertise = models.CharField(max_length=100,verbose_name= '专家领域')
    bio = models.TextField(verbose_name='专家简介')
    is_verified = models.BooleanField(default=False, verbose_name='是否认证')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='认证时间')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name='评分')
    total_answers = models.IntegerField(default=0, verbose_name='总回答数')
    accepted_answers = models.IntegerField(default=0, verbose_name='被采纳数')
    title = models.CharField(max_length=100, blank=True, verbose_name='职称')
    avatar = models.ImageField(upload_to='expert_avatars/', null=True, blank=True, verbose_name='头像')
    
    # 专家可以选择的领域类别
    CATEGORY_CHOICES = [
        ('planting', '种植'),
        ('harvesting', '收获'),
        ('pest_control', '病虫害防治'),
        ('fertilizer', '肥料'),
        ('irrigation', '灌溉'),
        ('soil', '土壤'),
        ('other', '其他')
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name='专业类别')
    
    # 专家等级
    LEVEL_CHOICES = [
        ('beginner', '初级专家'),
        ('intermediate', '中级专家'),
        ('advanced', '高级专家'),
        ('master', '大师级专家')
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner', verbose_name='专家等级')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return f"{self.user.username} - {self.expertise}"
    
    def verify(self):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
    
    def calculate_rating(self):
        if self.total_answers > 0:
            self.rating = (self.accepted_answers / self.total_answers) * 5
            self.save()
    
    def update_answer_stats(self, is_accepted=False):
        self.total_answers += 1
        if is_accepted:
            self.accepted_answers += 1
        self.calculate_rating()
    
    def get_level(self):
        if self.rating >= 4.5:
            return 'master'
        elif self.rating >= 4.0:
            return 'advanced'
        elif self.rating >= 3.0:
            return 'intermediate'
        else:
            return 'beginner'
    
    def save(self, *args, **kwargs):
        if self.rating > 0:
            self.level = self.get_level()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '专家资料'
        verbose_name_plural = '专家资料'

# 问题类别选项
QUESTION_CATEGORIES = [
    ('planting', '种植'),
    ('harvesting', '收获'),
    ('pest_control', '病虫害防治'),
    ('fertilizer', '肥料'),
    ('irrigation', '灌溉'),
    ('soil', '土壤'),
    ('other', '其他')
]

class Question(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='questions', verbose_name='提问者')
    expert = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_questions', verbose_name='指定专家')
    category = models.CharField(max_length=20, choices=QUESTION_CATEGORIES, default='other', verbose_name='问题类别')
    is_answered = models.BooleanField(default=False, verbose_name='是否已回答')
    parent_question = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='follow_up_questions', verbose_name='原问题')
    is_follow_up = models.BooleanField(default=False, verbose_name='是否为追问')
    votes = models.ManyToManyField(CustomUser, related_name='voted_questions', blank=True, verbose_name='投票')
    vote_count = models.IntegerField(default=0, verbose_name='投票数')
    views = models.IntegerField(default=0, verbose_name='浏览数')
    tags = models.CharField(max_length=200, blank=True, verbose_name='标签')
    
    def update_vote_count(self):
        self.vote_count = self.votes.count()
        self.save()
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = '问题'
        verbose_name_plural = '问题'

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='问题')
    content = models.TextField(verbose_name='回答内容')
    expert = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='answers', verbose_name='回答专家')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_accepted = models.BooleanField(default=False, verbose_name='是否被采纳')
    votes = models.ManyToManyField(CustomUser, related_name='voted_answers', blank=True, verbose_name='投票')
    vote_count = models.IntegerField(default=0, verbose_name='投票数')
    
    def update_vote_count(self):
        self.vote_count = self.votes.count()
        self.save()
    
    def __str__(self):
        return f"{self.expert.username}对问题'{self.question.title}'的回答"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '回答'
        verbose_name_plural = '回答'