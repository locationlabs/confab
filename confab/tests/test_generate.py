"""
Tests for template generation.
"""
from fabric.api import settings
from unittest import TestCase
from jinja2 import UndefinedError
from os.path import join, dirname
from nose.tools import eq_, ok_
import filecmp

from confab.conffiles import ConfFiles
from confab.definitions import Settings
from confab.loaders import PackageEnvironmentLoader, FileSystemEnvironmentLoader
from confab.data import DataLoader
from confab.options import Options
from confab.tests.utils import TempDir


class TestGenerate(TestCase):

    def setUp(self):
        self.settings = Settings()
        self.settings.environmentdefs = {
            'any': ['localhost'],
        }
        self.settings.roledefs = {
            'role': ['localhost'],
        }

    def test_generate(self):
        """
        Generated templates have the correct values.
        """
        conffiles = ConfFiles(self.settings.for_env('any').all()[0],
                              PackageEnvironmentLoader('confab.tests', 'templates/default'),
                              lambda _: {'bar': 'bar', 'foo': 'foo'})

        with TempDir() as tmp_dir:
            conffiles.generate(tmp_dir.path)

            # foo.txt is populated with 'foo'
            eq_('foo', tmp_dir.read('localhost/foo.txt'))

            # bar.txt is populated with 'bar' and path is substituted
            eq_('bar', tmp_dir.read('localhost/bar/bar.txt'))

    def test_unicode(self):
        """
        Generated templates with unicode data.
        """
        conffiles = ConfFiles(self.settings.for_env('any').all()[0],
                              PackageEnvironmentLoader('confab.tests', 'templates/default'),
                              lambda _: {'bar': 'bar', 'foo': u'\xc5\xae'})
        with TempDir() as tmp_dir:
            conffiles.generate(tmp_dir.path)

            # foo.txt is populated with u'\xc5\xae'
            eq_(u'\xc5\xae', tmp_dir.read('localhost/foo.txt'))

            # bar.txt is populated with 'bar' and path is substituted
            eq_('bar', tmp_dir.read('localhost/bar/bar.txt'))

    def test_undefined(self):
        """
        An exception is raised if a template value is undefined.
        """
        conffiles = ConfFiles(self.settings.for_env('any').all()[0],
                              PackageEnvironmentLoader('confab.tests', 'templates/default'),
                              lambda _: {'bar': 'bar'})

        with TempDir() as tmp_dir:
            with self.assertRaises(UndefinedError):
                conffiles.generate(tmp_dir.path)

    def test_should_render(self):
        """
        Passing a mime_type_func controls whether templates are rendered.
        """
        with Options(should_render=lambda mime_type: False):
            conffiles = ConfFiles(self.settings.for_env('any').all()[0],
                                  PackageEnvironmentLoader('confab.tests', 'templates/default'),
                                  lambda _: {'bar': 'bar', 'foo': 'foo'})

            with TempDir() as tmp_dir:
                conffiles.generate(tmp_dir.path)

                # templates not rendered (though paths are)
                eq_('{{foo}}', tmp_dir.read('localhost/foo.txt'))
                eq_('{{bar}}', tmp_dir.read('localhost/bar/bar.txt'))

    def test_binary_template(self):
        """
        Confab copies binary config files verbatim to generated folder.
        """
        templates_dir = join(dirname(__file__), 'templates/binary')
        conffiles = ConfFiles(self.settings.for_env('any').all()[0],
                              FileSystemEnvironmentLoader(templates_dir), lambda _: {})

        with TempDir() as tmp_dir:
            conffiles.generate(tmp_dir.path)

            ok_(filecmp.cmp(join(tmp_dir.path, 'localhost/test.png'),
                            join(templates_dir, 'role/test.png')))

    def test_components(self):
        """
        Generate templates for roles with components.
        """
        self.settings.environmentdefs = {
            'any': ['host1'],
        }
        self.settings.roledefs = {
            'role1': ['host1'],
            'role2': ['host1'],
            'role3': ['host1'],
        }
        self.settings.componentdefs = {
            'role1': ['comp1'],
            'role2': ['compgroup'],
            'compgroup': ['comp2', 'comp3'],
        }
        with TempDir() as tmp_dir:
            for host_and_role in self.settings.for_env('any').iterall():
                with settings(role=host_and_role.role,
                              host_string=host_and_role.role):
                    conffiles = ConfFiles(host_and_role,
                                          PackageEnvironmentLoader('confab.tests',
                                                                   'templates/components'),
                                          DataLoader(join(dirname(__file__), 'data/components')))
                    conffiles.generate(tmp_dir.path)

            self.assertEquals('foo', tmp_dir.read('host1/foo.txt'))
            self.assertEquals('bar', tmp_dir.read('host1/bar/bar.txt'))
            self.assertEquals('baz', tmp_dir.read('host1/baz.conf'))
