#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/11/7'

from django.conf.urls import url
from views import (
    AssetGroupView,
    EditGroupView,
    DelGroupView,
    AddGroupView,
    AssetView,
    AddAssetView,
    SeeAssetView,
    EditAssetView,
    DelAssetView,
    UpdateAssetView,
    WebSshView,
    UploadFileView,
    FileListView,
    FileEditView,
    SendKeyView,
    NewWebSshView,
)

urlpatterns = [
    url(r'^group/', AssetGroupView.as_view(), name='group'),
    url(r'^edit/', EditGroupView.as_view(), name='edit'),
    url(r'^del/', DelGroupView.as_view(), name='del'),
    url(r'^add/', AddGroupView.as_view(), name='add'),
    url(r'^asset_list/', AssetView.as_view(), name='asset_list'),
    url(r'^asset_add/', AddAssetView.as_view(), name='asset_add'),
    url(r'^asset_see/', SeeAssetView.as_view(), name='asset_see'),
    url(r'^asset_edit/', EditAssetView.as_view(), name='asset_edit'),
    url(r'^asset_del/', DelAssetView.as_view(), name='asset_del'),
    url(r'^asset_update', UpdateAssetView.as_view(), name='asset_update'),
    url(r'^send/key/', SendKeyView.as_view(), name='send_key'),
    url(r'^ssh/connect/', WebSshView.as_view(), name='web_ssh'),
    url(r'^upload/', UploadFileView.as_view(), name='upload'),
    url(r'^file/list/', FileListView.as_view(), name='file_list'),
    url(r'^file/edit/', FileEditView.as_view(), name='file_edit'),
    url(r'^web/ssh/', NewWebSshView.as_view(), name='webssh'),
]
