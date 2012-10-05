"""
Options for managing Confab.
"""

from fabric.api import env
from fabric.utils import _AttributeDict
from magic import Magic
from socket import getfqdn

def _should_render(mime_type):
    """
    Return whether a template file of with a particular mime type should be rendered.
    
    Some files may need to be excluded from template rendering; such files will be 
    copied verbatim.
    """
    return mime_type.split('/')[0] == 'text'

def _is_empty(mime_type):
    """
    Return whether a template file is an empty file.
    """
    return mime_type == 'inode/x-empty'

def _is_not_temporary(file_name):
    """
    Return whether a file name does not represent a temporary file.
    
    When listing configuration files, we usually want temporary files to be ignored.
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
    return getfqdn(env.host_string)

# Options that control how confab runs.
#
# These are in opposition to options likely to changed
# between different runs of confab, such as directories, 
# environments, roles, hosts, etc.
options = _AttributeDict({
        # Should sudo be used with put and in lieu of run?
        'use_sudo': False,

        # How do compute a file's mime_type?
        'get_mime_type': _get_mime_type,

        # How to determine if a template should be rendered?
        'should_render': _should_render,

        # How to determine if a template is an empty file?
        'is_empty': _is_empty,

        # How to determine the current hostname?
        'get_hostname': _get_hostname,

        # How do filter available templates within the jinja environment?
        'filter_func': _is_not_temporary,
        })

class Options(object):
    """
    Context manager to temporarily set options.
    """

    def __init__(self,**kwargs):
        self.kwargs = kwargs
        self.previous = {}

    def __enter__(self):
        for (k,v) in self.kwargs.iteritems():
            self.previous[k] = options.get(k)
            options[k] = v
        return self

    def __exit__(self, exc_type, value, traceback):
        for k in self.kwargs.keys():
            options[k] = self.previous[k]


