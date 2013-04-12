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
from fabric.api import settings
from fabric.network import disconnect_all

from confab.api import pull, push, diff, generate
from confab.definitions import Settings
from confab.options import Options
from gusset.output import configure_output


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


def get_environmentdef(parser, options):
    try:
        settings_ = Settings.load_from_module(options.directory)
    except ImportError as e:
        parser.error("Unable to load {settings}: {error}"
                     .format(settings=os.path.join(options.directory, "settings.py"),
                             error=e))

    # Normalize and resolve hosts to roles mapping
    try:
        selected_hosts = options.hosts.split(",") if options.hosts else []
        selected_roles = options.roles.split(",") if options.roles else []
        environmentdef = settings_.for_env(options.environment)
        environmentdef = environmentdef.with_hosts(*selected_hosts)
        environmentdef = environmentdef.with_roles(*selected_roles)
        return environmentdef
    except Exception as e:
        parser.error(e)


def get_task(parser, options, arguments):
    # Determine task
    try:
        task_name = arguments[0]
        (task, needs_templates, needs_remotes) = _tasks[task_name]
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
    return task, kwargs


def main():
    """
    Main command line entry point.
    """
    try:
        # Parse and validate arguments
        parser, options, arguments = parse_options()

        configure_output(options.verbosity,
                         options.quiet)

        environmentdef = get_environmentdef(parser, options)
        task, kwargs = get_task(parser, options, arguments)

        with settings(environmentdef=environmentdef,
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
