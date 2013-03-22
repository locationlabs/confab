"""
Test configuration file listing.
"""
from confab.conffiles import ConfFiles
from confab.loaders import PackageEnvironmentLoader
from confab.options import Options

from jinja2 import UndefinedError
from unittest import TestCase
from fabric.api import settings
from os.path import dirname
from mock import patch


class TestListing(TestCase):

    def setUp(self):
        self.settings = dict(roledefs={'role': ['host']},
                             componentdefs={},
                             host_string='host',
                             role='role')

    def test_get_conf_files(self):
        """
        Generating conf files finds all templates in the package
        and generates their names properly.
        """

        with settings(**self.settings):
            conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests', 'templates/default'),
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
                ConfFiles(PackageEnvironmentLoader('confab.tests', 'templates/default'),
                          lambda _: {})

    def test_filter_func(self):
        """
        Passing a filter_func limits which templates are generated.
        """

        with Options(filter_func=lambda file_name: file_name != 'foo.txt'):
            with settings(**self.settings):

                conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests', 'templates/default'),
                                      lambda _: {'bar': 'bar'})

                self.assertEquals(1, len(conffiles.conffiles))

                names = map(lambda x: x.name, conffiles.conffiles)

                self.assertTrue('bar/bar.txt' in names)

    def test_same_component_for_different_roles(self):
        """
        Two roles using the same component on the same host.
        """

        with settings(roledefs={'role1': ['host'],
                                'role2': ['host']},
                      componentdefs={'role1': ['comp'],
                                     'role2': ['comp']},
                      host_string='host'):

            environment_loader = PackageEnvironmentLoader('confab.tests', 'templates/validate')

            # use data that will create different conffiles for the same
            # component in the two roles.
            data_loader = lambda comp: {'foo': dirname(comp)}

            with settings(role='role1'):
                conffiles = ConfFiles(environment_loader, data_loader)

                self.assertEquals(1, len(conffiles.conffiles))
                self.assertTrue('role1.txt' == conffiles.conffiles[0].name)

            with settings(role='role2'):
                conffiles = ConfFiles(environment_loader, data_loader)

                self.assertEquals(1, len(conffiles.conffiles))
                self.assertTrue('role2.txt' == conffiles.conffiles[0].name)

            # change the data loader so that both roles end up having
            # the same config file.
            data_loader = lambda _: {'foo': 'foo'}

            with settings(role='role1'):
                with self.assertRaises(Exception):
                    conffiles = ConfFiles(environment_loader, data_loader)

            with settings(role='role2'):
                with self.assertRaises(Exception):
                    conffiles = ConfFiles(environment_loader, data_loader)

    def test_warn_no_conffiles(self):
        """
        Warn when a role doesn't have any configuration files.
        """
        with settings(**self.settings):

            with Options(filter_func=lambda _: False):
                with patch('confab.conffiles.warn') as warn_mock:
                    conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests',
                                                                   'templates/default'),
                                          lambda _: {})

                    self.assertEquals(0, len(conffiles.conffiles))
                    self.assertTrue(warn_mock.called)
