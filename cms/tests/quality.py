from unittest import TestCase
import os

from codequality.main import CodeQuality

import cms
from cms.test_utils.util.context_managers import StdoutOverride
import menus


class CodeQualityTest(TestCase):
    def test_codequality(self):
        cms_path = os.path.abspath(os.path.dirname(cms.__file__))
        menus_path = os.path.abspath(os.path.dirname(menus.__file__))
        options = type('Options', (object, ), {
            'scmhandler': None,
            'ignores': [
                '*/cms/migrations/*',
                '*/menus/migrations/*',
                '*/cms/static/cms/js/libs/*',
                '*/cms/static/cms/js/jstree/*',
                '*/cms/static/cms/js/plugins/jquery.ui.custom.js',
                '*/cms/static/cms/js/plugins/jquery.ui.nestedsortable.js',
            ],
            'verbose': False,
            'ignore_untracked': False,
            'list_checkers': False,
            'rev': None,
        })
        paths = [
            cms_path,
            menus_path,
        ]
        with StdoutOverride() as output:
            errs = CodeQuality(options).codequality(paths)
            self.assertFalse(errs, output.getvalue())
