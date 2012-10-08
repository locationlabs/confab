"""
Functions for interacting with the defined hosts, environments, and roles.
"""

from fabric.api import env
from confab.files import _import

import imp
import sys

def load_model_from_dir(dir_name):
    """
    Load model data (environments, roles, hosts) from settings.py.
    """

    settings = _import('settings', dir_name)
    try:
        env['environmentdefs'] = getattr(settings,'environmentdefs')
    except AttributeError:
        env['environmentdefs'] = {}

    try:
        env['roledefs'] = getattr(settings,'roledefs')
    except AttributeError:
        env['roledefs'] = {}

def _matching_keys(dct, value):
    """
    Return all keys in 'dct' whose value list contains 'value'.
    """
    return map(lambda (k,v): k, filter(lambda (k,v): value in v, dct.iteritems()))

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
        return []

    return env.environmentdefs.get(environment,[])

def has_same_roles(hosts):
    """
    Determine whether all provided hosts have the same roles.

    Returns the intersection of roles for all provided hosts.
    """
    if not hosts:
        return set()

    def to_role_set(host):
        return set(get_roles_for_host(host))

    return reduce(lambda a, b: a if a == b else set(), map(to_role_set, hosts))

def has_roles(hosts, roles):
    """
    Determine whether all provided hosts have the provided roles.
    """
    if not hosts:
        return False

    for host in hosts:
        roles_for_host = get_roles_for_host(host)
        if not set(roles_for_host).issuperset(roles):
            return False

    return True
