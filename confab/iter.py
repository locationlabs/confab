"""
Iterations over hosts, roles, components, config files.
"""

from fabric.api import env, settings, abort
from os.path import join
from os import getcwd

from confab.options import options
from confab.validate import assert_exists
from confab.loaders import FileSystemEnvironmentLoader
from confab.data import DataLoader
from confab.conffiles import ConfFiles


def iter_hosts_and_roles():
    """
    Iterate over all hosts and roles in the configured environment.
    """
    if 'environmentdef' not in env:
        abort("Environment needs to be configured")

    environmentdef = env.environmentdef

    # If we're running via `fab`, we should restrict the environment
    # to the current host.
    if env.host_string:
        environmentdef = environmentdef.with_hosts(env.host_string)

    for host_and_role in environmentdef.iterall():
        # fabric needs the host_string if we're calling from main()
        with settings(host_string=host_and_role.host):
            yield host_and_role


def iterconffiles(directory=None):
    """
    Generate ConfFiles objects for each host_and_role in an environment.

    Uses the default FileSystemEnvironmentLoader and DataLoader.
    """
    hosts_and_roles = iter_hosts_and_roles()
    directory = directory or env.environmentdef.directory or getcwd()

    # Construct directories
    templates_dir = join(directory, options.get_templates_dir())
    data_dir = join(directory, options.get_data_dir())
    assert_exists(templates_dir, data_dir)

    for host_and_role in hosts_and_roles:
        yield ConfFiles(host_and_role,
                        FileSystemEnvironmentLoader(templates_dir),
                        DataLoader(data_dir),
                        directory)
