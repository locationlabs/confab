"""
Tests for file operations.
"""
from os.path import dirname, join
from unittest import TestCase
from nose.tools import eq_, ok_

from confab.files import _import


class TestImport(TestCase):

    def setUp(self):
        self.dir_name = join(dirname(__file__), 'data/default')

    def test_import_empty(self):
        module = _import("empty", self.dir_name)
        ok_(module)

    def test_import_simple(self):
        module = _import("simple", self.dir_name)
        ok_(module)
        eq_("bar", module.foo)

    def test_import_not_found(self):
        with self.assertRaises(ImportError) as e:
            _import("missing", self.dir_name)
        # module_path not set: the module itself could not be found
        eq_(None, getattr(e.exception, 'module_path', None))

    def test_import_broken(self):
        with self.assertRaises(ImportError) as e:
            _import("broken", self.dir_name)
        # module_path was set: the module was found but had an import error
        eq_(join(self.dir_name, 'broken.py'), e.exception.module_path)
