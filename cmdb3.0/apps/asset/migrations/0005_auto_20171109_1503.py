# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-11-09 15:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0004_auto_20171108_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='disk',
            field=models.TextField(blank=True, max_length=1024, null=True, verbose_name='\u786c\u76d8'),
        ),
    ]