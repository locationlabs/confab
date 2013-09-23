"""
Manage hook functions to be used within a DataLoader to load additional data by scope.
"""


class Hook(object):
    """
    Class representation of a hook.
    * hook_func to call
    * scope in which to call it
    * filter_func to determine whether it should be called for specific component
    """
    def __init__(self, hook_func, filter_func=None):
        self._hook_func = hook_func
        self._filter_func = filter_func
        self._data = None

    def __call__(self, module_name):
        if self._data is None:
            self._data = self._hook_func(module_name)
        return self._data

    def __eq__(self, other):
        if type(self) is type(other):
            return (self._hook_func == other._hook_func and
                    self._filter_func == other._filter_func)
        return False

    def filter(self, componentdef):
        if self._filter_func is None:
            return True
        return self._filter_func(componentdef)


class HookRegistry(object):
    """
    Registry of hooks to be used by DataLoader.
    """
    def __init__(self):
        self._hooks = {}

    def add_hook(self, scope, hook):
        self._hooks.setdefault(scope, []).append(hook)

    def remove_hook(self, scope, hook):
        try:
            self._hooks.get(scope, []).remove(hook)
        except ValueError:
            return False
        return True

    def for_scope(self, scope):
        return self._hooks.get(scope, [])


class ScopeAndHooks(object):
    """
    Context manager for Hooks. Accepts one or more hooks with associated scope.
    """
    def __init__(self, *scope_and_hooks):
        self._scope_and_hooks = scope_and_hooks

    def __enter__(self):
        for scope, hook in self._scope_and_hooks:
            add_data_hook(scope, hook)

    def __exit__(self, type, value, traceback):
        for scope, hook in self._scope_and_hooks:
            remove_data_hook(scope, hook)


def add_data_hook(scope, hook):
    hooks.add_hook(scope, hook)


def remove_data_hook(scope, hook):
    return hooks.remove_hook(scope, hook)


hooks = HookRegistry()
