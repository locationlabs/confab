"""
Functions for interacting with the defined hosts, environments, and roles.
"""
from fabric.api import env

from confab.files import _import


def _keys():
    """
    Get the model's environment keys.
    """
    return ["environmentdefs", "roledefs"]


def load_model_from_dir(dir_name, module_name='settings'):
    """
    Load model data (environments, roles, hosts) from settings module.
    """

    settings = _import(module_name, dir_name)
    for key in _keys():
        env[key] = getattr(settings, key, {})


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
        env.environmentdefs
    except AttributeError:
        raise Exception("No environments are defined")

    try:
        return env.environmentdefs[environment]
    except KeyError:
        raise Exception("Environment '{}' is not defined".format(environment))
