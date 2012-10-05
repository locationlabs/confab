"""
Options for managin Confab.
"""

from fabric.utils import _AttributeDict
from magic import Magic

def _is_text(mime_type):
    """
    Return whether a mime type represents a text file.
    
    Only configuration files that are text will be treated as text; binary files 
    will be copied verbatim.
    """
    return mime_type.split('/')[0] == 'text'

def _is_empty(mime_type):
    """
    Return whether a mime type represents an empty file.
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

def _get_configuration_data():
    """
    Return configuration data as a dictionary.
    """
    return {}

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

        # How to determine if a mime_type represents text data?
        'is_text': _is_text,

        # How to determine if a mime_type represents an empty file?
        'is_empty': _is_empty,

        # How do filter available templates?
        'filter_func': _is_not_temporary,
        
        # How to load configuration?
        'get_configuration_data': _get_configuration_data
        })
