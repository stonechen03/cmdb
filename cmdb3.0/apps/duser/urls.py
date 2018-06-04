#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/11/7'

from django.conf.urls import url
from views import (
	LogoutView,
	LoginView,
	SeeView,
	EditUserView,
	AddUserView,
	DelUserView,
	SeeGroupView,
	AddGroupView,
	EditGroupView,
	DelGroupView,
	AuthUserView,
	AuthAssetView,
)

urlpatterns = [
	url(r'^login/', LoginView.as_view(), name='login'),
	url(r'^logout/', LogoutView.as_view(), name='logout'),
	url(r'^list/', SeeView.as_view(), name='list'),
	url(r'^edit/', EditUserView.as_view(), name='edit'),
	url(r'^add/', AddUserView.as_view(), name='add'),
	url(r'^del/', DelUserView.as_view(), name='del'),
	url(r'^group_list', SeeGroupView.as_view(), name='group_list'),
	url(r'^group_add', AddGroupView.as_view(), name='group_add'),
	url(r'^group_edit', EditGroupView.as_view(), name='group_edit'),
	url(r'^group_del', DelGroupView.as_view(), name='group_del'),
	url(r'^auth_user', AuthUserView.as_view(), name='auth_user'),
	url(r'^auth_asset', AuthAssetView.as_view(), name='auth_asset'),
]
