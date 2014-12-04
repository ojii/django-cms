import os

from django.utils.unittest import TestCase
from pyflakes.api import checkPath
from pyflakes.api import iterSourceCode
from pyflakes.reporter import Reporter

import cms
from cms.utils.compat.string_io import StringIO
import menus


class TestReporter(Reporter):
    def __init__(self, stream):
        super(TestReporter, self).__init__(stream, stream)


def test_method_factory(method_name, path):
    def test_method(self):
        stream = StringIO()
        reporter = TestReporter(stream)
        if checkPath(path, reporter):
            self.fail(stream.getvalue())
    test_method.__name__ = method_name
    return test_method


def path_to_method_name(base, path):
    return os.path.relpath(path, base).replace(os.path.sep, '__')


def build_test_case(name, source):
    methods = {}
    base = 'test_{0}__'.format(os.path.basename(source.rstrip(os.path.sep)))
    for path in iterSourceCode([source]):
        method_name = '{0}{1}'.format(base, path_to_method_name(source, path))
        methods[method_name] = test_method_factory(method_name, path)

    return type(name, (TestCase,), methods)


cms_path = os.path.abspath(os.path.dirname(cms.__file__))
menus_path = os.path.abspath(os.path.dirname(menus.__file__))

CMSPyflakesTests = build_test_case('CMSPyflakesTests', cms_path)
MenusPyflakesTests = build_test_case('MenusPyflakesTests', menus_path)
