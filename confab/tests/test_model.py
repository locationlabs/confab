"""
Test model functions.
"""
from os.path import dirname, join
from nose.tools import eq_, ok_
from confab.model import (_keys,
                          get_roles_for_host,
                          get_hosts_for_environment,
                          load_model_from_dir)

from fabric.api import env, settings
from unittest import TestCase


class TestModel(TestCase):

    def setUp(self):
        self.dir_name = join(dirname(__file__), "data")

    def test_get_roles_for_host(self):
        """
        Test key matching within roledefs.
        """

        with settings(roledefs={'foo': ['bar', 'baz'],
                                'bar': ['foo']}):

            ok_('bar' in get_roles_for_host('foo'))
            ok_('baz' not in get_roles_for_host('foo'))
            ok_('foo' in get_roles_for_host('bar'))
            ok_('baz' not in get_roles_for_host('bar'))
            ok_('foo' in get_roles_for_host('baz'))
            ok_('bar' not in get_roles_for_host('baz'))

    def test_get_hosts_for_environment(self):
        """
        Test dictionary lookup within environmentdefs.
        """

        # no environmentdefs
        with self.assertRaises(Exception):
            get_hosts_for_environment('foo')

        with settings(environmentdefs={'foo': ['bar', 'baz'],
                                       'bar': ['foo']}):

            ok_('bar' in get_hosts_for_environment('foo'))
            ok_('baz' in get_hosts_for_environment('foo'))
            ok_('foo' in get_hosts_for_environment('bar'))
            ok_('baz' not in get_hosts_for_environment('bar'))

            # no environmentdef
            with self.assertRaises(Exception):
                get_hosts_for_environment('baz')

    def test_load_empty_model(self):
        """
        Loading empty model state results in empty dictionaries.
        """
        for key in _keys():
            # env.roledefs is built into Fabric, so don't test for None explicilty
            ok_(not getattr(env, key, None))

        load_model_from_dir(dir_name=self.dir_name, module_name="empty")
        for key in _keys():
            eq_({}, getattr(env, key, None))

    def test_load_example_model(self):
        """
        Loading non-empty model state results in expected dictionaries.
        """
        for key in _keys():
            # env.roledefs is built into Fabric, so don't test for None explicilty
            ok_(not getattr(env, key, None))

        load_model_from_dir(dir_name=self.dir_name, module_name="example")
        eq_(["host1", "host2"], env.environmentdefs["environment1"])
        eq_(["host1"], env.roledefs["role1"])
