"""
Pull configuration files from remote host into remotes_dir.
"""
from fabric.api import abort, env, task
from gusset.output import status
from gusset.validation import with_validation

from confab.conffiles import iterconffiles
from confab.validate import assert_exists, assert_may_be_created


@task
@with_validation
def pull(templates_dir, data_dir, remotes_dir):
    """
    Pull remote configuration files.
    """
    assert_exists(templates_dir, data_dir)
    assert_may_be_created(remotes_dir)

    if not env.confab:
        abort("Confab needs to be configured")

    for conffiles in iterconffiles(env.confab, templates_dir, data_dir):
        status("Pulling remote templates for '{environment}' and '{role}'",
               environment=env.confab.name,
               role=conffiles.role)

        conffiles.pull(remotes_dir)
