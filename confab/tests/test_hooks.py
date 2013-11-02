"""
Tests for Hooks
"""

from unittest import TestCase
from os.path import join, dirname

from nose.tools import eq_, ok_

from confab.definitions import Settings
from confab.data import DataLoader
from confab.hooks import Hook, ScopeAndHooks, HookRegistry


class TestHooks(TestCase):
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

    def test_add_remove_hook(self):
        """
        Load additional configuration data via hook.

        * Test adding new hook
        * Test removing hook
        """
        def test_hook(host):
            return {'data': {'num_cores': 4}}

        testhook = Hook(test_hook)
        local_hooks = HookRegistry()

        local_hooks.add_hook('host', testhook)
        ok_(testhook in local_hooks._hooks['host'])

        local_hooks.remove_hook('host', testhook)
        ok_(testhook not in local_hooks._hooks['host'])

    def test_hook_override_data(self):
        """
        Test that data loaded via hook overwrites data loaded via config.
        """
        def test_hook(role):
            return {'data': {'role': 'role2'}}

        with ScopeAndHooks(('host', Hook(test_hook))):
            loader = DataLoader(join(dirname(__file__), 'data/order'))
            eq_(loader(self.component)['data'],
                {'default': 'default',
                 'component': 'component',
                 'role': 'role2',
                 'environment': 'environment',
                 'host': 'host'})

    def test_data_override_hook(self):
        """
        Test that data loaded via hook will be overwritten by data loaded later via config.
        """
        def test_hook(role):
            return {'data': {'environment': 'environment2'}}

        with ScopeAndHooks(('role', Hook(test_hook))):
            loader = DataLoader(join(dirname(__file__), 'data/order'))
            eq_(loader(self.component)['data'],
                {'default': 'default',
                 'component': 'component',
                 'role': 'role',
                 'environment': 'environment',
                 'host': 'host'})

    def test_hook_load_order(self):
        """
        Test that hooks overwrite each other based on order they are defined.
        """
        def test_hook1(host):
            return {'data': {'host': 'host1'}}

        def test_hook2(host):
            return {'data': {'host': 'host2'}}

        with ScopeAndHooks(('host', Hook(test_hook1)), ('host', Hook(test_hook2))):
            loader = DataLoader(join(dirname(__file__), 'data/order'))
            eq_(loader(self.component)['data'],
                {'default': 'default',
                 'component': 'component',
                 'role': 'role',
                 'environment': 'environment',
                 'host': 'host2'})

    def test_filter_func(self):
        """
        Test that hooks only run if the filter_func returns true
        """
        def test_hook1(host):
            return {'data': {'host': 'host1'}}

        def test_hook2(host):
            return {'data': {'host': 'host2'}}

        with ScopeAndHooks(('host', Hook(test_hook1)),
                           ('host', Hook(test_hook2, lambda componentdef: False))):
            loader = DataLoader(join(dirname(__file__), 'data/order'))
            eq_(loader(self.component)['data'],
                {'default': 'default',
                 'component': 'component',
                 'role': 'role',
                 'environment': 'environment',
                 'host': 'host1'})
