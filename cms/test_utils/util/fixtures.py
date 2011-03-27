from cms.test_utils.util.context_managers import (
    SettingsOverride) # pragma: no cover
from django.conf import settings # pragma: no cover
from django.core.management import call_command # pragma: no cover
from django.core.serializers import serialize, deserialize
from django.db import connections # pragma: no cover
from django.db.models.signals import pre_save, post_save
import os # pragma: no cover


class Fixture(object): # pragma: no cover
    DB_OVERRIDE = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }

    def __init__(self, name, apps=['cms'], **settings_overrides):
        self.name = name
        self.apps = apps
        self.settings_overrides = settings_overrides
        
    def start(self):
        self.so = SettingsOverride(**self.settings_overrides)
        self.so.__enter__()
        self.old_db = connections.databases['default'] 
        connections.databases['default'] = self.DB_OVERRIDE
        if 'default' in connections._connections:
            del connections._connections['default']
        call_command('syncdb', migrate_all=True, interactive=False, verbosity=0)
    
    def save(self):
        filename = os.path.join(settings.FIXTURE_DIRS[0], self.name)
        with open(filename, 'wb') as fobj:
            call_command('dumpdata', *self.apps, stdout=fobj)
        self.so.__exit__(None, None, None)
        connections.databases['default'] = self.old_db
        if 'default' in connections._connections:
            del connections._connections['default']

_FIXTURE_STORE = {}

class _Fixturize(dict):
    def listen(self, instance, *args, **kwargs):
        model_name = instance._meta.object_name.lower()
        app_label = instance._meta.app_label
        if app_label not in self:
            self[app_label] = {}
        if model_name not in self[app_label]:
            self[app_label][model_name] = {}
        self[app_label][model_name][instance.pk] = serialize('python', [instance])
        
    def load(self):
        pre_save_receivers = pre_save.receivers
        pre_save.receivers = []
        post_save_receivers = post_save.receivers
        post_save.receivers = []
        for models in self.values():
            for instances in models.values():
                for data in instances.values():
                    objects = deserialize('python', data)
                    for obj in objects:
                        obj.save()
        pre_save.receivers = pre_save_receivers
        post_save.receivers = post_save_receivers
    

def fixturize(method):
    def _decorated(self, *args, **kwargs):
        if method in _FIXTURE_STORE:
            _FIXTURE_STORE[method].load()
        else:
            _fixturize = _Fixturize()
            post_save.connect(_fixturize.listen, weak=False, dispatch_uid=method)
            method(self, *args, **kwargs)
            post_save.disconnect(_fixturize.listen, weak=False, dispatch_uid=method)
            _FIXTURE_STORE[method] = _fixturize
    _decorated.__name__ = method.__name__
    return _decorated