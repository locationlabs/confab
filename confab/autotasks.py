"""
Auto-generate Fabric tasks for environments.

The 'autogenerate_tasks' function creates fabric tasks to
set the current environment definition and are intended to be
used as a setup step to other standard Confab tasks (e.g. pull)
to customize configuration data::

    fab dev:web,queue push
"""
from fabric.api import abort, env
from fabric.state import commands

from confab.definitions import Settings


def _add_task(name, task, doc):
    """
    Register a Fabric task.
    """
    task_wrapper = lambda *args: task(*args)
    setattr(task_wrapper, '__doc__', doc)
    commands[name] = task_wrapper


def generate_tasks(settings_path=None):
    """
    Autogenerate `env` tasks for all defined environments.
    """
    def create_task(settings, environment):
        def select_environment(*roles):
            if hasattr(env, "environmentdef"):
                abort("Environment already defined as '{}'".format(env.environmentdef.name))

            # Do not select hosts here.
            #
            # If `fab` is run with multiple hosts, this task will be run multiple
            # times, overwriting the value of "env.environmentdef". By not selecting hosts
            # here, we ensure that the same environmentdef will be loaded each
            # time. See also confab.iter:iter_conffiles
            env.environmentdef = settings.for_env(environment).with_roles(*roles)
        return select_environment

    settings = Settings.load_from_module(settings_path)

    for environment in settings.environmentdefs.iterkeys():
        _add_task(environment,
                  create_task(settings, environment),
                  "Set environment to '{environment}'".format(environment=environment))
