"""
Tests for host and role resolution.
"""
from unittest import TestCase
from warnings import catch_warnings
from fabric.api import env
from nose.tools import eq_
from confab.resolve import resolve_hosts_and_roles


class TestResolve(TestCase):

    def setUp(self):
        # define environments
        env.environmentdefs = {
            "test1": ["host1", "host2", "host3"],
            "test2": ["host2", "host3"],
            "test3": []
        }
        # define roles
        env.roledefs = {
            "role1": ["host1", "host2", "host3"],
            "role2": ["host2", "host3"]
        }

    def test_only_environment(self):
        """
        Specifying only an environment, returns all of its hosts and roles.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1", "role2"],
             "host3": ["role1", "role2"]},
            resolve_hosts_and_roles("test1"))

    def test_only_empty_environment(self):
        """
        Specifying an empty environment generates a warning.
        """
        with catch_warnings(record=True) as caught_warnings:
            eq_({},
                resolve_hosts_and_roles("test3"))
            eq_(1, len(caught_warnings))

    def test_only_unknown_environment(self):
        """
        Specifying only an unknown environment raises an exception.
        """
        with self.assertRaises(Exception):
            resolve_hosts_and_roles("test4")
        with self.assertRaises(Exception):
            resolve_hosts_and_roles("test4", [], ["role1"])
        with self.assertRaises(Exception):
            resolve_hosts_and_roles("test4", ["host1"], ["role1"])

    def test_host_without_roles(self):
        """
        Explicit hosts return all of their roles.
        """
        eq_({"host1": ["role1"]}, resolve_hosts_and_roles("test1", ["host1"]))
        eq_({"host2": ["role1", "role2"]}, resolve_hosts_and_roles("test1", ["host2"]))

    def test_unknown_host_without_roles(self):
        """
        Unknown host raises an exception.
        """
        with self.assertRaises(Exception):
            resolve_hosts_and_roles("test1", ["host4"])

    def test_host_without_roles_in_wrong_environment(self):
        """
        Explicit hosts have to be in the specified environment.
        """
        with self.assertRaises(Exception):
            resolve_hosts_and_roles("test2", ["host1"])

    def test_hosts_without_roles(self):
        """
        Explicit host list returns all hosts and all of their roles.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1", "role2"]},
            resolve_hosts_and_roles("test1", ["host1", "host2"]))

    def test_role_without_hosts(self):
        """
        Explicit role returns all hosts in environment with that role.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1"],
             "host3": ["role1"]},
            resolve_hosts_and_roles("test1", [], ["role1"]))

    def test_roles_without_hosts(self):
        """
        Explicit role list returns all hosts in environment with any of those roles.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1", "role2"],
             "host3": ["role1", "role2"]},
            resolve_hosts_and_roles("test1", [], ["role1", "role2"]))

        eq_({"host2": ["role1", "role2"],
             "host3": ["role1", "role2"]},
            resolve_hosts_and_roles("test2", [], ["role1", "role2"]))

    def test_unknown_role_without_hosts(self):
        """
        Explicit role matching no hosts returns empty mapping.
        """
        eq_({}, resolve_hosts_and_roles("test1", [], ["role4"]))

    def test_host_with_role_not_in_environment(self):
        """
        Explicit host with a role not in the specified environment raises error.
        """
        with self.assertRaises(Exception):
            resolve_hosts_and_roles("test2", ["host1"], ["role1"])

    def test_host_with_role(self):
        """
        Explicit host and role mappings return host and role.
        """
        eq_({"host1": ["role1"]},
            resolve_hosts_and_roles("test1", ["host1"], ["role1"]))

    def test_host_not_in_environment(self):
        """
        Explicit host not in specified environemnt raises error.
        """
        # Doesn't matter if host is in environment
        with self.assertRaises(Exception):
            resolve_hosts_and_roles("test2", ["host1"], ["role1"])

    def test_hosts_with_role(self):
        """
        Explicit hosts and role mappings return role for all hosts.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1"]},
            resolve_hosts_and_roles("test1", ["host1", "host2"], ["role1"]))

    def test_host_with_roles(self):
        """
        Explicit host and roles mappings return all roles applicable for host.
        """
        eq_({"host1": ["role1"]},
            resolve_hosts_and_roles("test1", ["host1"], ["role1", "role2"]))
        eq_({"host2": ["role1", "role2"]},
            resolve_hosts_and_roles("test1", ["host2"], ["role1", "role2"]))

    def test_hosts_with_roles(self):
        """
        Explicit hosts and roles mappings return all roles applicable for hosts.
        """
        eq_({"host1": ["role1"],
             "host2": ["role1", "role2"]},
            resolve_hosts_and_roles("test1", ["host1", "host2"], ["role1", "role2"]))
