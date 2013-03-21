"""
Test configuration file listing.
"""
from confab.conffiles import ConfFiles
from confab.loaders import PackageEnvironmentLoader
from confab.options import Options

from jinja2 import UndefinedError
from unittest import TestCase
from fabric.api import settings


class TestListing(TestCase):

    def setUp(self):
        self.settings = dict(roledefs={'role': ['host']},
                             componentdefs={},
                             role='role')

    def test_get_conf_files(self):
        """
        Generating conf files finds all templates in the package
        and generates their names properly.
        """

        with settings(**self.settings):
            conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests'),
                                  lambda _: {'bar': 'bar'})

            self.assertEquals(2, len(conffiles.conffiles))

            names = map(lambda x: x.name, conffiles.conffiles)

            self.assertTrue('foo.txt' in names)
            self.assertTrue('bar/bar.txt' in names)

    def test_undefined(self):
        """
        Raise an error if a template value is undefined.
        """

        with self.assertRaises(UndefinedError):
            with settings(**self.settings):
                ConfFiles(PackageEnvironmentLoader('confab.tests'), lambda _: {})

    def test_filter_func(self):
        """
        Passing a filter_func limits which templates are generated.
        """

        with Options(filter_func=lambda file_name: file_name != 'foo.txt'):
            with settings(**self.settings):

                conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests'),
                                      lambda _: {'bar': 'bar'})

                self.assertEquals(1, len(conffiles.conffiles))

                names = map(lambda x: x.name, conffiles.conffiles)

                self.assertTrue('bar/bar.txt' in names)
