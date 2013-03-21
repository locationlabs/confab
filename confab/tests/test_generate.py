"""
Tests for template generation.
"""
from unittest import TestCase
from fabric.api import hide, settings
from jinja2 import UndefinedError

from confab.conffiles import ConfFiles
from confab.loaders import PackageEnvironmentLoader
from confab.options import Options
from confab.tests.utils import TempDir


class TestGenerate(TestCase):

    def setUp(self):
        self.settings = dict(roledefs={'role': ['localhost']},
                             componentdefs={},
                             host_string='localhost',
                             role='role')

    def test_generate(self):
        """
        Generated templates have the correct values.
        """
        with settings(**self.settings):
            conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests'),
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
            conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests'),
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
            conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests'),
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
                conffiles = ConfFiles(PackageEnvironmentLoader('confab.tests'),
                                      lambda _: {'bar': 'bar', 'foo': 'foo'})

                with TempDir() as tmp_dir:
                    conffiles.generate(tmp_dir.path)

                    # templates not rendered (though paths are)
                    self.assertEquals('{{foo}}', tmp_dir.read('localhost/foo.txt'))
                    self.assertEquals('{{bar}}', tmp_dir.read('localhost/bar/bar.txt'))
