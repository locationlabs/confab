"""
Output control utilities.
"""
import warnings
from fabric.api import env
from fabric.state import output
from fabric.utils import warn


def status(message, **kwargs):
    """
    Generate fabric-style output if and only if status output
    has been selected.
    """
    if not output.status:
        return
    print "[{hostname}] {message}".format(hostname=env.host_string,
                                          message=message.format(**kwargs))


def debug(message, **kwargs):
    """
    Generate fabric-style output if and only if debug output
    has been selected.
    """
    if not output.debug:
        return
    print "[{hostname}] {message}".format(hostname=env.host_string,
                                          message=message.format(**kwargs))


def warn_via_fabric(message, category, filename, lineno=None, line=None):
    """
    Adapt Python warnings to Fabric's warning output manager.
    """
    warn(message.message)


def configure_output(verbosity=0, quiet=False):
    """
    Configure verbosity level through Fabric's output managers.
    """
    output_levels = {
        "status": 0,
        "aborts": 0,
        "user": 1,
        "warnings": 1,
        "running": 1,
        "stdout": 2,
        "stderr": 2,
        "debug": 2
    }

    verbosity = verbosity if not quiet else -1

    # configure output manager levels via verbosity
    for manager, level in output_levels.iteritems():
        output[manager] = level <= verbosity

    # Hook up Python warnings to warning output manager
    warnings.showwarning = warn_via_fabric
    warnings.simplefilter("always", UserWarning)
