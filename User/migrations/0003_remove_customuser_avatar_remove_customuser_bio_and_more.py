# Generated by Django 5.1.5 on 2025-04-01 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0002_customuser_avatar_customuser_bio_customuser_birthday_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='avatar',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='birthday',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='join_date',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='specialty',
        ),
    ]
