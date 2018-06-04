#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/11/9'

from django.conf.urls import url
from monitor.views import (
    MonitorView,
    MonitorDataView,
    NetworkView,
)

urlpatterns = [
    url(r'^$', MonitorView.as_view(), name='Monitor'),
    url(r'^disk', MonitorDataView.as_view(), name='data'),
    url(r'^network/', NetworkView.as_view(), name='network')
]
