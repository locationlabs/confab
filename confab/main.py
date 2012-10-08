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

from confab.api import pull, push, diff, generate

from fabric.api import settings, hide
from fabric.network import disconnect_all
from optparse import OptionParser
import getpass
import os
import sys

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

    parser = OptionParser(usage="confab [options] command")

    parser.add_option('-d', '--directory', dest='directory', 
                      default=os.getcwd(),
                      help='Configuration directory [default: %default]')

    parser.add_option('-H', '--hosts', dest='hosts', 
                      default="",
                      help='comma-separated list of hosts to operate on')

    parser.add_option('-u', '--user', dest='user',
                      default=getpass.getuser(),
                      help='sername to use when connecting to remote hosts')


    opts, args = parser.parse_args()
    return parser, opts, args

def parse_task(name):
    """
    Translate task name to task.
    """
    return _tasks.get(name)

def main():
    """
    Main command line entry point.
    """
    try:
        # Parse and validate arguments
        parser, options, arguments = parse_options()

        if not options.hosts:
            parser.error('At least one host must be specified')

        if not arguments or len(arguments) != 1:
            parser.error('Exactly one task must be specified')

        task_name = arguments[0]
        (task, needs_templates, needs_remotes) = parse_task(task_name)

        # Identify task
        if not task:
            parser.error('Specified task must be one of: %s' % (', '.join(_tasks.keys())))

        # Construct task arguments
        kwargs = {'data_dir':      os.path.join(options.directory, 'data'),
                  'templates_dir': os.path.join(options.directory, 'templates')}

        if needs_templates:
            kwargs['generated_dir'] = os.path.join(options.directory, 'generated')
        if needs_remotes:
            kwargs['remotes_dir'] = os.path.join(options.directory, 'remotes')

        # Invoke task
        for host in options.hosts.split(','):
            with settings(hide('user'),
                          host_string=host,
                          user=options.user):
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
