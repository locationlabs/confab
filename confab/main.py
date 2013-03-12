"""
Main function declaration for confab console_script.

Confab may be used from within a fabfile or as a library. The main
function here is provided as a simple default way to invoke confab's
tasks:

 -  A single directory root is assumed, with templates, data, generated
    and remotes directories defined as subdirectories.

 -  A host list must be provided on the command line.

For more complex invocation, a custom fabfile may be more appropriate.
"""
from fabric.api import hide, settings
from fabric.network import disconnect_all
from optparse import OptionParser
import getpass
import os
import sys

from confab.api import pull, push, diff, generate
from confab.options import Options
from confab.model import (load_model_from_dir,
                          get_hosts_for_environment,
                          get_roles_for_host,
                          has_roles)

_tasks = {'diff':     (diff,     True,  True),
          'generate': (generate, True,  False),
          'pull':     (pull,     False, True),
          'push':     (push,     True,  True)}


def parse_options():
    """
    Parse command line options.

    Directory and host are required, though directory defaults to the current
    working directory.
    """

    usage = "confab [options] {tasks}".format(tasks="|".join(_tasks.keys()))
    parser = OptionParser(usage=usage)

    parser.add_option('-d', '--directory', dest='directory',
                      default=os.getcwd(),
                      help='directory from which to load configuration [default: %default]')

    parser.add_option('-e', '--environment', dest='environment',
                      default="local",
                      help='environment to operate on [default: %default]')

    parser.add_option('-H', '--hosts', dest='hosts',
                      default="",
                      help='comma-separated list of hosts to operate on')

    parser.add_option('-R', '--roles', dest='roles',
                      default="",
                      help='comma-separated list of roles to operate on')

    parser.add_option('-u', '--user', dest='user',
                      default=getpass.getuser(),
                      help='username to use when connecting to remote hosts')

    parser.add_option('-y', '--yes', dest='assume_yes',
                      action='store_true',
                      default=False,
                      help='automatically answer yes to prompts')

    opts, args = parser.parse_args()
    return parser, opts, args


def common_roles(hosts):
    """
    Determine the intersection of roles for all hosts.
    """
    roles = set(get_roles_for_host(hosts[0]))
    for host in hosts[1:]:
        roles = roles & set(get_roles_for_host(host))
    return roles


def resolve_model(parser, options):
    """
    Ensure that a valid environment, host, and model have been defined.

    If no hosts are defined, attempt to derive these from the current environment.
    If hosts are defined, validate that these are members of the current environment.

    If no roles are defined, attempt to derive these from the current hosts.
    If roles are defined, validate that hosts have these roles.
    """
    environment_hosts = get_hosts_for_environment(options.environment)

    # We must have an environmnt
    if not environment_hosts:
        parser.error("Unrecognized or missing environment definition: {environment}".
                     format(environment=options.environment))

    # Normalize
    options.hosts = options.hosts.split(",") if options.hosts else []
    options.roles = options.roles.split(",") if options.roles else []

    if options.hosts and options.roles:
        # Explicitly defined hosts and roles must match
        if common_roles(options.hosts) != set(options.roles):
            parser.error("Specified hosts do not match specified roles")
    elif options.hosts and not options.roles:
        # Use the common roles across all explicitly defined hosts
        options.roles = list(common_roles(options.hosts))
        if not options.roles:
            parser.error("Could not identify any roles that are shared by all specified hosts")
    elif not options.hosts and options.roles:
        # Subselect environment hosts that have all specified roles
        options.hosts = [host for host in environment_hosts if has_roles([host], options.roles)]
        # We must have some hosts
        if not options.hosts:
            parser.error("Could not identify any hosts that share all specified roles")
    else:
        # Use the common roles across all enviroment hosts
        options.hosts = environment_hosts
        options.roles = list(common_roles(options.hosts))
        if not options.roles:
            parser.error("Could not identify any roles that are shared by all environment hosts")


def main():
    """
    Main command line entry point.
    """
    try:
        # Parse and validate arguments
        parser, options, arguments = parse_options()

        try:
            load_model_from_dir(options.directory)
        except ImportError:
            parser.error('Could not find {settings}'.format(settings=os.path.join(options.directory,
                                                                                  'settings.py')))

        resolve_model(parser, options)

        if not arguments or len(arguments) != 1:
            parser.error('Exactly one task must be specified')

        task_name = arguments[0]
        try:
            (task, needs_templates, needs_remotes) = _tasks[task_name]
        except KeyError:
            parser.error('Specified task must be one of: {tasks}'.format(tasks=', '.join(_tasks.keys())))

        # Construct task arguments
        kwargs = {'data_dir': os.path.join(options.directory, 'data')}

        if needs_templates:
            kwargs['generated_dir'] = os.path.join(options.directory, 'generated')
        if needs_remotes:
            kwargs['remotes_dir'] = os.path.join(options.directory, 'remotes')

        # Invoke task once per host/role
        for host in options.hosts:
            for role in options.roles:

                # Scope templates dir by role
                kwargs['templates_dir'] = os.path.join(options.directory, 'templates', role)

                print "Running {task} on '{host}' for '{env}' and '{role}'".format(task=task_name,
                                                                                   host=host,
                                                                                   env=options.environment,
                                                                                   role=role)
                with settings(hide('user'),
                              environment=options.environment,
                              host_string=host,
                              role=role,
                              user=options.user):
                    with Options(assume_yes=options.assume_yes):
                        task(**kwargs)

    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.stderr.write("\nInterrupted\n")
        sys.exit(1)
    except:
        sys.excepthook(*sys.exc_info())
        sys.exit(1)
    finally:
        disconnect_all()
    sys.exit(0)
