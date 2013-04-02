"""
Tests for confab data model.
"""

from unittest import TestCase
from nose.tools import eq_
from confab.data import import_configuration, DataLoader
from fabric.api import settings
from os.path import dirname, join


class TestData(TestCase):

    def setUp(self):

        self.settings = dict(environment='environment',
                             role='role',
                             host_string='host')

    def test_data_templates(self):

        data = import_configuration('bar', join(dirname(__file__), 'data/templates'))

        eq_(data,
            {'foo': 'foo',
             'bar': 'bar',
             'baz': {'n': 42}})

    def test_default_load_order(self):

        with settings(**self.settings):
            loader = DataLoader(join(dirname(__file__), 'data/order'))

            eq_(loader('component')['data'],
                {'default': 'component',
                 'component': 'role',
                 'role': 'environment',
                 'environment': 'host',
                 'host': 'host'})

    def test_custom_load_order(self):

        with settings(**self.settings):
            loader = DataLoader(join(dirname(__file__), 'data/order'),
                                data_modules=reversed(DataLoader.ALL))

            eq_(loader('component')['data'],
                {'default': 'default',
                 'component': 'component',
                 'role': 'role',
                 'environment': 'environment',
                 'host': 'host'})

    def test_custom_data_modules(self):

        with settings(**self.settings):
            loader = DataLoader(join(dirname(__file__), 'data/order'),
                                data_modules=['role',
                                              'host',
                                              'default',
                                              'environment',
                                              'component'])

            eq_(loader('component')['data'],
                {'default': 'component',
                 'component': 'component',
                 'role': 'environment',
                 'environment': 'environment',
                 'host': 'host'})
