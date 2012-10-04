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

def _is_not_temporary(file_name):
    """
    Return whether a file name represents a temporary file.
    
    When listing configuration files, temporary files will be ignored.
    """
    return not file_name.endswith('~')

def _get_mime_type(file_name):
    """
    Return the mime type of a file.
    
    The mime_type will be used to determine if a configuration file is text.
    """
    return Magic(mime=True).from_file(file_name)

def make_default_options():
    """
    Return a default set of options.
    """
    return _AttributeDict({
            'dest_dir': None,
            'local_dir': None,
            'is_text': _is_text,
            'filter_func': _is_not_temporary,
            'get_mime_type': _get_mime_type
            })
