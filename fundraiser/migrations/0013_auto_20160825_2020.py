# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-25 20:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraiser', '0012_projectpage_show_comments'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productpage',
            old_name='amount',
            new_name='prize',
        ),
        migrations.AddField(
            model_name='productpage',
            name='stock',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
