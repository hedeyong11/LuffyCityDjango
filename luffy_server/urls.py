"""luffy_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url,include
from django.contrib import admin
from arya.service import sites
from mentor import views as mentor_views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^admin/', sites.site.urls),
    url(r'^api/', include('api.urls')),

    # url(r'^api/(?P<version>\w+)/auth/$', views.AuthView.as_view()),
    # url(r'^test/', views.test),
    url(r'^admin/login/$', mentor_views.login),
    url(r'^admin/logout/$', mentor_views.logout),
    url(r'^admin/index/$', mentor_views.index),
]
