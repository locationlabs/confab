"""
Representation of and iteration through defined hosts, environments, and roles.
"""
from warnings import warn
from confab.files import _import

import os


class Settings(object):
    """
    Collection of environment, role, and component definitions.

    :param directory: optional configuration directory

    Supports convenient iteration. For example:

        # Iterate over all hosts and roles
        for host_and_role in settings.for_env("env").all():
            print host_and_role

        # Iterate over selected hosts and/or roles
        for host_and_role in settings.for_env("env").with_hosts("host1", "host2").with_roles("role1").all():
            print host_and_role

        # Iterate over all hosts and roles, then all components
        for host_and_role in settings.for_env("dev").all():
            environment, host, role = host_and_role
            for component in host_and_role.components():
                print component

        # Iterate over components
        for component in settings.for_env("dev").components():
            environment, host, role, name = component
            print component
    """

    KEYS = ["environmentdefs", "roledefs", "componentdefs"]

    def __init__(self, directory=None):
        self.directory = directory
        self.environmentdefs = {}
        self.roledefs = {}
        self.componentdefs = {}

    @classmethod
    def load_from_module(cls, settings_path=None):
        """
        Load settings from a Python module.

        :param settings_path: path to settings module. a full path or directory name.
                              module name defaults to 'settings'. directory defaults
                              to the current working directory.
        """
        if settings_path:
            if settings_path.endswith(".py"):
                dir_name, module = os.path.split(settings_path)
                module_name, _ = os.path.splitext(module)
            else:
                dir_name, module_name = settings_path, None
        else:
            dir_name, module_name = os.getcwd(), None

        settings_ = Settings(dir_name)
        try:
            module = _import(module_name or 'settings', dir_name)
        except ImportError as e:
            raise Exception("Unable to load {settings}: {error}"
                            .format(settings=os.path.join(dir_name, module_name or "settings.py"),
                                    error=e))

        for key in Settings.KEYS:
            setattr(settings_, key, getattr(module, key, {}))
        return settings_

    @classmethod
    def load_from_dict(cls, dct):
        """
        Load settings from a Python dictionary.
        """
        settings = Settings()
        for key in Settings.KEYS:
            setattr(settings, key, dct.get(key, {}))
        return settings

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
            if not self._roles_for_host(host):
                raise Exception("Host '{}' does not have any configured roles".format(host))
        return EnvironmentDefinition(self, environment)

    def all(self):
        """
        Iterate through all valid enviornments.
        """
        for environment in self.environmentdefs:
            yield self.for_env(environment)

    def _roles_for_host(self, host):
        """
        Compute complete list of roles for a host.
        """
        return [role for (role, hosts) in self.roledefs.iteritems() if host in hosts]


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

    @property
    def directory(self):
        """
        Return the configuration directory (if any)
        """
        return self.settings.directory

    @property
    def host_roles(self):
        """
        Return the host to roles mapping.
        """
        return self._resolve_host_roles()

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
        for host, roles in self.host_roles.iteritems():
            for role in roles:
                yield HostAndRoleDefinition(self, host, role)

    def components(self):
        """
        Iterate through all valid components of all host and role combinations.
        """
        for host_and_role in self.all():
            for component in host_and_role.components():
                yield component

    def _resolve_host_roles(self):
        """
        Compute the most appropriate mapping from host to roles.
        """
        host_roles = {}
        hosts = self.selected_hosts or self.settings.environmentdefs[self.name]
        for host in hosts:
            roles = self.settings._roles_for_host(host)
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

    def __init__(self, environmentdef, host, role):
        """
        Constructor should not be called directly.
        """
        self.environmentdef = environmentdef
        self.host = host
        self.role = role

    def __iter__(self):
        return iter([self.environment, self.host, self.role])

    def __repr__(self):
        return str((self.environment, self.host, self.role))

    @property
    def environment(self):
        return self.environmentdef.name

    def components(self):
        # If a role has no components, will generate a component named after the role
        for component in self._expand_components(self.role, '', {}):
            yield ComponentDefinition(self, component)

    def _expand_components(self, component, path, seen):
        component_path = os.path.join(path, component)

        if component in seen:
            raise Exception("Detected cycle or multiple paths with role/component '{}'"
                            " ('{}' and '{}')".format(component,
                                                      seen[component],
                                                      component_path))
        seen[component] = component_path

        if component not in self.environmentdef.settings.componentdefs:
            return [component]

        components = []
        for c in self.environmentdef.settings.componentdefs.get(component):
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

    @property
    def environment(self):
        return self.host_and_role.environment

    @property
    def host(self):
        return self.host_and_role.host

    @property
    def role(self):
        return self.host_and_role.role

    def __iter__(self):
        return iter([self.environment,
                     self.host,
                     self.role,
                     self.name])

    def __repr__(self):
        return str((self.environment,
                    self.host,
                    self.role,
                    self.name))
