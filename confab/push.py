"""
Push generated configuration files to remote host.
"""
from fabric.api import abort, env, task

from confab.conffiles import iterconffiles
from confab.output import status
from confab.validate import validate_all


@task
def push(templates_dir=None,
         data_dir=None,
         generated_dir=None,
         remotes_dir=None):
    """
    Push configuration files.
    """
    validate_all(templates_dir, data_dir, generated_dir, remotes_dir)

    if not env.environmentdef:
        abort("No environment defined")

    for conffiles in iterconffiles(env.environmentdef, templates_dir, data_dir):
        status("Pushing templates for '{environment}' and '{role}'",
               environment=env.environmentdef.name,
               role=conffiles.role)

        conffiles.push(generated_dir, remotes_dir)
