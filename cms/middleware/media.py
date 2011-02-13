# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured

class PlaceholderMediaMiddleware(object):
    def __init__(self):
        raise ImproperlyConfigured(
            "The PlaceholderMediaMiddleware has been deprecated and removed in "
            "favor of django-sekizai, please refer to the documentation for "
            "further information."
        )
        