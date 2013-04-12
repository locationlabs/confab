"""
Determine the difference between remote and generated configuration files.
"""
from fabric.api import abort, env, task
from gusset.output import status
from gusset.validation import with_validation

from confab.conffiles import iterconffiles
from confab.validate import assert_exists, assert_may_be_created


@task
@with_validation
def diff(templates_dir,
         data_dir,
         generated_dir,
         remotes_dir):
    """
    Show configuration file diffs.
    """
    assert_exists(templates_dir, data_dir)
    assert_may_be_created(generated_dir, remotes_dir)

    if not env.environmentdef:
        abort("No environment defined")

    for conffiles in iterconffiles(env.environmentdef, templates_dir, data_dir):
        status("Computing template diffs for '{environment}' and '{role}'",
               environment=env.environmentdef.name,
               role=conffiles.role)

        conffiles.diff(generated_dir, remotes_dir)
