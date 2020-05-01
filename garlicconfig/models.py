import copy

from garlicconfig.exceptions import ValidationError
from garlicconfig.fields import ConfigField, validate_model_fields
from garlicconfig.layer import GarlicValue
from garlicconfig.utils import assert_value_type

import six


class ModelMetaInfo(object):

    def __init__(self):
        self.fields = {}


class ModelMetaClass(type):

    def __new__(mcs, name, bases, attributes):
        new_class = super(ModelMetaClass, mcs).__new__(mcs, str(name), bases, attributes)
        meta = ModelMetaInfo()
        for key in attributes:
            field = attributes[key]
            if isinstance(field, ConfigField):
                # if a friendly name is provided, skip this step.
                if not field.friendly_name:
                    field.friendly_name = key
                meta.fields[key] = field
                setattr(new_class, key, field.default)
        for base in bases:
            if isinstance(base, ModelMetaClass):
                meta.fields.update(base.__meta__.fields)
        new_class.__meta__ = meta
        return new_class


@six.add_metaclass(ModelMetaClass)
class ConfigModel(object):

    field_order = None  # Optional: how fields should be ordered when displayed

    def __init__(self):
        for field_name in self.__meta__.fields:
            value = getattr(self, field_name)
            if value is not None:
                setattr(self, field_name, copy.deepcopy(value))

    @classmethod
    def from_garlic(cls, garlic_value):
        """
        Instantiate a config model and load it using the given GarlicValue.
        """
        return cls.from_dict(garlic_value.py_value())

    @classmethod
    def from_dict(cls, value):
        """
        Instantiate a config model and load it using the given dict.
        """
        new_instance = cls()
        if value:
            for key, field in six.iteritems(cls.__meta__.fields):
                try:
                    setattr(new_instance, key, field.to_model_value(value[key]))
                except KeyError:
                    pass
        return new_instance

    @classmethod
    def get_model_desc_dict(cls):
        """
        Returns a python dictionary containing description for the current model and its children.
        """
        obj = {}
        for key, field in six.iteritems(cls.__meta__.fields):
            obj[key] = field.get_field_desc_dict()
        return obj

    @classmethod
    def resolve_field(cls, path):
        parts = path.split('.')
        current_field = None
        current_model = cls
        for part in parts:
            try:
                current_field = current_model.__meta__.fields[part]
                if isinstance(current_field, ModelField):
                    current_model = current_field.model_class
                else:
                    current_model = None
            except (AttributeError, KeyError):  # If __meta__ is not available or key doesn't exist, return None.
                return
        return current_field

    def garlic_value(self):
        """
        Returns an instance of GarlicValue representing this model.
        """
        return GarlicValue(self.py_value())

    def py_value(self):
        """
        Returns an instance of python dictionary containing only basic types so it can be used for encoding.
        """
        obj = {}
        for key, field in six.iteritems(self.__meta__.fields):
            dict_value = field.to_garlic_value(getattr(self, key))
            if dict_value is not None:
                obj[key] = dict_value
        return obj

    def validate(self):
        """
        Validates the current model.
        """
        validate_model_fields(self)


class ModelField(ConfigField):

    def __init__(self, model_class, **kwargs):
        """
        A field that stores another config field as a subsection.
        :param model_class: Any class of type ConfigModel to store as a subsection.
        :type model_class: Type[ConfigModel]
        """
        if not issubclass(model_class, ConfigModel):
            raise ValueError("'model_class' has to implement ConfigModel")
        self.model_class = model_class
        instance = self.model_class()  # initialize an instance
        kwargs['default'] = instance
        super(ModelField, self).__init__(**kwargs)

    def validate(self, value):
        super(ModelField, self).validate(value)
        assert_value_type(value, self.model_class, self.name)
        value.validate()

    def to_garlic_value(self, value):
        dict_data = value.py_value() if value else None
        return dict_data if dict_data else None  # if data is empty, return None

    def to_model_value(self, value):
        if not value:
            return self.model_class()  # initialize a new instance
        if not isinstance(value, dict):
            raise ValidationError("Value for {key} must be a python dict.".format(key=self.name))
        return self.model_class.from_dict(value)

    def __extra_desc__(self):
        name = self.model_class.__name__
        fields = self.model_class.get_model_desc_dict()
        field_order = self.model_class.field_order or list(fields)
        return {
            'model_info': {
                'name': name,
                'fields': fields,
                'field_order': field_order,
            }
        }
