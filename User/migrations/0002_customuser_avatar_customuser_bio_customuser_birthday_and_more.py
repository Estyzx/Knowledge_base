# Generated by Django 5.1.5 on 2025-04-01 13:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='头像'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bio',
            field=models.TextField(blank=True, max_length=500, verbose_name='个人简介'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='生日'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='join_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='加入日期'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customuser',
            name='specialty',
            field=models.CharField(blank=True, max_length=100, verbose_name='专长领域'),
        ),
    ]
