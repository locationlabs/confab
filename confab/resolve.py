"""
Resolve environment, role, and host choices into actions.

If a user specifies only an environment, confab should target all hosts
and roles in that environment. If one or more roles -- or one or more hosts --
are specified explicilty, confab should target a subset.
"""
from confab.model import get_roles_for_host, get_hosts_for_environment


def resolve_hosts_and_roles(environment, hosts=None, roles=None):
    """
    Given an environment, (possibly empty) list of hosts, and a (possibly empty)
    list of hosts, return a mapping from host to roles to target.

    Raises an exception if any targeted host would have no roles after resolution.
    """
    # Either use configured hosts or all hosts in environment
    if not hosts:
        if not environment:
            raise Exception("Environment was not specified")
        hosts = get_hosts_for_environment(environment)
        if hosts is None:
            raise Exception("Environment '{}' is not recognized.".format(environment))
        elif not hosts:
            raise Exception("Environment '{}' does not have any hosts configured.".format(environment))

    restricted_roles = set(roles)

    if restricted_roles:
        # If roles were specified, restrict mapping to those roles
        mapping = dict([(host, set(get_roles_for_host(host)) & restricted_roles) for host in hosts])
    else:
        # Otherwise, use all roles
        mapping = dict([(host, set(get_roles_for_host(host))) for host in hosts])

    # Validate that all hosts have at least one role
    for host, applicable_roles in mapping.iteritems():
        if not applicable_roles:
            if restricted_roles:
                raise Exception("Host '{}' does not have any of the specified roles".format(host))
            else:
                raise Exception("Host '{}' does not have any configured roles".format(host))

    return mapping
