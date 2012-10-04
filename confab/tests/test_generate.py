from confab.generate import generate
from unittest import TestCase
from jinja2 import Environment, PackageLoader

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

class TestGenerate(TestCase):

    def test_environment(self):

        env = Environment(loader=PackageLoader('confab.tests'))
        data = {'foo':'foo', 'bar':'bar'}

        with TempDir() as tmp_dir:
            generate(env, data, tmp_dir)

            # foo.txt is populated with 'foo'
            self.assertEqual(
                open(os.sep.join((tmp_dir,'foo.txt'))).read().strip(),
                'foo'
                )

            # bar.txt is populated with 'bar' and path is substituted
            self.assertEqual(
                open(os.sep.join((tmp_dir,'bar/bar.txt'))).read().strip(),
                'bar'
                )
            
