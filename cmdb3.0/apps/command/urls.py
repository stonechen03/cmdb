#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/12/1'

from django.conf.urls import url
from views import (
    CommandView,
    DownloadFileView,
    DispenseFileView,
    CronView,
    PushMonitorScriptView,
)

urlpatterns = [
    url(r'^cmd/', CommandView.as_view(), name='cmd'),
    url(r'^download/file/', DownloadFileView.as_view(), name='download_file'),
    url(r'dispense/file/', DispenseFileView.as_view(), name='dispense_file'),
    url(r'cron/', CronView.as_view(), name='cron'),
    url(r'push/monitor/script/', PushMonitorScriptView.as_view(), name='push_monitor_script'),
]
