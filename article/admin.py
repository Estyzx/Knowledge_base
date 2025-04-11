from django.contrib import admin
from .models import PlantingTechArticle, Comment, Category, Tag

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(PlantingTechArticle)
class PlantingTechArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'create_time', 'updated_time', 'views_count')
    list_filter = ('category', 'tags', 'author')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'article', 'parent', 'create_time')
    list_filter = ('author', 'create_time')
    search_fields = ('content',)