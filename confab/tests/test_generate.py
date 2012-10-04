from confab.generate import generate
from unittest import TestCase
from jinja2 import Environment, PackageLoader, StrictUndefined, UndefinedError

import os
import shutil
import tempfile

class TempDir(object):

    def __init__(self):
        self.path = None

    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, exc_type, value, traceback):
        shutil.rmtree(self.path)

def _make_env():
    return Environment(loader=PackageLoader('confab.tests'),
                       undefined=StrictUndefined)

class TestGenerate(TestCase):
    
    def _read_value(self, tmp_dir, file_name):
        return open(os.sep.join((tmp_dir,file_name))).read().strip()

    def test_undefined(self):
        """
        An exception is raised if a template value is undefined.
        """
        env = _make_env()
        data = {}

        with self.assertRaises(UndefinedError):
            with TempDir() as tmp_dir:
                generate(env, data, tmp_dir)

    def test_generate(self):
        """
        Generated templates have the correct values.
        """
        env = _make_env()
        data = {'foo':'foo', 'bar':'bar'}

        with TempDir() as tmp_dir:
            generate(env, data, tmp_dir)

            # foo.txt is populated with 'foo'
            self.assertEquals('foo', self._read_value(tmp_dir,'foo.txt'))

            # bar.txt is populated with 'bar' and path is substituted
            self.assertEquals('bar', self._read_value(tmp_dir,'bar/bar.txt'))
                    
    def test_filter_func(self):
        """
        Passing a filter_func limits which templates are generated.
        """
        env = _make_env()
        data = {'foo':'foo', 'bar':'bar'}

        def filter_func(file_name):
            return file_name != 'foo.txt'

        with TempDir() as tmp_dir:
            generate(env, data, tmp_dir, filter_func=filter_func)
                    
            # not generated
            with self.assertRaises(IOError):
                self._read_value(tmp_dir,'foo.txt')

    def test_mime_type_func(self):
        """
        Passing a mime_type_func controls whether templates are rendered.
        """
        env = _make_env()
        data = {'foo':'foo', 'bar':'bar'}

        def mime_type_func(file_name):
            return False

        with TempDir() as tmp_dir:
            generate(env, data, tmp_dir, mime_type_func=mime_type_func)

            # templates not rendered (though paths are)
            self.assertEquals('{{foo}}', self._read_value(tmp_dir,'foo.txt'))
            self.assertEquals('{{bar}}', self._read_value(tmp_dir,'bar/bar.txt'))
