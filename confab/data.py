"""
Functions for loading configuration data.
"""
from itertools import chain
from fabric.api import puts
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from confab.files import _import, _import_string
from confab.merge import merge
from confab.options import options
from confab.output import debug


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
        debug("Attempting to load {module_name}.py from {data_dir}",
              module_name=module_name,
              data_dir=data_dir)

        module = _import(module_name, data_dir)
        puts("Loaded {module_name}.py from {data_dir}".format(module_name=module_name,
                                                              data_dir=data_dir))
    except ImportError:
        debug("Attempting to load {module_name}.py_tmpl from {data_dir}",
              module_name=module_name,
              data_dir=data_dir)
        # try to load as a template
        try:
            env = Environment(loader=FileSystemLoader(data_dir))
            rendered_module = env.get_template(module_name + '.py_tmpl').render({})
        except TemplateNotFound:
            debug("Could not load {module_name} from {data_dir}",
                  module_name=module_name,
                  data_dir=data_dir)
            return None

        module = _import_string(module_name, rendered_module)
        puts("Loaded {module_name}.py_tmpl from {data_dir}".format(module_name=module_name,
                                                                   data_dir=data_dir))

    return as_dict(module)


class DataLoader(object):
    """
    Load and merge configuration data.

    Configuration data is loaded from python files by type,
    where type is defined to include defaults, per-role values,
    per-component values, per-environment values and per-host values.

    Configuration data also includes the current environment
    and host string values under a 'confab' key.
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
                              chain(['default'],
                                    _get_component_modules(component),
                                    [_get_environment_module(),
                                     _get_host_module()]))

        load_module = lambda module_name: import_configuration(module_name, self.data_dir)

        module_dicts = filter(is_not_none, map(load_module, module_names))

        confab_data = dict(confab=dict(environment=options.get_environmentname(),
                                       host=options.get_hostname(),
                                       component=component))

        return merge(confab_data, *module_dicts)
