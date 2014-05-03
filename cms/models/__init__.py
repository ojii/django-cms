# -*- coding: utf-8 -*-
import threading
from cms.apphook_pool import apphook_pool
from django.conf import settings as d_settings
from django.core.urlresolvers import get_resolver, _resolver_cache
from .settingmodels import *  # nopyflakes
from .pagemodel import *  # nopyflakes
from .permissionmodels import *  # nopyflakes
from .placeholdermodel import *  # nopyflakes
from .pluginmodel import *  # nopyflakes
from .titlemodels import *  # nopyflakes
from .placeholderpluginmodel import *  # nopyflakes
from .static_placeholder import *  # nopyflakes

# must be last
from cms import signals as s_import  # nopyflakes


def validate_settings():
    if "django.core.context_processors.request" not in d_settings.TEMPLATE_CONTEXT_PROCESSORS:
        raise ImproperlyConfigured('django-cms needs django.core.context_processors.request in settings.TEMPLATE_CONTEXT_PROCESSORS to work correctly.')
    if 'mptt' not in d_settings.INSTALLED_APPS:
        raise ImproperlyConfigured('django-cms needs django-mptt installed.')
    if 'cms.middleware.multilingual.MultilingualURLMiddleware' in d_settings.MIDDLEWARE_CLASSES and 'django.middleware.locale.LocaleMiddleware' in d_settings.MIDDLEWARE_CLASSES:
        raise ImproperlyConfigured('django-cms MultilingualURLMiddleware replaces django.middleware.locale.LocaleMiddleware! Please remove django.middleware.locale.LocaleMiddleware from your MIDDLEWARE_CLASSES settings.')


def validate_dependencies():
    # check for right version of reversions
    if 'reversion' in d_settings.INSTALLED_APPS:
        from reversion.admin import VersionAdmin
        if not hasattr(VersionAdmin, 'get_urls'):
            raise ImproperlyConfigured('django-cms requires never version of reversion (VersionAdmin must contain get_urls method)')

validate_dependencies()
validate_settings()


class ApphookResolver(object):
    def __init__(self, resolver):
        self.resolver = resolver
        apphooks = [
            apphook_pool.get_apphook(key)
            for key, _ in apphook_pool.get_apphooks()
        ]
        self.apphook_resolvers = {
            apphook: get_resolver(apphook.urls[0]) for apphook in apphooks
        }
        self.cache = {}
        self.lock = threading.Lock()

    @property
    def url_patterns(self):
        return self.resolver.url_patterns

    @property
    def namespace_dict(self):
        namespace_dict = self.resolver.namespace_dict
        for resolver in self.apphook_resolvers.values():
            namespace_dict.update(resolver.namespace_dict)
        return namespace_dict

    @property
    def app_dict(self):
        app_dict = self.resolver.app_dict
        for resolver in self.apphook_resolvers.values():
            app_dict.update(resolver.app_dict)
        return app_dict

    def resolve(self, path):
        return self.resolver.resolve(path)

    def _reverse_with_prefix(self, lookup_view, _prefix, *args, **kwargs):
        try:
            return self.resolver._reverse_with_prefix(
                lookup_view, _prefix, *args, **kwargs
            )
        except NoReverseMatch:
            result = self._reverse_for_apphook(
                lookup_view, _prefix, *args, **kwargs
            )
            if result is None:
                raise
            else:
                return result

    def _reverse_for_apphook(self, lookup_view, _prefix, *args, **kwargs):
        result = None
        result_hook = None
        for apphook, resolver in self.apphook_resolvers.items():
            try:
                result = resolver._reverse_with_prefix(
                    lookup_view, _prefix, *args, **kwargs
                )
            except NoReverseMatch:
                pass
            else:
                result_hook = apphook
                break
        if result is not None:
            with self.lock:
                if result_hook not in self.cache:
                    try:
                        page = Page.objects.public().get(
                            application_urls=result_hook.__name__
                        )
                    except Page.DoesNotExist:
                        self.cache[result_hook] = None
                        return None
                    else:
                        self.cache[result_hook] = page
                page = self.cache[result_hook]
                if not page:
                    return None
            return page.get_absolute_url() + result.lstrip('/')
        else:
            return None


def install_apphook_url_resolver():
    if apphook_pool.get_apphooks():
        resolver = ApphookResolver(get_resolver(None))
        _resolver_cache[(None,)] = resolver


install_apphook_url_resolver()
