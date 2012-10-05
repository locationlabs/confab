"""
Test configuration file listing.
"""
from confab.files import get_conf_files
from confab.loaders import load_from_package
from confab.options import Options

from jinja2 import UndefinedError
from unittest import TestCase

class TestFiles(TestCase):
    
    def test_get_conf_files(self):
        """
        Generating conf files finds all templates in the package
        and generates their names properly.
        """

        with Options(get_jinja2_environment = lambda: load_from_package('confab.tests'),
                     get_configuration_data = lambda: {'bar': 'bar'}):
            conf_files = get_conf_files()

            self.assertEquals(2, len(conf_files))

            names = map(lambda x: x.name, conf_files)
            
            self.assertTrue('foo.txt' in names)
            self.assertTrue('bar/bar.txt' in names)

    def test_undefined(self):
        """
        Raise an error if a template value is undefined.
        """

        with Options(get_jinja2_environment = lambda: load_from_package('confab.tests'),
                     get_configuration_data = lambda: {}):
            with self.assertRaises(UndefinedError):
                conf_files = get_conf_files()
            
    def test_filter_func(self):
        """
        Passing a filter_func limits which templates are generated.
        """

        with Options(filter_func = lambda file_name: file_name != 'foo.txt',
                     get_jinja2_environment = lambda: load_from_package('confab.tests'),
                     get_configuration_data = lambda: {'bar': 'bar'}):
            conf_files = get_conf_files()

            self.assertEquals(1, len(conf_files))

            names = map(lambda x: x.name, conf_files)

            self.assertTrue('bar/bar.txt' in names)

