"""
Allows custom jinja filters.
"""

### Built-in filters ###


def select(value, key):
    """
    Select a key from a dictionary.
    """
    if isinstance(value, dict):
        return value[key]
    return value


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
    """
    return [format.format(item) for item in sequence]


def built_in_filters():
    """
    Confab built-in Jinja filters.
    """
    return [
        select,
        rotate,
        map_format,
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
