"""
Test model functions.
"""
from os.path import dirname, join
from nose.tools import eq_, ok_
from confab.model import (_keys,
                          get_roles_for_host,
                          get_hosts_for_environment,
                          get_components_for_role,
                          load_model_from_dir)

from fabric.api import env, settings
from unittest import TestCase
from contextlib import contextmanager


@contextmanager
def empty_defs():
    """
    Make sure fabric env changes are local.

    Using confab.model.load_model_from_dir will change env settings.
    Use this context manager to make the changes local to the test.
    """
    with settings(environmentdefs={},
                  roledefs={},
                  componentdefs={}):
        # Any changes to the settings above will be reverted
        # once the with block closes.
        yield


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

        with empty_defs():
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

        with empty_defs():
            load_model_from_dir(dir_name=self.dir_name, module_name="example")
            eq_(["host1", "host2"], env.environmentdefs["environment1"])
            eq_(["host1"], env.roledefs["role1"])
            eq_(["component1"], env.componentdefs["role1"])

    def test_get_components_for_role(self):
        """
        Test key matching within componentdefs.
        """

        # no componentdefs is ok
        with settings(roledefs={'role1': ['host1']},
                      componentdefs={}):
            eq_([], get_components_for_role('role1'))

        with settings(roledefs={'role1': ['host1'],
                                'role2': ['host2'],
                                'role3': ['host2']},
                      componentdefs={'role1': ['comp1', 'compgroup'],
                                     'role2': ['comp2', 'comp3'],
                                     'compgroup': ['comp3', 'comp4']}):

            eq_(['comp1', 'comp3', 'comp4'],
                get_components_for_role('role1'))

            eq_(['comp2', 'comp3'],
                get_components_for_role('role2'))

            eq_([], get_components_for_role('role3'))

            with self.assertRaises(Exception):
                get_components_for_role('foo')

    def test_identify_componentdefs_problems(self):
        """
        Test model raises exception if componentdefs has cycles or
        components with multiple paths.
        """

        with settings(roledefs={'role1': ['host1']},
                      componentdefs={'role1': ['compgroup'],
                                     'compgroup': ['role1']}):
            with self.assertRaises(Exception):
                get_components_for_role('role1')

        with settings(roledefs={'role1': ['host1']},
                      componentdefs={'role1': ['compgroup1'],
                                     'compgroup1': ['compgroup2'],
                                     'compgroup2': ['compgroup1']}):
            with self.assertRaises(Exception):
                get_components_for_role('role1')

        with settings(roledefs={'role1': ['host1']},
                      componentdefs={'role1': ['comp1', 'compgroup'],
                                     'compgroup': ['comp1']}):
            with self.assertRaises(Exception):
                get_components_for_role('role1')
