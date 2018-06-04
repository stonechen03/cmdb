# coding:utf-8
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
# Create your models here.


class AssetGroup(models.Model):
	name = models.CharField(max_length=30, unique=True, verbose_name=u"组名")
	comment = models.TextField(max_length=100, blank=True, null=True, verbose_name=u"备注")
	add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

	def __str__(self):
		return self.name


class Asset(models.Model):
	ip = models.CharField(max_length=60, unique=True, verbose_name=u"主机IP")
	other_ip = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"其他IP")
	hostname = models.CharField(max_length=128, verbose_name=u"主机名")
	port = models.IntegerField(default=22, blank=True, null=True, verbose_name=u"端口号")
	group = models.CharField(max_length=30, blank=True, verbose_name=u"所属主机组")
	username = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"管理用户名")
	password = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"密码")
	mac = models.CharField(max_length=20, blank=True, null=True, verbose_name=u"MAC地址")
	cpu = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'CPU')
	memory = models.CharField(max_length=128, blank=True, null=True, verbose_name=u'内存')
	disk = models.TextField(max_length=1024, blank=True, null=True, verbose_name=u'硬盘')
	system_type = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"系统类型")
	system_version = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"系统版本号")
	system_arch = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"系统平台")
	kernel = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"内核")
	brand = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'硬件厂商型号')
	sn = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"SN编号")
	comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")
	add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

	class Meta:
		verbose_name = u"主机资产"
		verbose_name_plural = verbose_name
		db_table = 'assets'

	def __str__(self):
		return self.ip


class Upload(models.Model):
	name = models.CharField(max_length=50, verbose_name=u"文件名")
	suffix = models.CharField(max_length=10, verbose_name=u"后缀")
	url = models.CharField(max_length=100, verbose_name=u"上传图片地址")
	add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

	class Meta:
		verbose_name = u"文件上传url"
		verbose_name_plural = verbose_name
		db_table = 'upload'

	def __str__(self):
		return self.url
