#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/12/4'

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from alarm.views import (
    AlarmInterfaceView,
    AlarmListView,
)

urlpatterns = [
    url(r'^interface/', AlarmInterfaceView.as_view(), name='interface'),
    url(r'list/', AlarmListView.as_view(), name='list'),
]
