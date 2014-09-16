"""
Allows custom jinja filters.
"""
from ujson import dumps
from fabric.api import env
from random import shuffle

### Built-in filters ###


def select(value, key):
    """
    Select a key from a dictionary.

    If ``value`` is not a dictionary or ``key`` does not exist in it,
    the ``value`` is returned as is.
    """

    return value.get(key, value) if isinstance(value, dict) else value


def rotate(list_, pivot):
    """
    Rotate a list around a pivot.
    """
    try:
        pos = list_.index(pivot)
    except ValueError:
        # pivot not in list
        return list_
    else:
        return list_[pos:] + list_[:pos]


def map_format(sequence, format):
    """
    Apply format string on elements in sequence.

    :param format: format string. can use one positional format argument, i.e. '{}' or '{0}',
                   which will map to elements in the sequence.
    """
    return [format.format(item) for item in sequence]

def select_with_components_on_current_host(dictionary):
    """
    select values from the ``dictionary`` based on the
    keys being the names of the components on the current host
    """

    if not dictionary:
        return []

    return [dictionary.get(name, [])
            for name in
            sorted(set([component.name
                        for component in
                        env.environmentdef.settings.for_env(env.environmentdef.name).components()
                        if component.host == env.host_string]))]


def flatten_list(unflattened_list):
    """
    Flatten a list of lists of lists ....
    """
    flattened_list = []
    for item in unflattened_list:
        if type(item) is list:
            flattened_list.extend(flatten_list(item))
        elif item:
            flattened_list.append(item)
    return flattened_list


def shuffle_list(target_list):
    shuffle(target_list)
    return target_list


def join_json(list_to_join, delimiter):
    """
    Join the json of each member of the ``list_to_join`` on ``delimiter``.
    """
    return delimiter.join([dumps(item) for item in list_to_join])


def get_json(target):
    return dumps(target)

def built_in_filters():
    """
    Confab built-in Jinja filters.
    """
    return [
        flatten_list,
        get_json,
        join_json,
        map_format,
        rotate,
        select,
        select_with_components_on_current_host,
        shuffle_list,
    ]



### End built-in filters ###


class JinjaFiltersRegistry(object):
    """
    Registry of custom Jinja filters that are applied on Jinja environments
    when Confab generates templates.
    """
    def __init__(self):
        self._filters = set(built_in_filters())

    def add_filter(self, filter):
        self._filters.add(filter)

    def remove_filter(self, filter):
        try:
            self._filters.remove(filter)
        except KeyError:
            return False
        return True

    @property
    def filters(self):
        return {filter.__name__: filter for filter in self._filters}

    def register(self, environment):
        """
        Register filters on a Jinja environment object.
        """
        for name, filter in self.filters.iteritems():
            environment.filters[name] = filter


class JinjaFilters(object):
    """
    Context manager for Jinja filters.
    """
    def __init__(self, *filters):
        self._filters = filters

    def __enter__(self):
        for filter in self._filters:
            add_jinja_filter(filter)

    def __exit__(self, type, value, traceback):
        for filter in self._filters:
            remove_jinja_filter(filter)


def add_jinja_filter(filter):
    """
    Add a custom jinja filter.
    """
    jinja_filters.add_filter(filter)


def remove_jinja_filter(filter):
    """
    Remove a custom jinja filter.
    """
    return jinja_filters.remove_filter(filter)


jinja_filters = JinjaFiltersRegistry()
