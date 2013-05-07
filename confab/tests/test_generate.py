"""
Tests for template generation.
"""
from unittest import TestCase
from fabric.api import settings
from jinja2 import UndefinedError
from os.path import join, dirname
import filecmp

from confab.conffiles import ConfFiles
from confab.loaders import PackageEnvironmentLoader, FileSystemEnvironmentLoader
from confab.options import Options
from confab.tests.utils import TempDir


class TestGenerate(TestCase):

    def setUp(self):
        self.settings = dict(roledefs={'role': ['localhost']},
                             host_string='localhost',
                             role='role')

    def test_generate(self):
        """
        Generated templates have the correct values.
        """
        with settings(**self.settings):
            conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests', 'templates/default'),
                                  lambda _: {'bar': 'bar', 'foo': 'foo'})

            with TempDir() as tmp_dir:
                conffiles.generate(tmp_dir.path)

                # foo.txt is populated with 'foo'
                self.assertEquals('foo', tmp_dir.read('localhost/foo.txt'))

                # bar.txt is populated with 'bar' and path is substituted
                self.assertEquals('bar', tmp_dir.read('localhost/bar/bar.txt'))

    def test_unicode(self):
        """
        Generated templates with unicode data.
        """
        with settings(**self.settings):
            conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests', 'templates/default'),
                                  lambda _: {'bar': 'bar', 'foo': u'\xc5\xae'})
            with TempDir() as tmp_dir:
                conffiles.generate(tmp_dir.path)

                # foo.txt is populated with u'\xc5\xae'
                self.assertEquals(u'\xc5\xae', tmp_dir.read('localhost/foo.txt'))

                # bar.txt is populated with 'bar' and path is substituted
                self.assertEquals('bar', tmp_dir.read('localhost/bar/bar.txt'))

    def test_undefined(self):
        """
        An exception is raised if a template value is undefined.
        """
        with settings(**self.settings):
            conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests', 'templates/default'),
                                  lambda _: {'bar': 'bar'})

            with TempDir() as tmp_dir:
                with self.assertRaises(UndefinedError):
                    conffiles.generate(tmp_dir.path)

    def test_should_render(self):
        """
        Passing a mime_type_func controls whether templates are rendered.
        """
        with Options(should_render=lambda mime_type: False):
            with settings(**self.settings):
                conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests', 'templates/default'),
                                      lambda _: {'bar': 'bar', 'foo': 'foo'})

                with TempDir() as tmp_dir:
                    conffiles.generate(tmp_dir.path)

                    # templates not rendered (though paths are)
                    self.assertEquals('{{foo}}', tmp_dir.read('localhost/foo.txt'))
                    self.assertEquals('{{bar}}', tmp_dir.read('localhost/bar/bar.txt'))

    def test_binary_template(self):
        """
        Confab copies binary config files verbatim to generated folder.
        """
        with settings(**self.settings):
            templates_dir = join(dirname(__file__), 'templates/binary')
            conffiles = ConfFiles(FileSystemEnvironmentLoader(templates_dir), lambda _: {})

            with TempDir() as tmp_dir:
                conffiles.generate(tmp_dir.path)

                self.assertTrue(filecmp.cmp(join(tmp_dir.path, 'localhost/test.png'),
                                            join(templates_dir, 'role/test.png')))

    def test_components(self):
        """
        Generate templates for roles with components.
        """
        with settings(roledefs={'role1': ['host1'],
                                'role2': ['host1']},
                      componentdefs={'role1': ['comp1'],
                                     'role2': ['compgroup'],
                                     'compgroup': ['comp2', 'comp3']},
                      host_string='host1'):

            with TempDir() as tmp_dir:
                for role in ['role1', 'role2']:
                    with settings(role=role):
                        conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests',
                                                                       'templates/components'),
                                              lambda _: {'bar': 'bar', 'foo': 'foo', 'baz': 'baz'})

                        conffiles.generate(tmp_dir.path)

                self.assertEquals('foo', tmp_dir.read('host1/role1.txt'))
                self.assertEquals('foo', tmp_dir.read('host1/foo.txt'))
                self.assertEquals('bar', tmp_dir.read('host1/bar/bar.txt'))
                self.assertEquals('baz', tmp_dir.read('host1/baz.conf'))
