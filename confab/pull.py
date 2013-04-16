"""
Pull configuration files from remote host into remotes_dir.
"""
from fabric.api import task
from gusset.output import status
from gusset.validation import with_validation

from confab.iter import iter_conffiles


@task
@with_validation
def pull(directory=None):
    """
    Pull remote configuration files.
    """
    for conffiles in iter_conffiles(directory):
        status("Pulling remote templates for '{environment}' and '{role}'",
               environment=conffiles.environment,
               role=conffiles.role)

        conffiles.pull()
