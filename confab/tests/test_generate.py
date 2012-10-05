"""
Tests for template generation.
"""
from confab.conffiles import ConfFiles
from confab.loaders import load_from_package
from confab.options import Options
from confab.tests.utils import TempDir
from fabric.api import hide, settings

from jinja2 import UndefinedError
from unittest import TestCase

class TestGenerate(TestCase):
    
    def test_generate(self):
        """
        Generated templates have the correct values.
        """
        conffiles = ConfFiles(load_from_package('confab.tests'),
                              {'bar': 'bar', 'foo': 'foo'})

        with settings(hide('user'),
                      host_string = 'localhost'):
            with TempDir() as tmp_dir:
                conffiles.generate(tmp_dir.path)

                # foo.txt is populated with 'foo'
                self.assertEquals('foo', tmp_dir.read('localhost/foo.txt'))

                # bar.txt is populated with 'bar' and path is substituted
                self.assertEquals('bar', tmp_dir.read('localhost/bar/bar.txt'))

    def test_undefined(self):
        """
        An exception is raised if a template value is undefined.
        """
        conffiles = ConfFiles(load_from_package('confab.tests'),
                              {'bar': 'bar'})

        with settings(hide('user'),
                      host_string = 'localhost'):
            with TempDir() as tmp_dir:
                with self.assertRaises(UndefinedError):
                    conffiles.generate(tmp_dir.path)

                    
    def test_should_render(self):
        """
        Passing a mime_type_func controls whether templates are rendered.
        """
        conffiles = ConfFiles(load_from_package('confab.tests'),
                              {'bar': 'bar', 'foo': 'foo'})

        with Options(should_render = lambda mime_type: False):
            with settings(hide('user'),
                          host_string = 'localhost'):
                with TempDir() as tmp_dir:
                    conffiles.generate(tmp_dir.path)

                    # templates not rendered (though paths are)
                    self.assertEquals('{{foo}}', tmp_dir.read('localhost/foo.txt'))
                    self.assertEquals('{{bar}}', tmp_dir.read('localhost/bar/bar.txt'))
