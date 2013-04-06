"""
Representation of and iteration through defined hosts, environments, and roles.
"""
from os.path import join
from warnings import warn

from confab.files import _import


class Settings(object):
    """
    Collection of environment, role, and component definitions.
    """

    KEYS = ["environmentdefs", "roledefs", "componentdefs"]

    def __init__(self):
        self.environmentdefs = {}
        self.roledefs = {}
        self.componentdefs = {}

    def load_from_module(self, dir_name, module_name='settings'):
        """
        Load settings from a Python module in the specified directory.
        """
        settings = _import(module_name, dir_name)
        for key in Settings.KEYS:
            setattr(self, key, getattr(settings, key, {}))

    def load_from_dict(self, dct):
        """
        Load settings from a Python dictionary.
        """
        for key in Settings.KEYS:
            setattr(self, key, dct.get(key, {}))

    def roles_for_host(self, host):
        """
        Compute complete list of roles for a host.
        """
        return [role for (role, hosts) in self.roledefs.iteritems() if host in hosts]

    def for_env(self, environment):
        """
        Obtain a specific environment definition.

        Raises exceptions if the environment is not known
        """
        if not environment:
            raise ValueError("Environment was not specified")
        if environment not in self.environmentdefs:
            raise KeyError("Environment '{}' is not defined".format(environment))
        if not self.environmentdefs[environment]:
            warn("Environment '{}' does not have any hosts defined.".format(environment))
        for host in self.environmentdefs[environment]:
            if not self.roles_for_host(host):
                raise Exception("Host '{}' does not have any configured roles".format(host))
        return EnvironmentDefinition(self, environment)


class EnvironmentDefinition(object):
    """
    A specific environment with an optional selection of specific hosts or
    roles in the environment.
    """

    def __init__(self, settings, name, selected_hosts=None, selected_roles=None):
        """
        Constructor should not be called directly. Either use `Settings.from_env()`,
        `EnvironmentDefinition.with_hosts()` or `EnvironmentDefinition.with_roles()`
        """
        self.settings = settings
        self.name = name
        self.selected_hosts = selected_hosts or []
        self.selected_roles = selected_roles or []
        self.host_roles = self._resolve_host_roles()

    def with_hosts(self, *hosts):
        """
        Select hosts from within this environment.

        Raises KeyError if hosts are not defined in this environment.
        """
        # Forbid any hosts not in environment
        for host in hosts:
            if host not in self.settings.environmentdefs[self.name]:
                raise KeyError("Host '{host}' is not a member of the environment '{env}'"
                               .format(host=host, env=self.name))
        # Return an environment restricted to these hosts
        return EnvironmentDefinition(self.settings,
                                     self.name,
                                     self.selected_hosts + list(hosts),
                                     self.selected_roles)

    def with_roles(self, *roles):
        """
        Select roles from within this environment.

        Raises KeyError if role is not recognized.
        """
        # Forbid any unknown role
        for role in roles:
            if role not in self.settings.roledefs:
                raise KeyError("Role '{}' is not defined.".format(role))
        # Return an environment restricted to these roles
        return EnvironmentDefinition(self.settings,
                                     self.name,
                                     self.selected_hosts,
                                     self.selected_roles + list(roles))

    def all(self):
        """
        Iterate through all valid host and role combinations.
        """
        return list(self.iterall())

    def iterall(self):
        """
        Iterate through all valid host and role combinations.
        """
        for host, roles in self.host_roles.iteritems():
            for role in roles:
                yield HostAndRoleDefinition(self, host, role)

    def components(self):
        """
        Iterate through all valid components of all host and role combinations.
        """
        return list(self.itercomponents())

    def itercomponents(self):
        """
        Iterate through all valid components of all host and role combinations.
        """
        for host_and_role in self.iterall():
            for component in host_and_role.itercomponents():
                yield component

    def _resolve_host_roles(self):
        """
        Compute the most appropriate mapping from host to roles.
        """
        host_roles = {}
        hosts = self.selected_hosts or self.settings.environmentdefs[self.name]
        for host in hosts:
            roles = self.settings.roles_for_host(host)
            # If no roles are selected
            if not self.selected_roles:
                # Use all roles
                host_roles[host] = roles
            else:
                # Otherwise, filter out non-selected roles
                selected_roles = filter(lambda role: role in self.selected_roles, roles)
                if selected_roles:
                    # And exclude hosts that have no such roles
                    host_roles[host] = selected_roles
        return host_roles


class HostAndRoleDefinition(object):
    """
    A host and role in the context of a specific environment.
    """

    def __init__(self, environment, host, role):
        """
        Constructor should not be called directly.
        """
        self.environment = environment
        self.host = host
        self.role = role

    def __iter__(self):
        return iter([self.environment.name, self.host, self.role])

    def __repr__(self):
        return str((self.environment.name, self.host, self.role))

    def components(self):
        return list(self.itercomponents())

    def itercomponents(self):
        if self.role in self.environment.settings.componentdefs:
            for component in self._expand_components(self.role, '', {}):
                yield ComponentDefinition(self, component)

    def _expand_components(self, component, path, seen):
        component_path = join(path, component)

        if component in seen:
            raise Exception("Detected cycle or multiple paths with role/component '{}'"
                            " ('{}' and '{}')".format(component,
                                                      seen[component],
                                                      component_path))
        seen[component] = component_path

        if component not in self.environment.settings.componentdefs:
            return [component]

        components = []
        for c in self.environment.settings.componentdefs.get(component):
            components += self._expand_components(c, component_path, seen)

        return components


class ComponentDefinition(object):
    """
    A component in the context of a specific host and role.
    """

    def __init__(self, host_and_role, name):
        """
        Constructor should not be called directly.
        """
        self.host_and_role = host_and_role
        self.name = name

    def __iter__(self):
        return iter([self.host_and_role.environment.name,
                     self.host_and_role.host,
                     self.host_and_role.role,
                     self.name])

    def __repr__(self):
        return str((self.host_and_role.environment.name,
                    self.host_and_role.host,
                    self.host_and_role.role,
                    self.name))


if __name__ == '__main__':
    # Example usage
    settings = Settings()

    dct = {
        "environmentdefs": {
            "dev": ["webhost", "queuehost", "dbhost"]
        },
        "roledefs": {
            "web": ["webhost"],
            "queue": ["queuehost"],
            "db": ["dbhost"]
        },
        "componentdefs": {
            "common": ["sparkle", "smsrouter", "invitations"],
            "web": ["gateway", "common"],
            "queue": ["notifier", "common"]
        }
    }

    settings.load_from_dict(dct)

    # Use Case #1: Iterate over all hosts and roles
    for host_and_role in settings.for_env("dev").iterall():
        print host_and_role

    # Use Case #2: Iterate over selected hosts and/or roles
    for host_and_role in settings.for_env("dev").with_hosts("webhost", "dbhost").with_roles("web").iterall():
        print host_and_role

    # Use Case #3: Iterate over all hosts and roles, then all components:
    for host_and_role in settings.for_env("dev").iterall():
        environment, host, role = host_and_role
        print host_and_role
        for component in host_and_role.itercomponents():
            print component

    # Use Case 34: Iterate over components only:
    for component in settings.for_env("dev").itercomponents():
        environment, host, role, name = component
        print component
