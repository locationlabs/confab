"""
Determine the difference between remote and generated configuration files.
"""
from fabric.api import abort, env, task
from gusset.output import status
from gusset.validation import with_validation

from confab.conffiles import iterconffiles


@task
@with_validation
def diff(directory):
    """
    Show configuration file diffs.
    """
    if not env.confab:
        abort("Confab needs to be configured")

    for conffiles in iterconffiles(env.confab, directory):
        status("Computing template diffs for '{environment}' and '{role}'",
               environment=env.confab.name,
               role=conffiles.role)

        conffiles.diff(directory)
