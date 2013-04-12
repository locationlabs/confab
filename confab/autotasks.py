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


def autogenerate_tasks(settings=None):
    """
    Autogenerate `env` tasks for all defined environments.

    Normally the roledefs and environment defs will be configured
    using 'load_model_from_dir' or similar.
    """
    settings = Settings.load_from_module(settings)

    for environment in settings.environmentdefs.iterkeys():
        def select_environment(*roles):
            if hasattr(env, "environmentdef"):
                abort("Environment already defined as '{}'".format(env.environmentdef.name))

            env.environmentdef = settings.for_env(environment).with_roles(*roles)

        _add_task(environment,
                  select_environment,
                  "Set environment to '{environment}'".format(environment=environment))
