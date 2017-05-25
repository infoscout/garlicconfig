#!/usr/bin/env python
import unittest

from garlicconfig.fields import ConfigField, StringField, BooleanField, IntegerField
from garlicconfig.models import ConfigModel
from garlicconfig.exceptions import ValidationError


class TestConfigFields(unittest.TestCase):

    def test_base(self):
        """
        Test ConfigField to make sure it behaves correctly.
        This is the only place we should test __validate__, other tests should use Model.validate instead.
        """
        testfield = ConfigField()
        self.assertEqual(testfield.default, None)
        self.assertEqual(testfield.nullable, True)

        testfield = ConfigField(default=25, nullable=False)  # should not raise
        testfield = ConfigField(default=None, nullable=True)  # should not raise
        with self.assertRaises(ValidationError):
            testfield = ConfigField(default=None, nullable=False)  # can't set an invalid default value.

        # to make sure field's validate gets called properly
        class SomeField(ConfigField):
            def validate(self, value):
                if value != 25:
                    raise ValueError()

        testfield = SomeField(default=None, nullable=True)  # shouldn't raise cause it's null and it's permitted.
        testfield.__validate__(None)  # shouldn't raise because of the same reason
        testfield.__validate__(25)  # shouldn't raise because SomeFields's validate method doesn't raise.
        with self.assertRaises(ValueError):
            testfield.__validate__(20)  # bad value; should raise because SomeField's validate method raises Exception

        with self.assertRaises(ValueError):
            testfield.__validate__(24)  # bad default value; should raise

        testfield = SomeField(default=25, nullable=False)  # shouldn't raise

    def test_string(self):
        # test null and default
        testfield = StringField(default=None, nullable=True)
        testfield.validate('test string')  # make sure it doesn't raise

        with self.assertRaises(ValidationError):
            testfield = StringField(default=None, nullable=False)

        with self.assertRaises(ValidationError):
            testfield = StringField(default=25, nullable=False)

        with self.assertRaises(TypeError):
            testfield = StringField(default=None, nullable=False, choices='peyman,sth')  # invalid choices

        testfield = StringField(default='value1', nullable=False, choices=('value1', 'value2',))
        with self.assertRaises(ValidationError):
            testfield.validate('something')
        testfield.validate('value2')

    def test_bool(self):
        testfield = BooleanField(default=False, nullable=False)
        with self.assertRaises(ValidationError):
            testfield.validate('some random string')
        testfield.validate(True)

    def test_int(self):
        testfield = IntegerField(default=0, nullable=False)  # make sure we don't confuse 0 with None
        testfield.validate(-1)
        with self.assertRaises(ValidationError):
            testfield.validate('Rick Sanchez')


class TestConfigModel(unittest.TestCase):

    class ParentModel(ConfigModel):
        name = StringField()
        age = IntegerField(nullable=False, default=21)

    class ChildModel(ParentModel):
        working = BooleanField(default=True, nullable=False)
        occupation = StringField()

    def test_inheritance(self):
        self.assertEqual(set(self.ParentModel.__meta__.fields), set(['age', 'name']))
        self.assertEqual(set(self.ChildModel.__meta__.fields), set(['age', 'name', 'working', 'occupation']))

        # test with an instance
        test = self.ChildModel()
        test.age = 12
        test.occupation = 'zombie trainer'
        self.assertEqual(test.get_dict(), {'age': 12, 'occupation': 'zombie trainer', 'working': True})

    def test_get_and_load(self):
        test = self.ChildModel()
        test.age = 12
        self.assertEqual(test.get_dict(), {'age': 12, 'working': True})
        self.assertEqual(
            test.get_dict(include_null_values=True),
            {'age': 12, 'working': True, 'name': None, 'occupation': None}
        )

        test = self.ChildModel.load_dict(
            {
                'name': 'Jack Skellington',
                'age': 24,
                'working': False,
                'occupation': 'Head of Halloween Department'
            }
        )

        self.assertEqual(test.age, 24)
        self.assertEqual(test.working, False)
        self.assertEqual(test.occupation, 'Head of Halloween Department')
        self.assertEqual(test.name, 'Jack Skellington')

        with self.assertRaises(ValidationError):
            test = self.ChildModel.load_dict(
                {
                    'age': '25'
                }
            )


if __name__ == '__main__':
    unittest.main()
