#!/usr/bin/env python
import unittest

from garlicconfig.fields import ConfigField, StringField, BooleanField
from garlicconfig.exceptions import ValidationError


class TestConfigFields(unittest.TestCase):

    def test_base(self):
        testfield = ConfigField()
        self.assertEqual(testfield.default, None)
        self.assertEqual(testfield.nullable, True)
        testfield.validate(24)  # should not raise
        testfield.value = 24
        self.assertEqual(testfield.value, 24)
        testfield.validate('something')  # should not raise
        testfield.value = 'something'
        self.assertEqual(testfield.value, 'something')
        testfield.validate(None)  # should not raise
        testfield.value = None
        self.assertEqual(testfield.value, None)

        testfield = ConfigField(default=25, nullable=False)
        with self.assertRaises(ValidationError):
            testfield.value = None

        with self.assertRaises(ValidationError):
            testfield = ConfigField(default=None, nullable=False)  # can't set an invalid default value.

    def test_string(self):
        # test null and default
        testfield = StringField(default=None, nullable=True)
        self.assertEqual(testfield.value, None)
        testfield.value = None  # make sure it doesn't raise
        testfield.value = 'test string'
        self.assertEqual(testfield.value, 'test string')

        with self.assertRaises(TypeError):
            testfield = StringField(default=None, nullable=False, choices='peyman,sth')  # invalid choices

        testfield = StringField(default='value1', nullable=False, choices=('value1', 'value2',))
        with self.assertRaises(ValidationError):
            testfield.value = 'something'
        testfield.value = 'value2'
        self.assertEqual(testfield.value, 'value2')

    def test_bool(self):
        testfield = BooleanField(default=False, nullable=False)
        with self.assertRaises(ValidationError):
            testfield.value = None
        with self.assertRaises(ValidationError):
            testfield.value = 'some random string'
        testfield.value = True
        self.assertEqual(testfield.value, True)


if __name__ == '__main__':
    unittest.main()
