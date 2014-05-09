from cms.utils.compat import PY2

if not PY2:
    import os

    from viceroy.api import build_test_case
    from viceroy.contrib.django import ViceroyDjangoTestCase
    from viceroy.contrib.jasmine import JasmineScanner

    from cms.api import create_page
    from cms.test_utils.testcases import CMSTestCase

    class BaseTestCase(ViceroyDjangoTestCase, CMSTestCase):
        def setUp(self):
            super(BaseTestCase, self).setUp()
            create_page('Home', 'nav_playground.html', 'en')


    BasicJasmineTests = build_test_case(
        'BasicJasmineTests',
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'static', 'tests.js')
        ),
        JasmineScanner,
        BaseTestCase,
        viceroy_url='/'
    )
