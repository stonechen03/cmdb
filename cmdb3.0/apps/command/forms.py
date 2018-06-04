#!/usr/bin/env python
# coding:utf-8
__author__ = 'carey'
__date__ = '2017/12/6'

from django import forms
from django.core.exceptions import ValidationError
import re
import os


def validate_even_url(value):
	pattern = re.compile(r'http[s]?://\S')
	match = pattern.match(value)
	if not match:
		raise ValidationError("%s is not a url" % value)


def validate_even_checksum(value):
	pattern = re.compile(r'sha256:\w')
	match = pattern.match(value)
	if not match:
		raise ValidationError("checksum is error")


class DownloadFileForm(forms.Form):
	asset_id = forms.IntegerField(help_text=u"请输入资产id")
	module_args_url = forms.CharField(validators=[validate_even_url], help_text=u"请输入下载地址")
	module_args_dest = forms.CharField(help_text=u"请输入保存地址")
	module_args_checksum = forms.CharField(validators=[validate_even_checksum], required=False)


def validate_even_src(value):
	from django.conf import settings
	file_dir = settings.BASE_DIR + value
	if not os.path.isfile(file_dir):
		raise ValidationError(u"文件不存在")


def validate_even_permission(value):
	if not isinstance(int(value), int) and len(value) != 3:
		raise ValidationError(u"权限输入错误")


class DispenseFileForm(forms.Form):
	asset_id = forms.IntegerField(error_messages={'required': '请输入资产id'})
	module_args_src = forms.CharField(validators=[validate_even_src])
	module_args_dest = forms.CharField(error_messages={'required': '请输入目标地址'})
	module_args_permission = forms.IntegerField(error_messages={'required': '权限输入错误'}, validators=[validate_even_permission])


def validate_even_state(value):
	if value not in ['present', 'absent']:
		raise ValidationError(u"请选择正确的状态")


def validate_even_date(value):
	if value != '*':
		try:
			if not isinstance(int(value), int):
				raise ValidationError(u"请输入正确的时间")
			elif len(value) > 2:
				raise ValidationError(u"请输入正确的时间")
		except:
			if len(value) > 3:
				raise ValidationError(u"请输入正确的时间")


class CronForm(forms.Form):
	asset_id = forms.IntegerField(error_messages={'required': '请输入资产id'})
	state = forms.CharField(validators=[validate_even_state])
	name = forms.CharField(max_length=50, error_messages={'required': '字段过长'})
	minute = forms.CharField(validators=[validate_even_date])
	hour = forms.CharField(validators=[validate_even_date])
	day = forms.CharField(validators=[validate_even_date])
	month = forms.CharField(validators=[validate_even_date])
	weekday = forms.CharField(validators=[validate_even_date])
	job = forms.CharField()
