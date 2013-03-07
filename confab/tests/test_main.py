"""
Tests for command line tool.
"""
from unittest import TestCase
from nose.tools import eq_
from mock import Mock
from fabric.api import env
from confab.main import resolve_model
from confab.model import get_roles_for_host


class TestMain(TestCase):

    def setUp(self):
        # define environments
        env.environmentdefs = {
            'test1': ['host1', 'host2', 'host3'],
            'test2': ['host2', 'host3'],
            'test3': []
        }
        # define hosts
        env.roledefs = {
            'role1': ['host1', 'host2', 'host3'],
            'role2': ['host2', 'host3']
        }

        # define a mock parser that raises an assertion
        self.parser = Mock()
        self.parser.error.side_effect = AssertionError()

        # define a mock set of parsed options
        self.options = Mock()

    def test_resolve_model_no_hosts(self):
        """
        Cannot resolve with no hosts defined.
        """
        self.options.environment = ''
        self.options.hosts = ''
        self.options.roles = ''
        with self.assertRaises(AssertionError):
            resolve_model(self.parser, self.options)

    def test_resolve_model_no_hosts_empty_environment(self):
        """
        Cannot resolve with no hosts defined in the environment.
        """
        self.options.environment = 'test3'
        self.options.hosts = ''
        self.options.roles = ''
        with self.assertRaises(AssertionError):
            resolve_model(self.parser, self.options)

    def test_resolve_model_no_hosts_unknown_environment(self):
        """
        Cannot resolve with an unknown environment.
        """
        self.options.environment = 'test4'
        self.options.hosts = 'host1'
        self.options.roles = 'role1'
        with self.assertRaises(AssertionError):
            resolve_model(self.parser, self.options)

    def test_resolve_model_no_hosts_different_roles(self):
        """
        Cann resolve with environment hosts that do not have
        the same roles if there's at least one role in common.
        """
        self.options.environment = 'test1'
        self.options.hosts = ''
        self.options.roles = ''
        resolve_model(self.parser, self.options)
        eq_(['role1'], self.options.roles)
        eq_(['host1', 'host2', 'host3'], self.options.hosts)

    def test_resolve_model_no_hosts_no_roles_same_roles(self):
        """
        Can resolve with environment hosts that have the same role.
        """
        self.options.environment = 'test2'
        self.options.hosts = ''
        self.options.roles = ''
        resolve_model(self.parser, self.options)
        eq_(['role1', 'role2'], self.options.roles)
        eq_(['host2', 'host3'], self.options.hosts)

    def test_resolve_model_no_hosts_with_multiple_roles(self):
        """
        Can resolve with enviroment hosts that have the same role
        and multiple explicit roles are defined.
        """
        self.options.environment = 'test2'
        self.options.hosts = ''
        self.options.roles = 'role1,role2'
        resolve_model(self.parser, self.options)
        eq_(['role1', 'role2'], self.options.roles)
        eq_(['host2', 'host3'], self.options.hosts)

    def test_resolve_model_no_hosts_with_role(self):
        """
        Can resolve with enviroment hosts that have the same role
        and a single explicit role is defined.
        """
        self.options.environment = 'test2'
        self.options.hosts = ''
        self.options.roles = 'role1'
        resolve_model(self.parser, self.options)
        eq_(['role1'], self.options.roles)
        eq_(['host2', 'host3'], self.options.hosts)

    def test_resolve_model_no_hosts_with_different_roles(self):
        """
        Can resolve with environment hosts that have different roles
        to the subset that matches the explicitly defined roles.
        """
        self.options.environment = 'test1'
        self.options.hosts = ''
        self.options.roles = 'role1,role2'
        resolve_model(self.parser, self.options)
        eq_(['role1', 'role2'], self.options.roles)
        eq_(['host2', 'host3'], self.options.hosts)

    def test_resolve_model_no_hosts_with_single_invalid_role(self):
        """
        Can resolve with enviroment hosts that have different roles
        and a single, compatible role is defined.
        """
        self.options.environment = 'test1'
        self.options.hosts = ''
        self.options.roles = 'role2'
        resolve_model(self.parser, self.options)
        eq_(['role2'], self.options.roles)
        eq_(['host2', 'host3'], self.options.hosts)

    def test_resolve_model_no_hosts_with_single_valid_role(self):
        """
        Can resolve with enviroment hosts that have different roles
        and a single, compatible role is defined.
        """
        self.options.environment = 'test1'
        self.options.hosts = ''
        self.options.roles = 'role1'
        resolve_model(self.parser, self.options)
        eq_(['role1'], self.options.roles)
        eq_(['host1', 'host2', 'host3'], self.options.hosts)

    def test_resolve_model_no_role_same_roles(self):
        """
        Can resolve explicit hosts if they have the same roles.
        """
        self.options.environment = 'test1'
        self.options.hosts = 'host2,host3'
        self.options.roles = ''
        resolve_model(self.parser, self.options)
        eq_(['role1', 'role2'], self.options.roles)
        eq_(['host2', 'host3'], self.options.hosts)

    def test_resolve_model_no_role_different_roles(self):
        """
        Cannot resolve explicit hosts if they have different roles
        and no role is specified.
        """
        self.options.environment = 'test1'
        self.options.hosts = 'host1,host2'
        self.options.roles = ''
        resolve_model(self.parser, self.options)
        eq_(['role1'], self.options.roles)
        eq_(['host1', 'host2'], self.options.hosts)

    def test_resolve_model_same_roles(self):
        """
        Can resolve explicit hosts if they have the same roles
        and role is specified.
        """
        self.options.environment = 'test1'
        self.options.hosts = 'host1,host2'
        self.options.roles = 'role1'
        resolve_model(self.parser, self.options)
        eq_(['role1'], self.options.roles)
        eq_(['host1', 'host2'], self.options.hosts)

    def test_resolve_model_mismatched_roles_multiple_roles(self):
        """
        Cannot resolve explicit hosts if they have different roles
        and not all roles specified are shared.
        """
        self.options.environment = 'test1'
        self.options.hosts = 'host1,host2'
        self.options.roles = 'role1,role2'
        with self.assertRaises(AssertionError):
            resolve_model(self.parser, self.options)

    def test_resolve_model_mismatched_roles_shared_role(self):
        """
        Can resolve explicit hosts if they have different roles
        and the role specified is shared.
        """
        self.options.environment = 'test1'
        self.options.hosts = 'host1,host2'
        self.options.roles = 'role1'
        resolve_model(self.parser, self.options)
        eq_(['role1'], self.options.roles)
        eq_(['host1', 'host2'], self.options.hosts)

    def test_resolve_multiple_roles(self):
        """
        Can resolve explicit hosts and roles if they are all shared.
        """
        self.options.environment = 'test2'
        self.options.hosts = 'host2,host3'
        self.options.roles = 'role1,role2'
        resolve_model(self.parser, self.options)
        eq_(['role1', 'role2'], self.options.roles)
        eq_(['host2', 'host3'], self.options.hosts)
