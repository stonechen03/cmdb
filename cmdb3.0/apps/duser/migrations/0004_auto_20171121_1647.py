# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-11-21 16:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('duser', '0003_auto_20171121_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='\u7ec4\u540d')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u7ec4',
                'verbose_name_plural': '\u7528\u6237\u7ec4',
            },
        ),
        migrations.AddField(
            model_name='dctusermanger',
            name='group',
            field=models.ForeignKey(default=11, on_delete=django.db.models.deletion.CASCADE, to='duser.UserGroup', to_field='name', verbose_name='\u6388\u6743\u7ec4'),
            preserve_default=False,
        ),
    ]
