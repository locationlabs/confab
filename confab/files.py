"""
File options.
"""

import imp
import os
import shutil
import sys
from fabric.api import runs_once


@runs_once
def _clear_dir(dir_name):
    """
    Remove an entire directory tree.
    """
    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)


def _clear_file(file_name):
    """
    Remove an entire directory tree.
    """
    if os.path.exists(file_name):
        os.remove(file_name)


def _ensure_dir(dir_name):
    """
    Ensure that a directory exists.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def _import(module_name, dir_name):
    """
    Load python module from file system without reloading.

    Raises ImportError if not found.
    """

    # assign module a name that's not likely to conflict
    safe_name = 'confab.data.' + module_name

    # check if module is already loaded
    existing = sys.modules.get(safe_name)
    if existing:
        return existing

    # try to load module
    module_info = imp.find_module(module_name, [dir_name])
    module = imp.load_module(safe_name, *module_info)
    return module


def _import_string(module_name, content):
    """
    Load python module from an in-memory string without reloading.
    """

    # assign module a name that's not likely to conflict
    safe_name = 'confab.data.' + module_name

    # check if module is already loaded
    existing = sys.modules.get(safe_name)
    if existing:
        return existing

    # try to load module
    module = imp.new_module(safe_name)
    exec content in module.__dict__
    return module
