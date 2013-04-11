"""
Test configuration file listing.
"""
from fabric.api import settings
from jinja2 import UndefinedError
from nose.tools import eq_, ok_
from unittest import TestCase
from warnings import catch_warnings

from confab.conffiles import ConfFiles
from confab.definitions import Settings
from confab.loaders import PackageEnvironmentLoader
from confab.options import options, Options


class TestListing(TestCase):

    def setUp(self):
        self.settings = Settings()
        self.settings.environmentdefs = {
            'any': ['host'],
        }
        self.settings.roledefs = {
            'role': ['host'],
        }

    def test_get_conf_files(self):
        """
        Generating conf files finds all templates in the package
        and generates their names properly.
        """

        conffiles = ConfFiles(self.settings.for_env('any').all()[0],
                              PackageEnvironmentLoader('confab.tests', 'templates/default'),
                              lambda _: {'bar': 'bar'})

        eq_(2, len(conffiles.conffiles))

        names = map(lambda x: x.name, conffiles.conffiles)

        self.assertTrue('foo.txt' in names)
        self.assertTrue('bar/bar.txt' in names)

    def test_undefined(self):
        """
        Raise an error if a template value is undefined.
        """

        with self.assertRaises(UndefinedError):
            ConfFiles(self.settings.for_env('any').all()[0],
                      PackageEnvironmentLoader('confab.tests', 'templates/default'),
                      lambda _: {})

    def test_filter_func(self):
        """
        Passing a filter_func limits which templates are generated.
        """

        with Options(filter_func=lambda file_name: file_name != 'foo.txt'):
            conffiles = ConfFiles(self.settings.for_env('any').all()[0],
                                  PackageEnvironmentLoader('confab.tests', 'templates/default'),
                                  lambda _: {'bar': 'bar'})

            eq_(1, len(conffiles.conffiles))

            names = map(lambda x: x.name, conffiles.conffiles)

            self.assertTrue('bar/bar.txt' in names)

    def test_same_component_for_different_roles(self):
        """
        Two roles using the same component on the same host.
        """
        self.settings.roledefs = {
            'role1': ['host'],
            'role2': ['host'],
        }
        self.settings.componentdefs = {
            'role1': ['comp'],
            'role2': ['comp'],
        }
        environment_loader = PackageEnvironmentLoader('confab.tests', 'templates/validate')

        # use data that will create different conffiles for the same
        # component in the two roles.
        data_loader = lambda comp: {'foo': options.get_rolename()}

        with settings(role='role1'):
            conffiles = ConfFiles(self.settings.for_env('any').with_roles('role1').all()[0],
                                  environment_loader,
                                  data_loader)

            eq_(1, len(conffiles.conffiles))
            ok_('role1.txt' == conffiles.conffiles[0].name)

        with settings(role='role2'):
            conffiles = ConfFiles(self.settings.for_env('any').with_roles('role2').all()[0],
                                  environment_loader,
                                  data_loader)

            eq_(1, len(conffiles.conffiles))
            ok_('role2.txt' == conffiles.conffiles[0].name)

    def test_warn_no_conffiles(self):
        """
        Warn when a role doesn't have any configuration files.
        """
        with Options(filter_func=lambda _: False):
            with catch_warnings(record=True) as captured_warnings:
                conffiles = ConfFiles(self.settings.for_env('any').all()[0],
                                      PackageEnvironmentLoader('confab.tests',
                                                               'templates/default'),
                                      lambda _: {})

                eq_(0, len(conffiles.conffiles))
                eq_(1, len(captured_warnings))
