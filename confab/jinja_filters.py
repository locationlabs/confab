"""
Allows custom jinja filters.
"""

from jinja2.filters import contextfilter

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


def _hosts_with_roles(context, role):
    """
    returns the list of host names for the specified ``role`` in the current environment
    defined by ``context``.

    :param role: role to query
    """

    environmentdef = context["env"]["environmentdef"]
    current_env = environmentdef.settings.for_env(environmentdef.name)
    try:
        return [host.host for host in current_env.with_roles(role).hosts()]
    except KeyError:
        return []


@contextfilter
def pick_value_per_host(context, role_values_pair):
    """
    Pick a value for the current host for hosts in ``role``, from a list of ``values```.
    If ``values`` is not a list then return it as is.

    :param role_values_pair: a pair of (role, values) where role is the role being worked on
    and values is the list to pick a value from or the value if there is no choice available.
    """

    role, values = role_values_pair
    return (values[_hosts_with_roles(context, role).index(context["confab"]["host"]) % len(values)]
            if isinstance(values, list)
            else values)


def built_in_filters():
    """
    Confab built-in Jinja filters.
    """
    return [
        select,
        rotate,
        map_format,
        pick_value_per_host,
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
