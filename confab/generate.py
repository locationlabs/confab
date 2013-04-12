"""
Generate configuration files into generated_dir.
"""
from fabric.api import abort, env, task
from gusset.output import status
from gusset.validation import with_validation

from confab.conffiles import iterconffiles
from confab.validate import assert_exists, assert_may_be_created


@task
@with_validation
def generate(templates_dir, data_dir, generated_dir):
    """
    Generate configuration files.
    """
    assert_exists(templates_dir, data_dir)
    assert_may_be_created(generated_dir)

    if not env.confab:
        abort("Confab needs to be configured")

    for conffiles in iterconffiles(env.confab, templates_dir, data_dir):
        status("Generating templates for '{environment}' and '{role}'",
               environment=env.confab.name,
               role=conffiles.role)

        conffiles.generate(generated_dir)
