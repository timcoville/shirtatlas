# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-09 00:56
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0007_design_paused'),
    ]

    operations = [
        migrations.AlterField(
            model_name='design',
            name='categories',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), size=3),
        ),
    ]
