"""
Iterations over :term:`hosts<host>`, :term:`roles<role>`,
:term:`components<component>` and config files.
"""

from fabric.api import env, settings, abort
from os.path import join
from pkg_resources import iter_entry_points
from warnings import warn

from confab.options import options
from confab.validate import assert_exists
from confab.loaders import FileSystemEnvironmentLoader
from confab.data import DataLoader
from confab.conffiles import ConfFiles


def _get_environmentdef():
    """
    Retreive the EnvironmentDefinition from the fabric env.
    """
    if 'environmentdef' not in env:
        abort("Environment needs to be configured")

    environmentdef = env.environmentdef

    # If we're running via `fab`, we should restrict the environment
    # to the current host.
    if env.host_string:
        environmentdef = environmentdef.with_hosts(env.host_string)

    return environmentdef


def iter_hosts():
    """
    Iterate over all hosts in the configured environment.
    """
    environmentdef = _get_environmentdef()

    for host in environmentdef.hosts():
        # fabric needs the host_string if we're calling from main()
        with settings(host_string=host.host):
            yield host


def iter_hosts_and_roles():
    """
    Iterate over all hosts and roles in the configured environment.
    """
    environmentdef = _get_environmentdef()

    for host_and_role in environmentdef.all():
        # fabric needs the host_string if we're calling from main()
        with settings(host_string=host_and_role.host):
            yield host_and_role


def iter_conffiles(directory=None):
    """
    Generate :class:`~confab.conffiles.ConfFiles` objects for each
    ``host_and_role`` in an :term:`environment`.

    Uses the default :class:`~confab.loaders.FileSystemEnvironmentLoader` and
    :class:`~confab.data.DataLoader`.

    :param directory: Path to templates and data directories.
    """
    for host_and_role in iter_hosts_and_roles():
        yield make_conffiles(host_and_role, directory)


def make_conffiles(host_and_role, directory=None):
    """
    Create a :class:`~confab.conffiles.ConfFiles` object for a
    ``host_and_role`` in an :term:`environment`.

    Uses the default :class:`~confab.loaders.FileSystemEnvironmentLoader` and
    :class:`~confab.data.DataLoader`.

    :param directory: Path to templates and data directories.
    """
    directories = [directory or options.get_base_dir()]
    directories.extend(iter_extension_paths())

    # Construct directories
    templates_dirs = map(lambda dir: join(dir, options.get_templates_dir()), directories)
    assert_exists(*templates_dirs)
    data_dirs = map(lambda dir: join(dir, options.get_data_dir()), directories)
    assert_exists(*data_dirs)

    return ConfFiles(host_and_role,
                     FileSystemEnvironmentLoader(*templates_dirs),
                     DataLoader(data_dirs))


def iter_extension_paths():
    """
    Get templates paths from confab extension entry points.

    entry points should point to a callable that returns the base path
    to the data and templates directories.
    """
    for entry_point in iter_entry_points(group="confab.extensions"):
        try:
            path_func = entry_point.load()
            yield path_func()
        except ImportError as e:
            warn(str(e))
