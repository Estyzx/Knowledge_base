import os
import django
import random
import time
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Knowledge_base.settings')
django.setup()

from django.utils import timezone
from article.models import Category, Tag, PlantingTechArticle
from User.models import CustomUser

def create_sample_articles():
    """创建示例文章"""
    # 记录开始时间
    start_time = time.time()
    print("开始创建示例文章...")
    
    # 确保有管理员用户
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True,
            'phone': '13800000000',  # 添加必需的手机号字段
            'role': 'admin'  # 设置角色
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("已创建管理员用户")
    
    # 创建分类
    categories = [
        # ...existing code...
    ]
    
    category_objs = []
    for cat in categories:
        cat_obj, created = Category.objects.get_or_create(
            name=cat['name'],
            defaults={'description': cat['description']}
        )
        category_objs.append(cat_obj)
        if created:
            print(f"已创建分类: {cat['name']}")
    
    # 创建标签
    tags = [
        # ...existing code...
    ]
    
    tag_objs = []
    for tag_name in tags:
        tag_obj, created = Tag.objects.get_or_create(name=tag_name)
        tag_objs.append(tag_obj)
        if created:
            print(f"已创建标签: {tag_name}")
    
    # 文章内容
    articles = [
        # ...existing code...
    ]
    
    # 批量创建文章 - 使用事务处理和批量操作提高性能
    from django.db import transaction
    
    created_count = 0
    with transaction.atomic():
        for article_data in articles:
            # 检查是否已存在同标题文章
            if not PlantingTechArticle.objects.filter(title=article_data['title']).exists():
                article = PlantingTechArticle.objects.create(
                    title=article_data['title'],
                    content=article_data['content'],
                    author=admin_user,
                    category=article_data['category'],
                    views_count=random.randint(10, 200)
                )
                
                # 添加标签
                article.tags.set(article_data['tags'])
                
                # 随机添加收藏
                favorite_count = random.randint(0, 5)  # 减少收藏数量提高性能
                if favorite_count > 0:
                    users = list(CustomUser.objects.all()[:favorite_count])
                    article.favorite_user.set(users)
                
                created_count += 1
                print(f"已创建文章: {article_data['title']}")
    
    # 记录完成时间和性能数据
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"总共创建了 {created_count} 篇新文章")
    print(f"执行时间: {elapsed_time:.2f} 秒")
    
    # 计算每篇文章平均创建时间
    if created_count > 0:
        print(f"平均每篇文章创建时间: {(elapsed_time / created_count):.2f} 秒")
    
    return created_count

if __name__ == "__main__":
    create_sample_articles()