#!/usr/bin/env python
import unittest

from garlicconfig.fields import ConfigField, StringField, BooleanField, IntegerField, ArrayField
from garlicconfig.fields.model import ModelField
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

        with self.assertRaises(TypeError):
            testfield = IntegerField(range='peyman')

        testfield = IntegerField(domain=(1, 100))
        testfield.validate(1)  # inclusive lower bound
        testfield.validate(50)
        testfield.validate(100)  # inclusive upper bound

        with self.assertRaises(ValidationError):
            testfield.validate(-1)

        with self.assertRaises(ValidationError):
            testfield.validate(101)

    def test_model(self):
        class Test(ConfigModel):
            name = StringField()

        class WrongConfigModel(ConfigModel):
            name = IntegerField()

        class BadClass(object):
            name = StringField()

        with self.assertRaises(ValueError):
            testfield = ModelField(model_class=str)

        with self.assertRaises(ValueError):
            testfield = ModelField(model_class=BadClass)

        with self.assertRaises(TypeError):
            testfield = ModelField(model_class=BadClass())

        testfield = ModelField(model_class=Test)
        testfield.validate(Test())
        with self.assertRaises(ValidationError):
            testfield.validate(WrongConfigModel())

        testmodel = testfield.to_model_value({'name': 'Mark Rothko'})
        self.assertEqual(testmodel.name, 'Mark Rothko')
        testmodel = testfield.to_model_value({})
        testmodel = testfield.to_model_value(None)
        self.assertEqual(testfield.to_dict_value(None, False), None)
        self.assertEqual(testfield.to_dict_value(testmodel, False), None)

    def test_array(self):
        class Test(ConfigModel):
            age = IntegerField()

        testfield = ArrayField(field=ModelField(model_class=Test), default=[])
        testfield.validate([])
        with self.assertRaises(ValidationError):
            testfield.validate([1, 2, 3])
        with self.assertRaises(ValidationError):
            testfield.validate(['1', '2'])
        testfield.validate([Test(), Test()])

        testmodel = testfield.to_model_value([{'age': 1}, {'age': 2}])
        self.assertEqual(testmodel[0].age, 1)
        self.assertEqual(testmodel[1].age, 2)
        with self.assertRaises(ValidationError):
            testmodel = testfield.to_model_value('peyman')


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

        with self.assertRaises(ValidationError):
            test = self.ChildModel.load_dict({  # should raise ValidationError because age and working are not provided.
                'occupation': 'peyman'
            })

    def test_model_field(self):
        class BigConfig(ConfigModel):
            info = ModelField(model_class=self.ChildModel)

        test = BigConfig()
        test.info.name = 'Ms. Butterhead'
        test.info.working = False
        self.assertEqual(test.get_dict(), {
            'info': {
                'age': 21,
                'working': False,
                'name': 'Ms. Butterhead'
            }
        })

        test = BigConfig.load_dict({
            'info': {
                'age': 21,
                'working': False,
                'name': 'Ms. Butterhead'
            }
        })
        self.assertEqual(test.info.age, 21)
        self.assertEqual(test.info.working, False)
        self.assertEqual(test.info.name, 'Ms. Butterhead')
        self.assertEqual(test.info.occupation, None)

        with self.assertRaises(ValidationError):
            test = BigConfig.load_dict({
                'info': {
                    'age': '21',  # make sure we properly raise ValidationError
                    'working': False,
                    'name': 'Ms. Butterhead'
                }
            })


if __name__ == '__main__':
    unittest.main()