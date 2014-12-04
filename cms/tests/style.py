import os

from django.utils.unittest import TestCase
from pep8 import REPORT_FORMAT
from pep8 import StandardReport
from pep8 import StyleGuide
from pyflakes.api import checkPath
from pyflakes.api import iterSourceCode
from pyflakes.reporter import Reporter

import cms
from cms.utils.compat.string_io import StringIO
import menus


class PyflakesTestReporter(Reporter):
    def __init__(self, stream):
        super(PyflakesTestReporter, self).__init__(stream, stream)


class PEP8BaseReport(StandardReport):
    def __init__(self, options):
        super(StandardReport, self).__init__(options)
        self._fmt = REPORT_FORMAT.get(
            options.format.lower(),
            options.format
        )

    def init_file(self, filename, lines, expected, line_offset):
        """Signal a new file."""
        self._deferred_print = []
        return super(StandardReport, self).init_file(
            filename, lines, expected, line_offset
        )

    def error(self, line_number, offset, text, check):
        """Report an error, according to options."""
        code = super(StandardReport, self).error(
            line_number, offset, text, check
        )
        if code:
            self._deferred_print.append(
                (line_number, offset, code, text[5:], check.__doc__)
            )
        return code

    def get_file_results(self):
        """Print the result and return the overall count for this file."""
        self._deferred_print.sort()
        lines = []
        for line_number, offset, code, text, doc in self._deferred_print:
            lines.append(self._fmt % {
                'path': self.filename,
                'row': self.line_offset + line_number, 'col': offset + 1,
                'code': code, 'text': text,
            })
        return '\n'.join(lines)


def pyflakes_test_method_factory(method_name, path):
    def test_method(self):
        stream = StringIO()
        reporter = PyflakesTestReporter(stream)
        if checkPath(path, reporter):
            self.fail('\n{0}'.format(stream.getvalue()))
    test_method.__name__ = method_name
    return test_method


def pep8_test_method_factory(method_name, path):
    def test_method(self):
        style_guide = StyleGuide(paths=[path])
        style_guide.options.reporter = PEP8BaseReport
        style_guide.options.verbose = False
        style_guide.init_report()
        report = style_guide.check_files()
        if report.get_count():
            self.fail('\n{0}'.format(report.get_file_results()))
    test_method.__name__ = method_name
    return test_method


def path_to_method_name(base, path):
    return os.path.relpath(path, base).replace(os.path.sep, '__')


def build_test_case(name, method_factory, source, ignore_paths):
    methods = {}
    base = 'test_{0}__'.format(os.path.basename(source.rstrip(os.path.sep)))
    for path in iterSourceCode([source]):
        if path.startswith(tuple(ignore_paths)):
            continue
        method_name = '{0}{1}'.format(base, path_to_method_name(source, path))
        methods[method_name] = method_factory(method_name, path)

    return type(name, (TestCase,), methods)


cms_path = os.path.abspath(os.path.dirname(cms.__file__))
cms_migrations = os.path.join(cms_path, 'migrations')
cms_django_migrations = os.path.join(cms_path, 'migrations_django')
menus_path = os.path.abspath(os.path.dirname(menus.__file__))
menus_migrations = os.path.join(menus_path, 'migrations')
menus_django_migrations = os.path.join(menus_path, 'migrations_django')

CMSPyflakesTests = build_test_case(
    'CMSPyflakesTests',
    pyflakes_test_method_factory,
    cms_path,
    [cms_migrations, cms_django_migrations]
)
MenusPyflakesTests = build_test_case(
    'MenusPyflakesTests',
    pyflakes_test_method_factory,
    menus_path,
    [menus_migrations, menus_django_migrations]
)
CMSPEP8Tests = build_test_case(
    'CMSPEP8Tests',
    pep8_test_method_factory,
    cms_path,
    [cms_migrations, cms_django_migrations]
)
MenusPEP8Tests = build_test_case(
    'MenusPEP8Tests',
    pep8_test_method_factory,
    menus_path,
    [menus_migrations, menus_django_migrations]
)
