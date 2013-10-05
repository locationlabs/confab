"""
Functions for loading configuration data.
"""
from os.path import join
from itertools import chain

from fabric.api import puts
from gusset.output import debug
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from confab.files import _import, _import_string
from confab.merge import merge
from confab.options import options
from confab.hooks import hooks


class ModuleNotFound(Exception):
    """
    Raised when a python module cannot be found.
    """
    pass


def _import_configuration(module_name, data_dir):
    """
    Load configuration from file as python module.

    :param data_dir: directory to load from.
    """
    try:
        debug("Attempting to load {module_name}.py from {data_dir}",
              module_name=module_name,
              data_dir=data_dir)

        module = _import(module_name, data_dir)
        puts("Loaded {module_name}.py from {data_dir}".format(module_name=module_name,
                                                              data_dir=data_dir))
    except ImportError as e:
        # if the module was found but could not be loaded, re-raise the error
        if getattr(e, 'module_path', None):
            raise e
        debug("Attempting to load {module_name}.py_tmpl from {data_dir}",
              module_name=module_name,
              data_dir=data_dir)
        # try to load as a template
        try:
            env = Environment(loader=FileSystemLoader(data_dir))
            rendered_module = env.get_template(module_name + '.py_tmpl').render({})
            module = _import_string(module_name, rendered_module)
            puts("Loaded {module_name}.py_tmpl from {data_dir}".format(module_name=module_name,
                                                                       data_dir=data_dir))
        except TemplateNotFound:
            debug("Could not load {module_name} from {data_dir}",
                  module_name=module_name,
                  data_dir=data_dir)
            raise ModuleNotFound("No module named {}".format(module_name))

    return module


def import_configuration(module_name, *data_dirs, **kwargs):
    """
    Load configuration from a python module as a dictionary.

    :param data_dirs: List of directories to load from.
    :param scope: (kwargs) Containing folder name for module.
    """
    def add_scope(data_dirs, scope):
        if scope is None:
            return data_dirs
        return list(chain(*zip(data_dirs, map(lambda data_dir: join(data_dir, scope), data_dirs))))

    for data_dir in add_scope(data_dirs, kwargs.get('scope')):
        try:
            module = _import_configuration(module_name, data_dir)
            return options.module_as_dict(module)
        except ModuleNotFound:
            pass  # try the next directory

    # module not found in any directory
    return options.module_as_dict({})


class DataLoader(object):
    """
    Load and merge configuration data.

    Configuration data is loaded from python files by type,
    where type is defined to include defaults, per-role values,
    per-component values, per-environment values and per-host values.

    Configuration data also includes the current environment
    and host string values under a ``confab`` key.
    """

    ALL = ['default', 'component', 'role', 'environment', 'host']

    def __init__(self, data_dirs, data_modules=ALL, ignore_hooks=False):
        """
        Create a data loader for the given data directories.

        :param data_dirs: list of data directories or a single data directory path.
        :param data_modules: list of modules to load in the order to load them.
        """
        self.data_dirs = data_dirs if isinstance(data_dirs, list) else [data_dirs]
        self.data_modules = set(data_modules)
        self._ignore_hooks = ignore_hooks

    def __call__(self, componentdef):
        """
        Load the data for the current configuration.

        :param component: a component definition.
        """
        def load_module(scope_and_module):
            scope, module_name = scope_and_module
            hook_dicts = [hook(module_name) for hook in hooks.for_scope(scope)
                          if hook.filter(componentdef)] if not self._ignore_hooks else {}
            return merge(import_configuration(module_name, *self.data_dirs, scope=scope),
                         *hook_dicts)

        module_dicts = map(load_module, self._list_modules(componentdef))

        confab_data = dict(confab=dict(environment=componentdef.environment,
                                       host=componentdef.host,
                                       role=componentdef.role,
                                       component=componentdef.name))

        return merge(confab_data, *module_dicts)

    def _list_modules(self, componentdef):
        """
        Get the list of modules to load.
        """
        module_names = [
            ('default', 'default'),
            ('component', componentdef.name),
            ('role', componentdef.role if componentdef.role != componentdef.name else None),
            ('environment', componentdef.environment),
            ('host', componentdef.host)
        ]

        return [(key, name) for key, name in module_names
                if key in self.data_modules and name is not None]
