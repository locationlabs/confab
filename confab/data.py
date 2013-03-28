"""
Functions for loading configuration data.
"""
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


def _get_role_module():
    """
    Return the current configuration role.
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

    options.module_preprocess(module)
    return as_dict(module)


class DataLoader(object):
    """
    Load and merge configuration data.

    Configuration data is loaded from python files by type,
    where type is defined to include defaults, per-role values,
    per-component values, per-environment values and per-host values.

    Configuration data also includes the current environment, component
    and host string values under a 'confab' key.
    """

    ALL = ['default', 'role', 'component', 'environment', 'host']

    def __init__(self, data_dir, data_modules=ALL):
        """
        Create a data loader for the given data directory.

        :param data_modules: list of modules to load in the order to load them.
        """
        self.data_dir = data_dir
        self.data_modules = data_modules

    def __call__(self, component):
        """
        Load the data for the current configuration.

        :param component: a component name. can be None to load role data.
        """
        is_not_none = lambda x: x is not None

        module_names = filter(is_not_none, self._list_modules(component))

        load_module = lambda module_name: import_configuration(module_name, self.data_dir)

        module_dicts = filter(is_not_none, map(load_module, module_names))

        confab_data = dict(confab=dict(environment=options.get_environmentname(),
                                       host=options.get_hostname(),
                                       component=component))

        return merge(confab_data, *module_dicts)

    def _list_modules(self, component):
        """
        Get the list of modules to load.
        """
        module_names = {
            'default': 'default',
            'role': _get_role_module(),
            'component': component,
            'environment': _get_environment_module(),
            'host': _get_host_module()
        }

        return map(lambda module: module_names[module], self.data_modules)
