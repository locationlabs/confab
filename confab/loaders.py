"""
Jinja2 Environment loading helper functions.

Confab's options need to be configured with a 'get_jinja2_environment' 
function, which should return an Environment using a Loader that 
supports list_templates(). All subsequent confab operations will use
these templates.

The default Jinja2 Loaders assume a charset (default: utf-8), which means
it will take special effort to handle binary data. Confab is not designed
as a general file copying mechanism; it is probably better to modify
'options.filter_func' to ignore binary files if you must have them in
your templates directory.
"""

from jinja2 import Environment, FileSystemLoader, PackageLoader, StrictUndefined

def load_from_dir(dir_name):
    """
    Load a Jinja2 Environment from a directory name.
    """
    return Environment(loader=FileSystemLoader(dir_name),
                       undefined=StrictUndefined)

def load_from_package(package_name):
    """
    Load a Jinja2 Environment from a package name.
    """
    return Environment(loader=PackageLoader(package_name),
                       undefined=StrictUndefined)

