# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-16 14:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_blogpage_show_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpage',
            name='teaser',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]