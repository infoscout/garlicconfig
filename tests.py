#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import shutil
import unittest

from garlicconfig import encoder
from garlicconfig.exceptions import ConfigNotFound, ValidationError
from garlicconfig.fields import ArrayField, BooleanField, ConfigField, IntegerField, StringField
from garlicconfig.models import ConfigModel, ModelField
from garlicconfig.repositories import FileConfigRepository, MemoryConfigRepository


class TestConfigFields(unittest.TestCase):

    def test_base(self):
        """
        Test ConfigField to make sure it behaves correctly.
        This is the only place we should test __validate__, other tests should use Model.validate instead.
        """
        test_field = ConfigField()
        self.assertEqual(test_field.default, None)
        self.assertEqual(test_field.nullable, True)

        ConfigField(default=25, nullable=False)  # should not raise
        ConfigField(default=None, nullable=True)  # should not raise
        with self.assertRaises(ValidationError):
            ConfigField(default=None, nullable=False)  # can't set an invalid default value.

        # to make sure field's validate gets called properly
        class SomeField(ConfigField):
            def validate(self, value):
                if value != 25:
                    raise ValueError()

        test_field = SomeField(default=None, nullable=True)  # shouldn't raise cause it's null and it's permitted.
        test_field.__validate__(None)  # shouldn't raise because of the same reason
        test_field.__validate__(25)  # shouldn't raise because SomeFields's validate method doesn't raise.
        with self.assertRaises(ValueError):
            test_field.__validate__(20)  # bad value; should raise because SomeField's validate method raises Exception

        with self.assertRaises(ValueError):
            test_field.__validate__(24)  # bad default value; should raise

        SomeField(default=25, nullable=False)  # shouldn't raise

    def test_string(self):
        # test null and default
        test_field = StringField(default=None, nullable=True)
        test_field.validate('test string')  # make sure it doesn't raise

        with self.assertRaises(ValidationError):
            StringField(default=None, nullable=False)

        with self.assertRaises(ValidationError):
            StringField(default=25, nullable=False)

        with self.assertRaises(TypeError):
            StringField(default=None, nullable=False, choices=15)  # invalid choices

        test_field = StringField(default='value1', nullable=False, choices=('value1', 'value2',))
        with self.assertRaises(ValidationError):
            test_field.validate('something')
        test_field.validate('value2')

    def test_bool(self):
        test_field = BooleanField(default=False, nullable=False)
        with self.assertRaises(ValidationError):
            test_field.validate('some random string')
        test_field.validate(True)

    def test_int(self):
        test_field = IntegerField(default=0, nullable=False)  # make sure we don't confuse 0 with None
        test_field.validate(-1)
        with self.assertRaises(ValidationError):
            test_field.validate('Rick Sanchez')

        with self.assertRaises(TypeError):
            IntegerField(range='peyman')

        test_field = IntegerField(domain=(1, 100))
        test_field.validate(1)  # inclusive lower bound
        test_field.validate(50)
        test_field.validate(100)  # inclusive upper bound

        with self.assertRaises(ValidationError):
            test_field.validate(-1)

        with self.assertRaises(ValidationError):
            test_field.validate(101)

        with self.assertRaises(TypeError):
            IntegerField(domain=12)

    def test_model(self):
        class Test(ConfigModel):
            name = StringField()

        class WrongConfigModel(ConfigModel):
            name = IntegerField()

        class BadClass(object):
            name = StringField()

        with self.assertRaises(ValueError):
            ModelField(model_class=str)

        with self.assertRaises(ValueError):
            ModelField(model_class=BadClass)

        with self.assertRaises(TypeError):
            ModelField(model_class=BadClass())

        test_field = ModelField(model_class=Test)
        test_field.validate(Test())
        with self.assertRaises(ValidationError):
            test_field.validate(WrongConfigModel())

        test_model = test_field.to_model_value({'name': 'Mark Rothko'})
        self.assertEqual(test_model.name, 'Mark Rothko')
        test_field.to_model_value({})
        test_model = test_field.to_model_value(None)
        self.assertEqual(test_field.to_dict_value(None), None)
        self.assertEqual(test_field.to_dict_value(test_model), None)

    def test_array(self):
        class Test(ConfigModel):
            age = IntegerField()

        test_field = ArrayField(field=ModelField(model_class=Test), default=[])
        test_field.validate([])
        with self.assertRaises(TypeError):
            test_field = ArrayField(field='something')
        with self.assertRaises(ValidationError):
            test_field.validate([1, 2, 3])
        with self.assertRaises(ValidationError):
            test_field.validate(['1', '2'])
        test_field.validate([Test(), Test()])

        test_model = test_field.to_model_value([{'age': 1}, {'age': 2}])
        self.assertEqual(test_model[0].age, 1)
        self.assertEqual(test_model[1].age, 2)
        with self.assertRaises(ValidationError):
            test_field.to_model_value('peyman')

        test_field = ArrayField(field=StringField(choices=('a', 'b'), nullable=True))
        self.assertEqual(test_field.to_model_value(['a', 'b']), ['a', 'b'])
        self.assertEqual(test_field.to_model_value(('a', 'b')), ['a', 'b'])
        self.assertEqual(test_field.to_dict_value(['a', 'b']), ['a', 'b'])

        test_field = ArrayField(field=ModelField(model_class=Test))
        dict_value = test_field.to_dict_value([
            Test.load_dict({'age': 12}),
            Test.load_dict({'age': 13})
        ])
        self.assertEqual(dict_value, [{'age': 12}, {'age': 13}])


class TestConfigModel(unittest.TestCase):

    class ParentModel(ConfigModel):
        name = StringField()
        age = IntegerField(nullable=False, default=21)

    class ChildModel(ParentModel):
        working = BooleanField(default=True, nullable=False)
        occupation = StringField()

    class OptionalConfig(ConfigModel):
        name = StringField()

    def test_inheritance(self):
        self.assertEqual(set(self.ParentModel.__meta__.fields), {'age', 'name'})
        self.assertEqual(set(self.ChildModel.__meta__.fields), {'age', 'name', 'working', 'occupation'})

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

        # make sure we do instantiate a model object no matter what.
        self.assertEqual(self.OptionalConfig.load_dict(None).get_dict(), self.OptionalConfig().get_dict())

        with self.assertRaises(ValidationError):
            self.assertEqual(self.ChildModel.load_dict(None).get_dict(), self.ChildModel().get_dict())

        self.assertEqual(test.age, 24)
        self.assertEqual(test.working, False)
        self.assertEqual(test.occupation, 'Head of Halloween Department')
        self.assertEqual(test.name, 'Jack Skellington')

        with self.assertRaises(ValidationError):
            self.ChildModel.load_dict(
                {
                    'age': '25'
                }
            )

        with self.assertRaises(ValidationError):
            self.ChildModel.load_dict({  # should raise ValidationError because age and working are not provided.
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
            BigConfig.load_dict({
                'info': {
                    'age': '21',  # make sure we properly raise ValidationError
                    'working': False,
                    'name': 'Ms. Butterhead'
                }
            })

    def test_model_desc(self):
        class KidConfig(ConfigModel):
            name = StringField(name='First Name', nullable=False, default='Sam')

        class ParentConfig(ConfigModel):
            name = StringField(name='First Name', desc='Enter your first name', nullable=False, default='Peter')
            status = StringField(desc='Whats your status?', choices=('Good', 'Bad', 'Indifferent'))
            age = IntegerField(domain=(21, 150))
            nick_names = ArrayField(StringField(), name='Nick Names', nullable=False, default=['No Nick Name'])
            kids = ArrayField(ModelField(KidConfig))

        expected_end_result = {
            'name': {
                'type': 'StringField',
                'name': 'First Name',
                'desc': 'Enter your first name',
                'extra': {
                    'nullable': False,
                    'default': 'Peter',
                }
            },
            'status': {
                'type': 'StringField',
                'name': 'status',
                'desc': 'Whats your status?',
                'extra': {
                    'choices': ('Good', 'Bad', 'Indifferent',),
                    'nullable': True,
                    'default': None,
                }
            },
            'age': {
                'type': 'IntegerField',
                'name': 'age',
                'desc': None,
                'extra': {
                    'nullable': True,
                    'default': None,
                    'domain': (21, 150)
                }
            },
            'nick_names': {
                'type': 'ArrayField',
                'name': 'Nick Names',
                'desc': None,
                'extra': {
                    'nullable': False,
                    'default': ['No Nick Name'],
                    'element_info': {
                        'type': 'StringField',
                        'name': 'StringField',
                        'desc': None,
                        'extra': {
                            'nullable': True,
                            'default': None,
                        }
                    }
                }
            },
            'kids': {
                'type': 'ArrayField',
                'name': 'kids',
                'desc': None,
                'extra': {
                    'nullable': True,
                    'default': None,
                    'element_info': {
                        'type': 'ModelField',
                        'name': 'ModelField',
                        'desc': None,
                        'extra': {
                            'nullable': True,
                            'default': {
                                'name': 'Sam'
                            },
                            'model_info': {
                                'name': 'KidConfig',
                                'fields': {
                                    'name': {
                                        'type': 'StringField',
                                        'name': 'First Name',
                                        'desc': None,
                                        'extra': {
                                            'nullable': False,
                                            'default': 'Sam'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        expected_end_result_json = json.dumps(expected_end_result, sort_keys=True)
        actual_result_json = json.dumps(ParentConfig.get_model_desc_dict(), sort_keys=True)
        self.assertEqual(actual_result_json, expected_end_result_json)


class TestEncoder(unittest.TestCase):

    class Test(ConfigModel):
        name = StringField()
        age = IntegerField()
        numbers = ArrayField(IntegerField())
        matrix = ArrayField(ArrayField(IntegerField()))

    def test_json(self):
        # encode
        test = self.Test()
        test.name = 'Peyman'
        test.age = 21
        test.matrix = [[1, 2], [3, 4]]
        encoded_data = encoder.encode(test, pretty=False)
        self.assertEqual(encoded_data, '{"age":21,"matrix":[[1,2],[3,4]],"name":"Peyman"}')

        encoded_data = encoder.encode(test, pretty=True)
        self.assertEqual(
            encoded_data,
            '{\n  "age": 21,\n  "matrix": [\n    [1, 2],\n    [3, 4]\n  ],\n  "name": "Peyman"\n}'
        )

        with self.assertRaises(TypeError):
            encoder.encode('some random string')

        with self.assertRaises(TypeError):
            encoder.encode(test, cls=str)

        # decode
        with self.assertRaises(TypeError):
            encoder.decode('{"age":21,"name":"Peyman"}', self.Test, cls=str)

        test = encoder.decode('{"age":21,"name":"Peyman","numbers":[1,2,3,4]}', self.Test)
        self.assertEqual(test.age, 21)
        self.assertEqual(test.name, 'Peyman')
        self.assertEqual(test.numbers, [1, 2, 3, 4])

        with self.assertRaises(TypeError):
            encoder.decode('{}', str)


class TestMemoryConfigRepository(unittest.TestCase):

    def test_memory_repo(self):
        memory_repo = MemoryConfigRepository()
        self.assertEqual(list(memory_repo.all()), [])
        with self.assertRaises(ConfigNotFound):
            memory_repo.retrieve('something')

        memory_repo.save('config1', 'data')
        self.assertEqual(memory_repo.retrieve('config1'), 'data')


class TestFileConfigRepository(unittest.TestCase):

    TEST_DIR = 'testdata'

    def setUp(self):
        os.mkdir(self.TEST_DIR)

    def test_memory_repo(self):
        file_repo = FileConfigRepository(root_dir=self.TEST_DIR)
        self.assertEqual(list(file_repo.all()), [])
        with self.assertRaises(ConfigNotFound):
            file_repo.retrieve('something')

        file_repo.save('config1', 'data')
        self.assertEqual(file_repo.retrieve('config1'), 'data')

        with open(os.path.join(self.TEST_DIR, '.DS_Store'), 'w') as f:
            f.write('something')

        self.assertEqual(set(file_repo.all()), {'config1'})

    def tearDown(self):
        shutil.rmtree(self.TEST_DIR)


if __name__ == '__main__':
    unittest.main()
