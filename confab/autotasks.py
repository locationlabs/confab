"""
Auto-generate Fabric tasks for roles and environments.

The 'autogenerate_tasks' function creates fabric tasks to
set the current role or environment and are intended to be
used along side the other standard Confab tasks (e.g. pull)
to customize configuration data.

These tasks are somewhat experimental.
"""
from fabric.api import abort, env
from fabric.state import commands

from confab.definitions import Settings


def _add_task(name, task, doc):
    """
    Register a Fabric task.
    """
    task_wrapper = lambda: task()
    setattr(task_wrapper, '__doc__', doc)
    commands[name] = task_wrapper


def autogenerate_tasks():
    """
    Autogenerate role_ and env_ tasks for all defined roles and
    environments in the Fabric environment.

    Normally the roledefs and environment defs will be configured
    using 'load_model_from_dir' or similar.
    """
    settings = Settings()
    # XXX create separate task to load settings

    for environment in settings.environmentdefs.iterkeys():
        def select_environment():
            if hasattr(env, "environmentdef"):
                abort("Environment already defined as '{}'".format(env.environmentdef.name))
            env.environmentdef = settings.with_env(environment)

        _add_task('env_' + environment,
                  select_environment,
                  "Set environment to '{environment}'".format(environment=environment))

    for role in settings.roledefs.iterkeys():
        def select_role():
            if not hasattr(env, "environmentdef"):
                abort("Environment must be defined before role")
            env.environmentdef = env.environmentdef.with_roles(role)

        _add_task('role_' + role,
                  select_role,
                  "Select role '{}'".format(role))
