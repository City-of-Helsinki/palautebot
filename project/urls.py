
# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^sysadmin/', include(admin.site.urls)),
]


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

