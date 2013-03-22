"""
Resolve environment, role, and host choices into actions.

If a user specifies only an environment, confab should target all hosts
and roles in that environment. If one or more roles -- or one or more hosts --
are specified explicilty, confab should target a subset.
"""
from warnings import warn
from confab.model import get_roles_for_host, get_hosts_for_environment


def resolve_hosts_and_roles(environment, hosts=None, roles=None):
    """
    Given an environment, (possibly empty) list of hosts, and a (possibly empty)
    list of roles, return a mapping from host to roles to target.

    Raises an exception if any targeted host would have no roles after resolution.
    """
    # Validate environment
    if not environment:
        raise Exception("Environment was not specified")

    # Determine hosts for the environment
    environment_hosts = get_hosts_for_environment(environment)
    if environment_hosts is None:
        raise Exception("Environment '{}' is not recognized.".format(environment))
    elif not environment_hosts:
        warn("Environment '{}' does not have any hosts configured.".format(environment))

    # Use all environment hosts if none are specified
    hosts = hosts or environment_hosts

    # Forbid any hosts not in environment
    for host in hosts:
        if host not in environment_hosts:
            raise Exception("Host '{host}' is not a member of the environment '{env}'"
                            .format(host=host, env=environment))

    # Determine roles for hosts
    if roles:
        # If roles were specified, restrict mapping to those roles
        valid_roles = lambda role: role in roles
        hosts_to_roles = {}
        for host in hosts:
            host_roles = filter(valid_roles, get_roles_for_host(host))
            if host_roles:
                hosts_to_roles[host] = host_roles
    else:
        # Otherwise, use all roles
        hosts_to_roles = dict([(host, get_roles_for_host(host)) for host in hosts])

    # Validate that all hosts have at least one role
    for host, host_roles in hosts_to_roles.iteritems():
        if not host_roles:
            if roles:
                raise Exception("Host '{}' does not have any of the specified roles".format(host))
            else:
                raise Exception("Host '{}' does not have any configured roles".format(host))

    return hosts_to_roles
