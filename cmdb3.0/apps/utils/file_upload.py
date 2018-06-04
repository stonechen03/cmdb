#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/11/30'

import os
import time
from django.conf import settings
from asset.models import Upload


def upload_file(files):
	now = time.localtime(time.time())
	year = time.strftime("%Y", now)
	month = time.strftime("%m", now)
	day = time.strftime("%d", now)

	if files:
		base_dir = settings.MEDIA_ROOT
		upload_dir = '/'.join((base_dir, year, month, day))
		if not os.path.exists(upload_dir):
			os.makedirs(upload_dir)
		file_dir = '/'.join((upload_dir, files.name))
		if not os.path.isfile(file_dir):
			url = '/'+'/'.join(('upload', year, month, day, files.name))
			Upload.objects.create(
				name=files.name,
				suffix=files.name.split('.')[-1],
				url=url,
			)

		with open(file_dir, 'wb+') as f:
			for chunk in files.chunks():
				f.write(chunk)
			return True
	return False
