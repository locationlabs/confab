"""
Functions for loading configuration data.
"""

from confab.files import _import
from confab.merge import merge
from confab.options import options
from itertools import chain


def _get_environment_module():
    """
    Return the current configuration environment.

    Placeholder.
    """
    return options.get_environmentname()


def _get_component_modules(component):
    """
    Return the different modules in the component path.
    """
    return component.split('/')


def _get_host_module():
    """
    Return the current configuration hostname.
    """
    return options.get_hostname()


def import_configuration(module_name, data_dir):
    """
    Load configuration from file as python module.

    Returns publicly names values in module's __dict__.
    """

    def as_dict(module):
        try:
            return {k: v for k, v in module.__dict__.iteritems() if not k[0:1] == '_'}
        except AttributeError:
            return None

    try:
        module = _import(module_name, data_dir)
        return as_dict(module)
    except ImportError:
        return None


class DataLoader(object):
    """
    Load and merge configuration data.

    Configuration data is loaded from python files by type,
    where type is defined to include defaults, per-environment values,
    per-role values, per-component values and per-host values.
    """

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def __call__(self, component):
        """
        Load the data for the given component.

        :param component: a component path, i.e. `{role}/{sub-component}/{component}`.
        """
        is_not_none = lambda x: x is not None

        module_names = filter(is_not_none,
                              chain(['default',
                                     _get_environment_module()],
                                    _get_component_modules(component),
                                    [_get_host_module()]))

        load_module = lambda module_name: import_configuration(module_name, self.data_dir)

        module_dicts = filter(is_not_none, map(load_module, module_names))

        return merge(*module_dicts)
