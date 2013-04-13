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
import getpass
import os
import sys
from optparse import OptionParser
from fabric.api import env, settings
from fabric.network import disconnect_all
from gusset.output import configure_output

from confab.definitions import Settings
from confab.diff import diff
from confab.generate import generate
from confab.options import Options
from confab.pull import pull
from confab.push import push


_tasks = {"diff":     (diff,     True,  True),
          "generate": (generate, True,  False),
          "pull":     (pull,     False, True),
          "push":     (push,     True,  True)}


def parse_options():
    """
    Parse command line options.

    Directory and host are required, though directory defaults to the current
    working directory.
    """

    usage = "confab [options] {tasks}".format(tasks="|".join(_tasks.keys()))
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--directory", dest="directory",
                      default=os.getcwd(),
                      help="directory from which to load configuration [default: %default]")

    parser.add_option("-e", "--environment", dest="environment",
                      default="local",
                      help="environment to operate on [default: %default]")

    parser.add_option("-H", "--hosts", dest="hosts",
                      default="",
                      help="comma-separated list of hosts to operate on")

    parser.add_option("-q", "--quiet", dest="quiet",
                      action="store_true",
                      default=False,
                      help="minimize output verbosity")

    parser.add_option("-R", "--roles", dest="roles",
                      default="",
                      help="comma-separated list of roles to operate on")

    parser.add_option("-u", "--user", dest="user",
                      default=getpass.getuser(),
                      help="username to use when connecting to remote hosts")

    parser.add_option("-v", "--verbose", dest="verbosity",
                      action="count",
                      default=0,
                      help="control confab verbosity; by default, confab suppresses"
                      "most output. Additional -v flags increase verbosity.")

    parser.add_option("-y", "--yes", dest="assume_yes",
                      action="store_true",
                      default=False,
                      help="automatically answer yes to prompts")

    opts, args = parser.parse_args()
    return parser, opts, args


def load_environmentdef(environment,
                        settings_path=None,
                        hosts=None,
                        roles=None):
    """
    Load settings, construct an environment definition, and save in Fabric env
    as "confab" for use by subsequent confab tasks.

    :param environment: environment name
    :param settings_path: path to settings module
    :param hosts: comma delimited host list
    :param roles: comma delimited role list
    """

    settings_ = Settings.load_from_module(settings)

    # Normalize and resolve hosts to roles mapping
    selected_hosts = hosts.split(",") if hosts else []
    selected_roles = roles.split(",") if roles else []

    env.environmentdef = settings_.for_env(environment)
    env.environmentdef = env.environmentdef.with_hosts(*selected_hosts)
    env.environmentdef = env.environmentdef.with_roles(*selected_roles)
    return env.environmentdef


def get_task(parser, options, arguments):
    """
    Parse a task from command line arguments.

    Return the task function and its required arguments.
    """
    # Determine task
    try:
        task_name = arguments[0]
        (task_func, needs_templates, needs_remotes) = _tasks[task_name]
    except IndexError:
        parser.error("Please specify a task")
    except KeyError:
        parser.error("Specified task must be one of: {tasks}"
                     .format(tasks=", ".join(_tasks.keys())))

    # Construct task arguments
    kwargs = {"data_dir": os.path.join(options.directory, "data")}

    if needs_templates:
        kwargs["generated_dir"] = os.path.join(options.directory, "generated")
    if needs_remotes:
        kwargs["remotes_dir"] = os.path.join(options.directory, "remotes")

    kwargs["templates_dir"] = os.path.join(options.directory, "templates")
    return task_func, kwargs


def main():
    """
    Main command line entry point.
    """
    try:
        # Parse and validate arguments
        parser, options, arguments = parse_options()

        configure_output(options.verbosity,
                         options.quiet)

        try:
            load_environmentdef(environment=options.environment,
                                settings_path=options.directory,
                                hosts=options.hosts,
                                roles=options.roles)
        except Exception as e:
            parser.error(e)

        task_func, kwargs = get_task(parser, options, arguments)

        with settings(user=options.user):
            with Options(assume_yes=options.assume_yes):
                task_func(**kwargs)

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
