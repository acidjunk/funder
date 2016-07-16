# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-16 13:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20160709_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_blog_pages', to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
    ]
