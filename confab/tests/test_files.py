"""
Tests for file operations.
"""
from os.path import dirname, join
from unittest import TestCase
from nose.tools import eq_, ok_

from confab.files import _import


class TestImport(TestCase):

    def setUp(self):
        self.dir_name = join(dirname(__file__), 'data')

    def test_import_empty(self):
        module = _import("empty", self.dir_name)
        ok_(module)

    def test_import_simple(self):
        module = _import("simple", self.dir_name)
        ok_(module)
        eq_("bar", module.foo)

    def test_import_not_found(self):
        with self.assertRaises(ImportError):
            _import("missing", self.dir_name)

    def test_import_broken(self):
        with self.assertRaises(ImportError):
            _import("broken", self.dir_name)
