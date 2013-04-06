"""
Test definition functions.
"""
from os.path import dirname, join
from nose.tools import eq_
from unittest import TestCase
from warnings import catch_warnings

from confab.definitions import Settings


class TestSettings(TestCase):
    """
    Tests for loading Settings.
    """

    def setUp(self):
        self.dir_name = join(dirname(__file__), "data/default")
        self.settings = Settings()

    def test_load_from_empty_module(self):
        """
        Loading empty state results in empty dictionaries.
        """
        self.settings.load_from_module(dir_name=self.dir_name, module_name="empty")
        for key in Settings.KEYS:
            eq_({}, getattr(self.settings, key, {}))

    def test_load_from_empty_dict(self):
        """
        Loading empty state results in empty dictionaries.
        """
        self.settings.load_from_dict({})
        for key in Settings.KEYS:
            eq_({}, getattr(self.settings, key, {}))

    def test_load_from_example_module(self):
        """
        Loading non-empty module results in expected dictionaries.
        """
        self.settings.load_from_module(dir_name=self.dir_name, module_name="example")
        eq_(["host1", "host2"], self.settings.environmentdefs["environment1"])
        eq_(["host1"], self.settings.roledefs["role1"])
        eq_(["component1"], self.settings.componentdefs["role1"])

    def test_load_from_dict(self):
        """
        Loading empty state results in empty dictionaries.
        """
        dct = {
            "environmentdefs": {
                "environment1": ["host1", "host2"],
            },
            "roledefs": {
                "role1": ["host1"],
            },
            "componentdefs": {
                "role1": ["component1"],
            }
        }
        self.settings.load_from_dict(dct)
        eq_(["host1", "host2"], self.settings.environmentdefs["environment1"])
        eq_(["host1"], self.settings.roledefs["role1"])
        eq_(["component1"], self.settings.componentdefs["role1"])


class TestEnvironment(TestCase):
    """
    Tests for environment selection.
    """
    def setUp(self):
        self.dir_name = join(dirname(__file__), "data/default")
        self.settings = Settings()

    def test_no_environments(self):
        """
        Fail if there is no environments defined.
        """
        with self.assertRaises(Exception):
            self.settings.for_env("local")

    def test_unknown_environments(self):
        """
        Fail if an environment is unknown.
        """
        self.settings.environmentdefs = {
            "foo": ["bar"],
        }
        self.settings.roledefs = {
            "baz": ["bar"],
        }
        with self.assertRaises(Exception):
            self.settings.for_env("local")

    def test_environment(self):
        """
        Lookup by environments works.
        """
        self.settings.environmentdefs = {
            "foo": ["bar", "baz"],
            "bar": ["foo"],
        }
        self.settings.roledefs = {
            "role": ["foo", "bar", "baz"],
        }

        eq_({"bar": ["role"],
             "baz": ["role"]},
            self.settings.for_env("foo").host_roles)
        eq_({"foo": ["role"]},
            self.settings.for_env("bar").host_roles)

    def test_host_without_roles(self):
        """
        Fail if an environment host has no roles
        """
        self.settings.environmentdefs = {
            "foo": ["bar"],
        }
        self.settings.roledefs = {
        }

        with self.assertRaises(Exception):
            self.self.settings.for_env("foo")

    def test_select_hosts(self):
        """
        Selecting specific hosts works.
        """
        self.settings.environmentdefs = {
            "foo": ["bar", "baz"],
        }
        self.settings.roledefs = {
            "role": ["bar", "baz"],
        }

        eq_({"bar": ["role"]},
            self.settings.for_env("foo").with_hosts("bar").host_roles)
        eq_({"bar": ["role"],
             "baz": ["role"]},
            self.settings.for_env("foo").with_hosts("bar", "baz").host_roles)

    def test_select_unknown_hosts(self):
        """
        Fail if a selected host is not known.
        """
        self.settings.environmentdefs = {
            "foo": ["bar", "baz"],
            "other": ["blah"]
        }
        self.settings.roledefs = {
            "role": ["bar", "baz", "blah"],
        }
        with self.assertRaises(Exception):
            self.self.settings.for_env("foo").with_hosts("bad")
        with self.assertRaises(Exception):
            self.self.settings.for_env("foo").with_hosts("blah")

    def test_select_role(self):
        """
        Selecting specific roles works.
        """
        self.settings.environmentdefs = {
            "foo": ["bar", "baz"],
        }
        self.settings.roledefs = {
            "role1": ["bar", "baz"],
            "role2": ["bar"],
        }
        eq_({"bar": ["role1"],
             "baz": ["role1"]},
            self.settings.for_env("foo").with_roles("role1").host_roles)
        eq_({"bar": ["role2"]},
            self.settings.for_env("foo").with_roles("role2").host_roles)

    def test_select_unknown_role(self):
        """
        Fail if a selected role is not known.
        """
        self.settings.environmentdefs = {
            "foo": ["bar", "baz"],
        }
        self.settings.roledefs = {
            "role1": ["bar"],
            "role2": ["baz"],
        }
        with self.assertRaises(Exception):
            self.self.settings.for_env("foo").with_roles("bad")

    def test_select_roles_and_hosts(self):
        """
        Test key matching within roledefs.
        """
        self.settings.environmentdefs = {
            "foo": ["bar", "baz"],
        }
        self.settings.roledefs = {
            "role1": ["bar"],
            "role2": ["baz"],
        }
        eq_({"baz": ["role2"]},
            self.settings.for_env("foo").with_hosts("bar", "baz").with_roles("role2").host_roles)


class TestHostAndRole(TestCase):
    """
    Test host and role resolution.
    """
    def setUp(self):
        self.settings = Settings()
        self.settings.environmentdefs = {
            "test1": ["host1", "host2", "host3"],
            "test2": ["host2", "host3"],
            "test3": []
        }
        self.settings.roledefs = {
            "role1": ["host1", "host2", "host3"],
            "role2": ["host2", "host3"],
            "role3": [],
        }

    def test_resolve_only_environment(self):
        """
        Specifying only an environment, returns all of its hosts and roles.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1", "role2"],
             "host3": ["role1", "role2"]},
            self.settings.for_env("test1").host_roles)

    def test_resolve_only_empty_environment(self):
        """
        Specifying an empty environment generates a warning.
        """
        with catch_warnings(record=True) as caught_warnings:
            eq_({},
                self.settings.for_env("test3").host_roles)
        eq_(1, len(caught_warnings))

    def test_resolve_host_without_roles(self):
        """
        Explicit hosts return all of their roles.
        """
        eq_({"host1": ["role1"]},
            self.settings.for_env("test1").with_hosts("host1").host_roles)
        eq_({"host2": ["role1", "role2"]},
            self.settings.for_env("test1").with_hosts("host2").host_roles)

    def test_resolve_hosts_without_roles(self):
        """
        Explicit host list returns all hosts and all of their roles.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1", "role2"]},
            self.settings.for_env("test1").with_hosts("host1", "host2").host_roles)

    def test_resolve_role_without_hosts(self):
        """
        Explicit role returns all hosts in environment with that role.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1"],
             "host3": ["role1"]},
            self.settings.for_env("test1").with_roles("role1").host_roles)

    def test_resolve_roles_without_hosts(self):
        """
        Explicit role list returns all hosts in environment with any of those roles.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1", "role2"],
             "host3": ["role1", "role2"]},
            self.settings.for_env("test1").with_roles("role1", "role2").host_roles)

        eq_({"host2": ["role1", "role2"],
             "host3": ["role1", "role2"]},
            self.settings.for_env("test2").with_roles("role1", "role2").host_roles)

    def test_resolve_unknown_role_without_hosts(self):
        """
        Explicit role matching no hosts returns empty mapping.
        """
        eq_({},
            self.settings.for_env("test1").with_roles("role3").host_roles)

    def test_resolve_host_with_role(self):
        """
        Explicit host and role mappings return host and role.
        """
        eq_({"host1": ["role1"]},
            self.settings.for_env("test1").with_hosts("host1").with_roles("role1").host_roles)

    def test_resolve_hosts_with_role(self):
        """
        Explicit hosts and role mappings return role for all hosts.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1"]},
            self.settings.for_env("test1").with_hosts("host1", "host2").with_roles("role1").host_roles)

    def test_resolve_host_with_roles(self):
        """
        Explicit host and roles mappings return all roles applicable for host.
        """
        eq_({"host1": ["role1"]},
            self.settings.for_env("test1").with_hosts("host1").with_roles("role1", "role2").host_roles)
        eq_({"host2": ["role1", "role2"]},
            self.settings.for_env("test1").with_hosts("host2").with_roles("role1", "role2").host_roles)

    def test_resolve_hosts_with_roles(self):
        """
        Explicit hosts and roles mappings return all roles applicable for hosts.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1", "role2"]},
            self.settings.for_env("test1").with_hosts("host1", "host2").with_roles("role1", "role2").host_roles)


class TestComponents(TestCase):
    """
    Tests for component selection.
    """
    def setUp(self):
        self.settings = Settings()

    def test_components_for_role(self):
        """
        Test key matching within componentdefs.
        """
        self.settings.environmentdefs = {
            "env": ["host1", "host2"],
        }
        self.settings.roledefs = {
            "role1": ["host1"],
            "role2": ["host2"],
            "role3": ["host2"],
        }

        # no componentdefs is ok
        eq_([],
            map(lambda c: c.name, self.settings.for_env("env").components()))

        self.settings.componentdefs = {
            "role1": ["comp1", "compgroup"],
            "role2": ["comp2", "comp3"],
            "compgroup": ["comp3", "comp4"]
        }

        eq_(["comp1", "comp3", "comp4"],
            map(lambda c: c.name, self.settings.for_env("env").with_roles("role1").components()))
        eq_(["comp2", "comp3"],
            map(lambda c: c.name, self.settings.for_env("env").with_roles("role2").components()))
        eq_([],
            map(lambda c: c.name, self.settings.for_env("env").with_roles("role3").components()))

    def test_componentdefs_cycle(self):
        """
        Fail if componentdefs has cycles.
        """
        self.settings.environmentdefs = {
            "env": ["host1"],
        }
        self.settings.roledefs = {
            "role1": ["host1"],
        }
        self.settings.componentdefs = {
            "role1": ["compgroup"],
            "compgroup": ["role1"],
        }
        with self.assertRaises(Exception):
            map(lambda c: c.name, self.settings.for_env("env").with_roles("role1").components())

    def test_componentdefs_cycle2(self):
        """
        Fail if componentdefs has cycles.
        """
        self.settings.environmentdefs = {
            "env": ["host1"],
        }
        self.settings.roledefs = {
            "role1": ["host1"],
        }
        self.settings.componentdefs = {
            "role1": ["compgroup1"],
            "compgroup1": ["compgroup2"],
            "compgroup2": ["compgroup1"],
        }
        with self.assertRaises(Exception):
            map(lambda c: c.name, self.settings.for_env("env").with_roles("role1").components())

    def test_multiple_paths(self):
        """
        Fail if componentdefs has multiple paths to a leaf component.
        """
        self.settings.environmentdefs = {
            "env": ["host1"],
        }
        self.settings.roledefs = {
            "role1": ["host1"],
        }
        self.settings.componentdefs = {
            "role1": ["comp1", "compgroup"],
            "compgroup": ["comp1"],
        }
        with self.assertRaises(Exception):
            map(lambda c: c.name, self.settings.for_env("env").with_roles("role1").components())
