from confab.files import get_conf_files, env_from_package
from confab.options import make_default_options

from jinja2 import UndefinedError
from unittest import TestCase

class TestFiles(TestCase):
    
    def setUp(self):
        self.env = env_from_package('confab.tests')
        self.data = {'bar': 'bar'}
        self.options = make_default_options()

    def test_get_conf_files(self):
        """
        Generating conf files finds all templates in the package
        and generates their names properly.
        """

        conf_files = get_conf_files(self.env, self.data, self.options)

        self.assertEquals(2, len(conf_files))

        names = map(lambda x: x.name, conf_files)

        self.assertTrue('foo.txt' in names)
        self.assertTrue('bar/bar.txt' in names)

    def test_undefined(self):
        """
        Raise an error if a template value is undefined.
        """

        del self.data['bar']
        with self.assertRaises(UndefinedError):
            conf_files = get_conf_files(self.env, self.data, self.options)

    def test_filter_func(self):
        """
        Passing a filter_func limits which templates are generated.
        """

        def filter_func(file_name):
            return file_name != 'foo.txt'
        self.options.filter_func = filter_func

        conf_files = get_conf_files(self.env, self.data, self.options)

        self.assertEquals(1, len(conf_files))

        names = map(lambda x: x.name, conf_files)

        self.assertTrue('bar/bar.txt' in names)

