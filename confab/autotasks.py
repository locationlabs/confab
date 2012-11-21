"""
Auto-generate Fabric tasks for roles and environments.

The 'autogenerate_tasks' function creates fabric tasks to
set the current role or environment and are intended to be
used along side the other standard Confab tasks (e.g. pull)
to customize configuration data.

These tasks are somewhat experimental.
"""
from fabric.api import env
from fabric.state import commands


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
    for role in env.roledefs.iterkeys():
        _add_task('role_' + role,
                  lambda: setattr(env, 'role', role),
                  "Set role to '{role}'".format(role=role))

    try:
        for environment in env.environmentdefs.iterkeys():
            _add_task('env_' + environment,
                      lambda: setattr(env, 'environment', environment),
                      "Set environment to '{environment}'".format(environment=environment))
    except AttributeError:
        # environment defs not configured
        pass
