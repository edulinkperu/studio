# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-04-23 01:24
from __future__ import unicode_literals

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('contentcuration', '0110_auto_20200117_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='first_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
