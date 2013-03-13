"""
Functions for interacting with the defined hosts, environments, and roles.
"""
from confab.files import _import

from fabric.api import env


def load_model_from_dir(dir_name):
    """
    Load model data (environments, roles, hosts) from settings.py.
    """

    settings = _import('settings', dir_name)
    try:
        env['environmentdefs'] = getattr(settings, 'environmentdefs')
    except AttributeError:
        env['environmentdefs'] = {}

    try:
        env['roledefs'] = getattr(settings, 'roledefs')
    except AttributeError:
        env['roledefs'] = {}


def _matching_keys(dct, value):
    """
    Return all keys in 'dct' whose value list contains 'value'.
    """
    return map(lambda (k, v): k, filter(lambda (k, v): value in v, dct.iteritems()))


def get_roles_for_host(host):
    """
    Get all roles that a host belongs to.

    Delegates to Fabric's env roledefs.
    """
    return _matching_keys(env.roledefs, host)


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
