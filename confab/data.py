"""
Functions for loading configuration data.
"""

from confab.files import _import
from confab.merge import merge
from confab.options import options


def _get_environment_module():
    """
    Return the current configuration environment.

    Placeholder.
    """
    return options.get_environmentname()


def _get_role_module():
    """
    Return the current configuration role.

    Placeholder.
    """
    return options.get_rolename()


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

    # use __all__ as the module's dictionary
    def as_dict(module):
        try:
            return module.__all__
        except AttributeError:
            return None

    try:
        module = _import(module_name, data_dir)
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
                          ['default',
                           _get_environment_module(),
                           _get_role_module(),
                           _get_host_module()])

    load_module = lambda module_name: import_configuration(module_name, data_dir)

    module_dicts = filter(is_not_none, map(load_module, module_names))

    return merge(*module_dicts)
