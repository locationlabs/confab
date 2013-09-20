"""
Tests for confab data model.
"""
from os.path import dirname, join
from nose.tools import eq_
from unittest import TestCase

from confab.data import import_configuration, DataLoader
from confab.definitions import Settings


class TestData(TestCase):

    def setUp(self):
        self.settings = Settings()
        self.settings.environmentdefs = {
            "environment": ["host"],
        }
        self.settings.roledefs = {
            "role": ["host"],
        }
        self.settings.componentdefs = {
            "role": ["component"],
        }
        self.component = self.settings.for_env("environment").components().next()

    def test_data_templates(self):
        """
        Data modules can be templates.

        This test loads the "bar.py_tmpl" file as a Jinja template and converts it
        into a Python module. In the process of resolving this template, the foo.py
        module is included (defining "foo") and the "baz.py" macro is evaluated
        (defining "baz").
        """

        data = import_configuration('bar', join(dirname(__file__), 'data/templates'))
        eq_(data,
            {'foo': 'foo',
             'bar': 'bar',
             'baz': {'n': 42}})

    def test_load_order(self):
        """
        Data modules are always loaded in the same order: default,
        component, role, environment, then host.
        """
        loader = DataLoader(join(dirname(__file__), 'data/order'))

        eq_(loader(self.component)['data'],
            {'default': 'default',
             'component': 'component',
             'role': 'role',
             'environment': 'environment',
             'host': 'host'})

    def test_custom_data_modules_load_order(self):
        """
        Defining custom data modules does not affect load order.
        """

        loader = DataLoader(join(dirname(__file__), 'data/order'),
                            data_modules=reversed(DataLoader.ALL))

        eq_(loader(self.component)['data'],
            {'default': 'default',
             'component': 'component',
             'role': 'role',
             'environment': 'environment',
             'host': 'host'})

    def test_custom_data_modules_selection(self):
        """
        Defining custom data modules may select specific modules to load.
        """

        loader = DataLoader(join(dirname(__file__), 'data/order'),
                            data_modules=['component',
                                          'host'])

        eq_(loader(self.component)['data'],
            {'role': 'component',
             'component': 'component',
             'environment': 'component',
             'host': 'host'})

    def test_nested_configuration_files(self):
        '''
        Load configuration data from nested folder structure.
        '''
        loader = DataLoader(join(dirname(__file__), 'data/nested'))

        eq_(loader(self.component)['data'],
            {'default': 'default',
             'component': 'component',
             'role': 'role',
             'environment': 'environment',
             'host': 'host'})

    def test_missing_data_module(self):
        """
        If a data module does not exist, it is ignored.
        """
        loader = DataLoader(join(dirname(__file__), 'data/missing'),
                            data_modules=['component'])

        # no module named component
        eq_(None, loader(self.component).get('data'))

    def test_broken_data_module(self):
        """
        If a data module has a broken import, an import error is raised.
        """
        loader = DataLoader(join(dirname(__file__), 'data/broken'),
                            data_modules=['component'])

        with self.assertRaises(ImportError):
            loader(self.component).get('data')

    def test_broken_data_template(self):
        """
        If a data template has a broken import, an import error is raised.
        """
        loader = DataLoader(join(dirname(__file__), 'data/broken'),
                            data_modules=['host'])

        with self.assertRaises(ImportError):
            loader(self.component).get('data')
