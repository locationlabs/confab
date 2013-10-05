"""
Tests for custom Jinja filters.
"""
from unittest import TestCase
from nose.tools import eq_

from confab.conffiles import ConfFiles
from confab.definitions import Settings
from confab.loaders import PackageEnvironmentLoader
from confab.api import JinjaFilters
from confab.tests.utils import TempDir


class TestJinjaFilters(TestCase):

    def setUp(self):
        self.settings = Settings()
        self.settings.environmentdefs = {
            'any': ['localhost'],
        }
        self.settings.roledefs = {
            'role': ['localhost'],
        }

    def test_built_in_filters(self):
        """
        Generated templates that use built-in filters have the correct values.
        """
        conffiles = ConfFiles(self.settings.for_env('any').all().next(),
                              PackageEnvironmentLoader('confab.tests',
                                                       'templates/jinjafilters/builtin'),
                              lambda _: {
                                  'bar': [1, 2, 3],
                                  'pivot': 2,
                                  'foo': {
                                      'key1': 'foo1',
                                      'key2': 'foo2',
                                  },
                                  'key': 'key2',
                              })

        with TempDir() as tmp_dir:
            conffiles.generate(tmp_dir.path)

            eq_('foo2', tmp_dir.read('generated/localhost/foo.txt'))

            eq_("['+2+', '+3+', '+1+']", tmp_dir.read('generated/localhost/bar/bar.txt'))

    def test_user_filters(self):
        """
        Generated templates that use user-defined filters have the correct values.
        """
        def multiply(value, mult):
            return value * mult

        with JinjaFilters(multiply):
            conffiles = ConfFiles(self.settings.for_env('any').all().next(),
                                  PackageEnvironmentLoader('confab.tests',
                                                           'templates/jinjafilters/user'),
                                  lambda _: {'foo': 'foo'})

        with TempDir() as tmp_dir:
            conffiles.generate(tmp_dir.path)

            eq_('foofoofoo', tmp_dir.read('generated/localhost/foo.txt'))
