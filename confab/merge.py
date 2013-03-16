"""
Configuration data structure merging functions.

We expect to obtain hierarchical configurations as native dictionaries
and want to merge the higher precedence (override) data into the
lower precedence (default) data, potentially multiple times.

Merge rules are as follows:
 - Dictionaries are merged recursively by default.
 - Lists and primitives are replaced by default.
 - Callables are called to provide custom extension.

For example, a list of hosts in the default dictionary will normally
be replaced by values defined in the override dictionary; however if
the override dictionary's list is a callable, it can be made to do
something else, such as append a new host to the default list.
"""


def _best(default_value, has_override, override_value):
    """
    Return the best value according to the merge rules.
    """
    if not has_override:
        return default_value
    elif callable(override_value):
        # custom callable
        return override_value(default_value)
    elif isinstance(default_value, dict) and isinstance(override_value, dict):
        # merge recursively
        return _merge(default_value, override_value)
    else:
        # replace with override
        return override_value


def _iterkeys(default, override):
    """
    Return an iterator over the keys of the both dicts.
    """
    return iter(set(default.keys()) | set(override.keys()))


def _entry(default, override, key):
    """
    Return a dictionary entry with the best value from the default and
    override dictionaries.
    """
    return key, _best(default.get(key), key in override, override.get(key))


def _merge(default, override):
    """Recursively merge two dictionaries.
    """
    return dict(_entry(default, override, key) for key in _iterkeys(default, override))


def merge(*args):
    """Recursively merge multiple dictionaries.
    """
    return reduce(_merge, args, {})


class Append(list):
    """
    Customized callable list that appends its values to the default.
    """
    def __init__(self, *args):
        super(Append, self).__init__(args)

    def __call__(self, default):
        return (default or []) + self


def append(*args):
    return Append(*args)


class Prepend(list):
    """
    Customized callable list that prepends its values to the default.
    """

    def __init__(self, *args):
        super(Prepend, self).__init__(args)

    def __call__(self, default):
        return self + (default or [])


def prepend(*args):
    return Prepend(*args)


class UniqueUnion(list):
    """
    Customized callable list that adds its values to the default list
    preserving unique values.
    """

    def __init__(self, *args):
        super(UniqueUnion, self).__init__(args)

    def __call__(self, default):
        return list(set(default or []) | set(*self))


def unique_union(*args):
    return UniqueUnion(*args)
