# coding:utf-8
from __future__ import unicode_literals

from django.db import models
from datetime import datetime


# Create your models here.


class Alarm(models.Model):
    level = models.CharField(max_length=15, verbose_name=u'告警级别')
    item = models.CharField(max_length=50, verbose_name=u'告警项')
    value = models.TextField(verbose_name=u"告警内容")
    ip = models.CharField(max_length=120, verbose_name=u'ip地址')
    resolve = models.BooleanField(default=False, verbose_name=u'是否已解决')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'报警时间')

    class Meta:
        verbose_name = u'报警信息'
        verbose_name_plural = verbose_name
        db_table = 'alarm'

    def __str__(self):
        return self.item
