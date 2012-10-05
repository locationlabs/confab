"""
Test configuration file generation.
"""
from confab.files import get_conf_files, env_from_package
from confab.tests.utils import Options

from jinja2 import UndefinedError
from unittest import TestCase

class TestFiles(TestCase):
    
    def setUp(self):
        self.env = env_from_package('confab.tests')

    def test_get_conf_files(self):
        """
        Generating conf files finds all templates in the package
        and generates their names properly.
        """

        with Options(get_configuration_data = lambda: {'bar': 'bar'}):
            conf_files = get_conf_files(self.env)

            self.assertEquals(2, len(conf_files))

            names = map(lambda x: x.name, conf_files)
            
            self.assertTrue('foo.txt' in names)
            self.assertTrue('bar/bar.txt' in names)

    def test_undefined(self):
        """
        Raise an error if a template value is undefined.
        """

        with Options(get_configuration_data = lambda: {}):
            with self.assertRaises(UndefinedError):
                conf_files = get_conf_files(self.env)
            
    def test_filter_func(self):
        """
        Passing a filter_func limits which templates are generated.
        """

        with Options(filter_func = lambda file_name: file_name != 'foo.txt',
                     get_configuration_data = lambda: {'bar': 'bar'}):
            conf_files = get_conf_files(self.env)

            self.assertEquals(1, len(conf_files))

            names = map(lambda x: x.name, conf_files)

            self.assertTrue('bar/bar.txt' in names)

