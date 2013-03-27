"""
Options for managing Confab.
"""

from fabric.api import env, task
from fabric.utils import _AttributeDict

from difflib import unified_diff
from magic import Magic
from re import match


def _should_render(mime_type):
    """
    Return whether a template file of with a particular mime type
    should be rendered.

    Some files may need to be excluded from template rendering;
    such files will be copied verbatim.
    """
    return next((True for pattern in ['text/', 'application/xml'] if match(pattern, mime_type)),
                False)


def _is_empty(mime_type):
    """
    Return whether a template file is an empty file.
    """
    return mime_type == 'inode/x-empty'


def _is_not_temporary(file_name):
    """
    Return whether a file name does not represent a temporary file.

    When listing configuration files, we usually want temporary
    files to be ignored.
    """
    return not file_name.endswith('~')


def _get_mime_type(file_name):
    """
    Return the mime type of a file.

    The mime_type will be used to determine if a configuration file is text.
    """
    return Magic(mime=True).from_file(file_name)


def _get_hostname():
    """
    Return the current target hostname.
    """
    return env.host_string


def _get_rolename():
    """
    Return the current target role.

    Assume the role value is being saved in Fabric's env;
    if not return None.
    """
    try:
        return env.role
    except AttributeError:
        return None


def _get_environmentname():
    """
    Return the current target environment.

    Assume the environment value is being saved in Fabric's env;
    if not return None.
    """
    try:
        return env.environment
    except AttributeError:
        return None


def _diff(a, b, fromfile=None, tofile=None):
    """
    Return a diff using '---', '+++', and '@@' control lines.

    By default, uses unified_diff.
    """
    return unified_diff(a, b, fromfile=fromfile, tofile=tofile)

# Options that control how confab runs.
#
# These are in opposition to options likely to changed
# between different runs of confab, such as directories,
# environments, roles, hosts, etc.
options = _AttributeDict({
    # Should yes be assumed for interactive prompts?
    'assume_yes': False,

    # How to compute a file's mime_type?
    'get_mime_type': _get_mime_type,

    # How to determine if a template should be rendered?
    'should_render': _should_render,

    # How to determine if a template is an empty file?
    'is_empty': _is_empty,

    # How to determine the current host name?
    'get_hostname': _get_hostname,

    # How to determine the current role name?
    'get_rolename': _get_rolename,

    # How to determine the current environment name?
    'get_environmentname': _get_environmentname,

    # How do filter available templates within the jinja environment?
    'filter_func': _is_not_temporary,

    # How to determine diffs?
    'diff': _diff
})


class Options(object):
    """
    Context manager to temporarily set options.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.previous = {}

    def __enter__(self):
        for (k, v) in self.kwargs.iteritems():
            self.previous[k] = options.get(k)
            options[k] = v
        return self

    def __exit__(self, exc_type, value, traceback):
        for k in self.kwargs.keys():
            options[k] = self.previous[k]


@task
def assume_yes():
    """
    Set the option to assume_yes in other tasks.
    """
    options.assume_yes = True
