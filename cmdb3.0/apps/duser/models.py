# coding:utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class AuthGroupManage(models.Model):
	name = models.CharField(max_length=30, unique=True, verbose_name=u"组名")
	users = models.TextField(null=True, blank=True, verbose_name=u"授权用户")
	asset = models.TextField(null=True, blank=True, verbose_name=u"授权资产")

	class Meta:
		verbose_name = u"授权组"
		verbose_name_plural = verbose_name
		db_table = 'dct_group'

	def __unicode__(self):
		return self.name


class DctUserManger(AbstractUser):
	default_img = models.CharField(max_length=30, default='images/login/default.jpg', verbose_name=u"用户头像")
	mobile = models.CharField(max_length=15, verbose_name=u"用户手机")

	class Meta:
		verbose_name = u"用户管理"
		verbose_name_plural = verbose_name
		db_table = 'dct_user'

	def __str__(self):
		return self.username


