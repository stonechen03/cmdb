# coding:utf-8
from __future__ import unicode_literals

from django.db import models
from asset.models import Asset
from datetime import datetime
# Create your models here.


class MonitorInfo(models.Model):
	mem_free = models.IntegerField(verbose_name=u"mem free")
	mem_buff = models.IntegerField(verbose_name=u"mem buff")
	mem_cache = models.IntegerField(verbose_name=u"mem cache")
	io_bi = models.IntegerField(verbose_name=u"io bi")
	io_bo = models.IntegerField(verbose_name=u"io bo")
	cpu_use = models.IntegerField(verbose_name=u"cpu us")
	cpu_sys = models.IntegerField(verbose_name=u"cpu sy")
	cpu_idle = models.IntegerField(verbose_name=u"cpu id")
	ip = models.ForeignKey(Asset, to_field='ip', verbose_name=u"关联主机")
	monitor_time = models.DateTimeField(verbose_name=u"取值时间")

	class Meta:
		verbose_name = "监控信息"
		verbose_name_plural = verbose_name

	def __str__(self):
		return self.id

	def __repr__(self):
		return str(self.ip)
