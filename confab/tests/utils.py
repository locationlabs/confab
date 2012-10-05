"""
Test helpers.
"""

from confab.options import options

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
        return open(os.sep.join((self.path,file_name))).read().strip()

    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self

    def __exit__(self, exc_type, value, traceback):
        shutil.rmtree(self.path)

class Options(object):
    """
    With statement to temporarily set options.
    
    """

    def __init__(self,**kwargs):
        self.kwargs = kwargs
        self.previous = {}

    def __enter__(self):
        for (k,v) in self.kwargs.iteritems():
            self.previous[k] = options.get(k)
            options[k] = v
        return self

    def __exit__(self, exc_type, value, traceback):
        for k in self.kwargs.keys():
            options[k] = self.previous[k]


