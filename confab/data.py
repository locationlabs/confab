"""
Functions for loading configuration data.
"""

from confab.files import _import_string
from confab.merge import merge
from confab.options import options
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from fabric.api import env as fabric_env


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

    Returns publicly names values in module's __dict__.
    """

    def as_dict(module):
        try:
            return {k: v for k, v in module.__dict__.iteritems() if not k[0:1] == '_'}
        except AttributeError:
            return None

    try:
        env = Environment(loader=FileSystemLoader(data_dir))
        rendered_module = env.get_template(module_name + '.py').render({})

        module = _import_string(module_name, rendered_module)
        return as_dict(module)
    except (ImportError, TemplateNotFound):
        return None


def load_data_from_dir(data_dir):
    """
    Load and merge configuration data.

    Configuration data is loaded from python files by type,
    where type is defined to include defaults, per-role values,
    per-environment values and per-host values.

    Configuration data also includes the current environment
    and host string values under a 'confab' key.
    """

    is_not_none = lambda x: x is not None

    module_names = filter(is_not_none,
                          ['default',
                           _get_role_module(),
                           _get_environment_module(),
                           _get_host_module()])

    load_module = lambda module_name: import_configuration(module_name, data_dir)

    module_dicts = filter(is_not_none, map(load_module, module_names))

    confab_data = dict(confab=dict(environment=fabric_env.environment, host=fabric_env.host_string))

    return merge(confab_data, *module_dicts)
