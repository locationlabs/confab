"""
Test helpers.
"""
import codecs
import os
import shutil
import tempfile


class TempDir(object):
    """
    With statement compatible temporary directory structure.

    Based on a similar construct from the skeleton project.
    """

    def __init__(self):
        self.path = None

    def read(self, file_name):
        return codecs.open(os.sep.join((self.path, file_name)), encoding='utf-8').read().strip()

    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self

    def __exit__(self, exc_type, value, traceback):
        shutil.rmtree(self.path)
