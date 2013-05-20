"""
Functions for validating user input to tasks.
"""
from os import makedirs
from os.path import dirname, exists, isdir
from fabric.api import abort


def assert_exists(*directories):
    """
    Assert that directories exist.
    """
    for directory in directories:
        if not isdir(directory):
            abort('{} is not a valid directory'.format(directory))


def assert_may_be_created(path):
    """
    Assert that path's directory either exists or can be created.
    """
    directory = dirname(path)
    if not exists(directory):
        try:
            makedirs(directory)
        except OSError as e:
            abort(e)
    elif not isdir(directory):
        abort('{} is not a valid directory'.format(directory))
