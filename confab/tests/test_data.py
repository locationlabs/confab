"""
Tests for confab data model.
"""

from unittest import TestCase
from confab.data import import_configuration
from nose.tools import eq_
from os.path import dirname, join


class TestData(TestCase):

    def test_data_templates(self):

        data = import_configuration('bar', join(dirname(__file__), 'data/templates'))

        eq_(data,
            {'foo': 'foo',
             'bar': 'bar',
             'baz': {'n': 42}})
