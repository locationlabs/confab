"""
Test helpers.
"""
from jinja2 import Environment, PackageLoader, StrictUndefined
import os
import shutil
import tempfile

class TempDir(object):

    def __init__(self):
        self.path = None

    def read(self, file_name):
        return open(os.sep.join((self.path,file_name))).read().strip()

    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self

    def __exit__(self, exc_type, value, traceback):
        shutil.rmtree(self.path)

def make_env():
    return Environment(loader=PackageLoader('confab.tests'),
                       undefined=StrictUndefined)
