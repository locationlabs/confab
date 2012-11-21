"""
Test model functions.
"""

from confab.model import get_roles_for_host, get_hosts_for_environment, has_same_roles, has_roles

from fabric.api import settings
from unittest import TestCase


class TestModel(TestCase):

    def test_get_roles_for_host(self):
        """
        Test key matching within roledefs.
        """

        with settings(roledefs={'foo': ['bar', 'baz'],
                                'bar': ['foo']}):

            self.assertTrue('bar' in get_roles_for_host('foo'))
            self.assertFalse('baz' in get_roles_for_host('foo'))
            self.assertTrue('foo' in get_roles_for_host('bar'))
            self.assertFalse('baz' in get_roles_for_host('bar'))
            self.assertTrue('foo' in get_roles_for_host('baz'))
            self.assertFalse('bar' in get_roles_for_host('baz'))

    def test_get_hosts_for_environment(self):
        """
        Test dictionary lookup within environmentdefs.
        """

        with settings(environmentdefs={'foo': ['bar', 'baz'],
                                       'bar': ['foo']}):

            self.assertTrue('bar' in get_hosts_for_environment('foo'))
            self.assertTrue('baz' in get_hosts_for_environment('foo'))
            self.assertTrue('foo' in get_hosts_for_environment('bar'))
            self.assertFalse('baz' in get_hosts_for_environment('bar'))
            self.assertFalse('foo' in get_hosts_for_environment('baz'))
            self.assertFalse('bar' in get_hosts_for_environment('baz'))

    def test_has_same_roles(self):
        """
        Test role set intersection.
        """

        with settings(roledefs={'foo': ['bar', 'baz', 'foo'],
                                'bar': ['baz', 'foo']}):
            self.assertTrue(has_same_roles(['baz', 'foo']))
            self.assertFalse(has_same_roles(['bar', 'foo']))
            self.assertFalse(has_same_roles(['bar', 'baz']))

    def test_has_roles(self):
        """
        Test role superset check.
        """

        with settings(roledefs={'foo': ['bar', 'baz', 'foo'],
                                'bar': ['baz', 'foo']}):
            self.assertTrue(has_roles(['baz', 'foo'], ['foo', 'bar']))
            self.assertTrue(has_roles(['baz', 'foo'], ['foo']))
            self.assertFalse(has_roles(['baz', 'foo'], ['baz']))
            self.assertTrue(has_roles(['baz', 'bar'], ['foo']))
            self.assertFalse(has_roles(['baz', 'bar'], ['bar']))
