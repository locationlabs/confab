"""
Options for managing Confab.
"""
from os.path import basename
from fabric.api import task
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


def _is_not_internal(file_name):
    """
    Return whether a file name does not represent internal usage.

    When listing configuration files, we want to omit internal
    files, especially if they are used as Jinja includes
    """
    return not basename(file_name).startswith('_')


def _filter_func(file_name):
    """
    Return the default filter func, which excludes temporary and internal files.
    """
    return _is_not_temporary(file_name) and _is_not_internal(file_name)


def _get_mime_type(file_name):
    """
    Return the mime type of a file.

    The mime_type will be used to determine if a configuration file is text.
    """
    return Magic(mime=True).from_file(file_name)


def _diff(a, b, fromfile=None, tofile=None):
    """
    Return a diff using '---', '+++', and '@@' control lines.

    By default, uses unified_diff.
    """
    return unified_diff(a, b, fromfile=fromfile, tofile=tofile)


def _as_dict(module):
    """
    Returns publicly names values in module's __dict__.
    """
    try:
        return {k: v for k, v in module.__dict__.iteritems() if not k[0:1] == '_'}
    except AttributeError:
        return {}


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

    # How do filter available templates within the jinja environment?
    'filter_func': _filter_func,

    # How to determine diffs?
    'diff': _diff,

    # How to get dictionary configuration from module data?
    'module_as_dict': _as_dict,

    # What is the name of the template directory?
    'get_templates_dir': lambda: 'templates',

    # What is the name of the data directory?
    'get_data_dir': lambda: 'data',

    # What is the name of the generated directory?
    'get_generated_dir': lambda: 'generated',

    # What is the name of the remotes directory?
    'get_remotes_dir': lambda: 'remotes',
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
