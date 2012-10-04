from confab.files import get_conf_files, env_from_package
from confab.generate import generate_conf_files
from confab.options import get_default_options
from confab.tests.utils import TempDir

from fabric.api import hide, settings
from jinja2 import UndefinedError
from unittest import TestCase

class TestGenerate(TestCase):
    
    def setUp(self):
        self.env = env_from_package('confab.tests')
        self.data = {'bar': 'bar', 'foo': 'foo'}
        self.options = get_default_options()

    def test_generate(self):
        """
        Generated templates have the correct values.
        """
        conf_files = get_conf_files(self.env, self.data, self.options)

        with settings(hide('user'),
                      host_string = 'localhost'):
            with TempDir() as tmp_dir: 
                generate_conf_files(conf_files, tmp_dir.path)

                # foo.txt is populated with 'foo'
                self.assertEquals('foo', tmp_dir.read('localhost/foo.txt'))

                # bar.txt is populated with 'bar' and path is substituted
                self.assertEquals('bar', tmp_dir.read('localhost/bar/bar.txt'))

    def test_undefined(self):
        """
        An exception is raised if a template value is undefined.
        """
        conf_files = get_conf_files(self.env, self.data, self.options)

        del self.data['foo']
        with settings(hide('user'),
                      host_string = 'localhost'):
            with TempDir() as tmp_dir:
                with self.assertRaises(UndefinedError):
                    generate_conf_files(conf_files, tmp_dir.path)

                    
    def test_is_text(self):
        """
        Passing a mime_type_func controls whether templates are rendered.
        """
        conf_files = get_conf_files(self.env, self.data, self.options)

        self.options.is_text = lambda mime_type: False


        with settings(hide('user'),
                      host_string = 'localhost'):
            with TempDir() as tmp_dir:
                generate_conf_files(conf_files, tmp_dir.path)

                # templates not rendered (though paths are)
                self.assertEquals('{{foo}}', tmp_dir.read('localhost/foo.txt'))
                self.assertEquals('{{bar}}', tmp_dir.read('localhost/bar/bar.txt'))
