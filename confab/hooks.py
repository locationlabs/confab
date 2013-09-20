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
        self.hook_func = hook_func
        if filter_func is None:
            self.filter_func = lambda componentdef: True
        else:
            self.filter_func = filter_func
        self._data = None

    def __call__(self, module_name):
        if self._data is None:
            self._data = self.hook_func(module_name)
        return self._data

    def filter(self, componentdef):
        return self.filter_func(componentdef)


class HookRegistry(object):
    """
    Registry of hooks to be used by DataLoader.
    """
    def __init__(self):
        self._hooks = {}

    def add_hook(self, scope, hook):
        try:
            self._hooks[scope].append(hook)
        except KeyError:
            self._hooks[scope] = [hook]

    def remove_hook(self, scope, hook):
        try:
            self._hooks[scope].remove(hook)
        except (KeyError, ValueError):
            return False
        return True

    def for_scope(self, scope):
        try:
            return self._hooks[scope]
        except KeyError:
            return []


class ScopeAndHooks(object):
    """
    Context manager for Hooks. Accepts one or more hooks with associated scope.
    """
    def __init__(self, *scope_and_hooks):
        self._scope_and_hooks = scope_and_hooks

    def __enter__(self):
        for scope_and_hook in self._scope_and_hooks:
            scope, hook = scope_and_hook
            add_data_hook(scope, hook)

    def __exit__(self, type, value, traceback):
        for scope_and_hook in self._scope_and_hooks:
            scope, hook = scope_and_hook
            remove_data_hook(scope, hook)
        print type, value, traceback


def add_data_hook(scope, hook):
    hooks.add_hook(scope, hook)


def remove_data_hook(scope, hook):
    return hooks.remove_hook(scope, hook)


hooks = HookRegistry()
