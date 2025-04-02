# Generated by Django 5.1.5 on 2025-03-29 11:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gannan_orange', '0005_pest_review_comment_pest_review_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(choices=[('variety', '品种'), ('planting_tech', '种植技术'), ('pest', '病虫害'), ('soil_type', '土壤类型')], max_length=15, verbose_name='内容类型')),
                ('content_id', models.PositiveIntegerField(verbose_name='内容ID')),
                ('action', models.CharField(choices=[('approve', '通过'), ('reject', '拒绝'), ('comment', '评论')], max_length=10, verbose_name='审核操作')),
                ('comment', models.TextField(blank=True, verbose_name='审核意见')),
                ('review_date', models.DateTimeField(auto_now_add=True, verbose_name='审核时间')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_histories', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
            ],
            options={
                'verbose_name': '审核历史',
                'verbose_name_plural': '审核历史',
                'ordering': ['-review_date'],
            },
        ),
    ]
