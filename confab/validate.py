"""
Functions for validating user input to tasks.
"""
import os
from fabric.api import abort, env


def assert_exists(*directories):
    """
    Directories must be defined and exist.
    """
    for directory in directories:
        if not os.path.isdir(directory):
            abort('{} is not a valid directory'.format(directory))


def assert_may_be_created(*directories):
    """
    Directories must either be defined or must not exist.
    """
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                abort(e)
        elif not os.path.isdir(directory):
            abort('{} is not a valid directory'.format(directory))


def validate_host():
    """
    Fabric host_string must be defined.
    """
    # XXX unclear if we still want this check
    if not env.host_string:
        abort('Please specify a host or a role')
