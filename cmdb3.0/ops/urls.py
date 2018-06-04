"""dct_monitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
import os
from django.conf.urls.static import static
from asset.views import IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^user/', include('duser.urls', namespace='user')),
    url(r'^asset/', include('asset.urls', namespace='asset')),
    url(r'^monitor/', include('monitor.urls', namespace='monitor')),
    url(r'^command/', include('command.urls', namespace='command')),
    url(r'^alarm/', include('alarm.urls', namespace='alarm')),
]
if settings.DEBUG:
    media_root = os.path.join(settings.BASE_DIR, 'upload')
    urlpatterns += static('/upload/', document_root=media_root)
