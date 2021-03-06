from confab.merge import merge, append, prepend

from unittest import TestCase


class TestMerge(TestCase):

    def test_no_inputs(self):
        """
        Sane results if no inputs are provided.
        """

        merged = merge()

        self.assertEquals(merged, {})

    def test_no_overrride(self):
        """
        Sane results if no overrides are provided.
        """

        default = {
            'foo': 'bar'
        }

        merged = merge(default)

        self.assertEquals(merged, default)

    def test_override(self):
        """
        Overrides work as expected.
        """

        default = {
            'value1': 'foo',
            'list': ['foo'],
            'dict': {
                'value2': 'foo',
                'value3': 'foo'
            },
        }

        override = {
            'value1': 'bar',
            'list': ['bar'],
            'dict': {
                'value2': 'bar',
                'value4': 'bar'
            },
        }

        merged = merge(default, override)

        # primitive values are replaced
        self.assertEqual('bar', merged['value1'])

        # lists are replaced
        self.assertEqual(['bar'], merged['list'])

        # dictionaries are recursively merged
        self.assertEqual('bar', merged['dict']['value2'])
        self.assertEqual('foo', merged['dict']['value3'])
        self.assertEqual('bar', merged['dict']['value4'])

    def test_override_custom(self):
        """
        Custom append() and prepend() lists append and prepend to
        the origin using N-ary merge.
        """

        default = {
            'list': ['two']
        }

        override1 = {
            'list': append('three', 'four')
        }

        override2 = {
            'list': prepend('one')
        }

        merged = merge(default, override1, override2)

        self.assertEquals(merged['list'], ['one', 'two', 'three', 'four'])

    def test_boolean_overrides(self):
        """
        Override with boolean values
        """

        self.check_override({'bool': False}, {})
        self.check_override({}, {'bool': False}, {'bool': False})
        self.check_override({'bool': True}, {})
        self.check_override({}, {'bool': True}, {'bool': True})
        self.check_override({'bool': True}, {'bool': False}, {'bool': False})
        self.check_override({'bool': False}, {'bool': True}, {'bool': True})

    def test_special_overrides(self):
        """
        Override with special values ('', None, ...)
        """

        self.check_override({'key': ''}, {})
        self.check_override({'key': None}, {})
        self.check_override({}, {'key': ''}, {'key': ''})
        self.check_override({}, {'key': None}, {'key': None})

    def check_override(self, default, override, expected=None):

        merged = merge(default, override)

        self.assertEqual(merged, expected or default)
