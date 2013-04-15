"""
Generate configuration files into generated_dir.
"""
from fabric.api import task
from gusset.output import status
from gusset.validation import with_validation

from confab.iter import iterconffiles


@task
@with_validation
def generate(directory=None):
    """
    Generate configuration files.
    """
    for conffiles in iterconffiles(directory):
        status("Generating templates for '{environment}' and '{role}'",
               environment=conffiles.environment,
               role=conffiles.role)

        conffiles.generate()
