from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from User.models import CustomUser

# Create your models here.
class PlantingTechArticle(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    title = models.CharField('标题', max_length=50, unique=False, blank=False)
    content = RichTextUploadingField('内容', blank=False)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='planting_tech_articles', verbose_name='作者')
    favorite_user = models.ManyToManyField(
        CustomUser,
        verbose_name='收藏用户',
        related_name='favorite_articles',
        blank=True
    )
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = '种植技术文章'
        verbose_name_plural = '种植技术文章'

class Comment(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    content = RichTextUploadingField('内容', blank=False)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments', verbose_name='作者')
    article = models.ForeignKey(PlantingTechArticle, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    def __str__(self):
        return self.content
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'

class UserArticleView(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(PlantingTechArticle, on_delete=models.CASCADE)
    view_time = models.DateTimeField(auto_now_add=True)