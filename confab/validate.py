"""
Functions for validating user input to tasks.
"""

from fabric.api import abort, env
import os


def validate_templates_dir(templates_dir):
    """
    Template directory must be defined and exist.
    """
    if not templates_dir:
        abort('Please provide a valid templates directory')
    elif not os.path.isdir(templates_dir):
        abort('{templates_dir} is not a valid directory'.format(templates_dir=templates_dir))


def validate_data_dir(data_dir):
    """
    Data directory must be defined and exist.
    """
    if not data_dir:
        abort('Please provide a valid data_dir')
    elif not os.path.isdir(data_dir):
        abort('{data_dir} is not a valid directory'.format(data_dir=data_dir))


def validate_generated_dir(generated_dir):
    """
    Generated directory must be defined and not be a regular file.
    """
    if not generated_dir:
        abort('Please provide a valid generated_dir')
    elif os.path.exists(generated_dir) and not os.path.isdir(generated_dir):
        abort('{generated_dir} is not a valid directory'.format(generated_dir=generated_dir))


def validate_remotes_dir(remotes_dir):
    """
    Remotes directory must be defined and not be a regular file.
    """
    if not remotes_dir:
        abort('Please provide a valid remotes_dir')
    elif os.path.exists(remotes_dir) and not os.path.isdir(remotes_dir):
        abort('{remotes_dir} is not a valid directory'.format(remotes_dir=remotes_dir))


def validate_host():
    """
    Fabric host_string must be defined.
    """
    if not env.host_string:
        abort('Please specify a host or a role')


def validate_all(templates_dir, data_dir, generated_dir, remotes_dir):
    """
    Validate templates_dir, data_dir, generated_dir, remotes_dir, and host.
    """
    validate_templates_dir(templates_dir)
    validate_data_dir(data_dir)
    validate_generated_dir(generated_dir)
    validate_remotes_dir(remotes_dir)
    validate_host()


def validate_generate(templates_dir, data_dir, generated_dir):
    """
    Validate templates_dir, data_dir, generated_dir, and host.
    """
    validate_templates_dir(templates_dir)
    validate_data_dir(data_dir)
    validate_generated_dir(generated_dir)
    validate_host()


def validate_pull(templates_dir, data_dir, remotes_dir):
    """
    Validate templates_dir, data_dir, remotes_dir, and host.
    """
    validate_templates_dir(templates_dir)
    validate_data_dir(data_dir)
    validate_remotes_dir(remotes_dir)
    validate_host()
