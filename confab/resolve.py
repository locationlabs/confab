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
        if not hosts:
            raise Exception("Unrecognized or mis-configured environment: {}; no hosts found.".format(environment))

    if roles:
        # If roles were specified, restrict mapping to those roles
        restricted_roles = set(roles)
        mapping = dict([(host, set(get_roles_for_host(host)) & restricted_roles) for host in hosts])
    else:
        # Otherwise, use all roles
        mapping = dict([(host, set(get_roles_for_host(host))) for host in hosts])

    # Validate that all hosts have at least one role
    for host, roles in mapping.iteritems():
        if not roles:
            raise Exception("No roles applicable for host: {}".format(host))

    return mapping
