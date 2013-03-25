"""
Functions for interacting with the defined hosts, environments, and roles.
"""
from fabric.api import env
from confab.files import _import
from os.path import join


def _keys():
    """
    Get the model's environment keys.
    """
    return ["environmentdefs", "roledefs", "componentdefs"]


def load_model_from_dir(dir_name, module_name='settings'):
    """
    Load model data (environments, roles, hosts) from settings module.
    """

    settings = _import(module_name, dir_name)
    for key in _keys():
        env[key] = getattr(settings, key, {})


def load_model_from_dict(settings):
    """
    Load model data (environments, roles, hosts) from settings dictionary.
    """

    for key in _keys():
        env[key] = settings.get(key, {})


def get_roles_for_host(host):
    """
    Get all roles that a host belongs to.

    Delegates to Fabric's env roledefs.
    """
    return [role for (role, hosts) in env.roledefs.iteritems() if host in hosts]


def get_hosts_for_environment(environment):
    """
    Get all hosts for an environment.

    Assumes an environmentsdef structure in Fabric's env.
    """
    try:
        return env.environmentdefs[environment]
    except AttributeError:
        raise Exception("No environments are defined")
    except KeyError:
        raise Exception("Environment '{}' is not defined".format(environment))


def get_components_for_role(role):
    """
    Get all component paths for the given role.
    """
    if role not in env.roledefs:
        raise Exception("Role '{}' is not defined".format(role))

    if role not in env.componentdefs:
        return []

    return _expand_components(role, '', {})


def _expand_components(component, path, seen):
    """
    Recursively expand component paths rooted at the given component
    based on componentdefs.

    Raises an exception if a cycle is discovered in component definitions
    or if a component leaf exists in multiple paths.

    :param component: A component name.
    :param path: The component path being built.
    :param seen: Dictionary of visited components and their paths.
    """
    component_path = join(path, component)

    if component in seen:
        raise Exception("Detected cycle or multiple paths with role/component '{}'"
                        " ('{}' and '{}')".format(component,
                                                  seen[component],
                                                  component_path))
    seen[component] = component_path

    if component not in env.componentdefs:
        return [component_path]

    components = []
    for c in env.componentdefs.get(component):
        components += _expand_components(c, component_path, seen)

    return components
