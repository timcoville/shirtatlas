# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-05 23:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_auto_20180802_0313'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='sales',
            field=models.IntegerField(default=0),
        ),
    ]
