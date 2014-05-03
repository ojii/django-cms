# -*- coding: utf-8 -*-
from cms.views import details
from django.conf import settings
from django.conf.urls import url, patterns

if settings.APPEND_SLASH:
    reg = url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', details, name='pages-details-by-slug')
else:
    reg = url(r'^(?P<slug>[0-9A-Za-z-_.//]+)$', details, name='pages-details-by-slug')

urlpatterns = [
    # Public pages
    url(r'^$', details, {'slug':''}, name='pages-root'),
    reg,
]

urlpatterns = patterns('', *urlpatterns)
