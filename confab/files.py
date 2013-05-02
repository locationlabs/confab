"""
File options.
"""

import imp
import os
import shutil
import sys
from hashlib import md5
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
    safe_name = 'confab.data.' + _hash(module_name, dir_name)

    # check if module is already loaded
    existing = sys.modules.get(safe_name)
    if existing:
        return existing

    # try to load module
    module_info = imp.find_module(module_name, [dir_name])
    try:
        module = imp.load_module(safe_name, *module_info)
    except ImportError as e:
        # In the normal case, an import error is raised during imp.find_module()
        # because the module is not found. However, ImportError can also be raised
        # if the module itself contains other ImportErrors. Rather than depend on the
        # error message or invent a non-standard exception type, decorate the error
        # with the path to the module that was found.
        e.module_path = module_info[1]
        raise e
    return module


def _import_string(module_name, content):
    """
    Load python module from an in-memory string without reloading.
    """

    # assign module a name that's not likely to conflict
    safe_name = 'confab.data.' + _hash(module_name, content)

    # check if module is already loaded
    existing = sys.modules.get(safe_name)
    if existing:
        return existing

    # try to load module
    module = imp.new_module(safe_name)
    exec content in module.__dict__
    return module


def _hash(*args):
    """
    Create a hash out of a list of strings.
    """
    return md5(''.join(args)).digest().encode("base64")
