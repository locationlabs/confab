"""
Functions for loading configuration data.
"""

from confab.merge import merge
from confab.options import options
import imp
import os
import sys

def _get_environment_module():
    """
    Return the current configuration environment.

    Placeholder.
    """
    return None

def _get_role_module():
    """
    Return the current configuration role.

    Placeholder.
    """
    return None

def _get_host_module():
    """
    Return the current configuration hostname.
    """
    return options.get_hostname()

def import_configuration(module_name, data_dir):
    """
    Load configuration from file as python module.
    
    Treats module's __all__ value as the configuration dictionary.
    """

    # assign module a name that's not likely to conflict
    safe_name = 'confab.data.' + module_name

    # use __all__ as the module's dictionary
    def as_dict(module):
        try:
            return module.__all__
        except AttributeError:
            return None


    # check if module is already loaded
    existing = sys.modules.get(safe_name)
    if existing:
        return as_dict(existing)

    # try to load module
    try:
        module_info = imp.find_module(module_name, [data_dir])
        module = imp.load_module(safe_name, *module_info)
        return as_dict(module)
    except ImportError:
        return None

def load_data_from_dir(data_dir):
    """
    Load and merge configuration data.
    
    Configuration data is loaded from python files by type,
    where type is defined to include defaults, per-environment values,
    per-role values and per-host values.
    """

    is_not_none = lambda x: x is not None

    module_names = filter(is_not_none,
                          [ 'default',
                            _get_environment_module(),
                            _get_role_module(),
                            _get_host_module() ])

    load_module = lambda module_name: import_configuration(module_name, data_dir)

    module_dicts = filter(is_not_none, map(load_module, module_names))

    return merge(*module_dicts)
