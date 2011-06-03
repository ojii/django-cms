# -*- coding: utf-8 -*-
from cms.test_utils.selenium_testcases import SeleniumTestCase


class ToolbarTests(SeleniumTestCase):
    def test_server_runs(self):
        self.selenium.open('/')