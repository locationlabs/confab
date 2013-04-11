"""
Generate configuration files into generated_dir.
"""
from fabric.api import abort, env, task

from confab.conffiles import iterconffiles
from confab.output import status
from confab.validate import validate_generate


@task
def generate(templates_dir=None,
             data_dir=None,
             generated_dir=None):
    """
    Generate configuration files.
    """
    validate_generate(templates_dir, data_dir, generated_dir)

    if not env.environmentdef:
        abort("No environment defined")

    for conffiles in iterconffiles(env.environmentdef, templates_dir, data_dir):
        status("Generating templates for '{environment}' and '{role}'",
               environment=env.environmentdef.name,
               role=conffiles.role)

        conffiles.generate(generated_dir)
