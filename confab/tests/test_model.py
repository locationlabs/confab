"""
Test model functions.
"""

from confab.model import get_roles_for_host, get_hosts_for_environment

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
