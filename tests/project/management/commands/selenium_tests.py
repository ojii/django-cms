# -*- coding: utf-8 -*-
from cms.utils.django_load import iterload
from django.core.management.base import BaseCommand
from django.test.simple import DjangoTestSuiteRunner
import unittest


class Command(BaseCommand):
    def handle(self, *args, **options):
        suite = unittest.TestSuite()
        for module in iterload('selenium_tests'):
            suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(module))
        DjangoTestSuiteRunner(verbosity=1, failfast=False).run_suite(suite)
        