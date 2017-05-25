#!/usr/bin/env python
import unittest

from garlicconfig.fields import ConfigField
from garlicconfig.exceptions import ValidationError


class TestConfigFields(unittest.TestCase):

    def test_nullable(self):
        # ConfigField
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


if __name__ == '__main__':
    unittest.main()
