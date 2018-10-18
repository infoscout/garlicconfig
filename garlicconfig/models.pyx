import copy

from cython.operator cimport dereference as deref
from libcpp.memory cimport shared_ptr
import six

from garlicconfig.exceptions import ValidationError
from garlicconfig.fields cimport ConfigField
from garlicconfig.layer cimport GarlicValue, ObjectValue, LayerValue
from garlicconfig.utils import assert_value_type


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
                setattr(new_class, key, copy.deepcopy(field.default) if field.default is not None else None)
        for base in bases:
            if isinstance(base, ModelMetaClass):
                meta.fields.update(base.__meta__.fields)
        new_class.__meta__ = meta
        return new_class


@six.add_metaclass(ModelMetaClass)
class ConfigModel(object):

    @classmethod
    def from_garlic(cls, GarlicValue garlic_value):
        """
        Instantiate a config model and load it using the given GarlicValue.
        """
        return cls.from_dict(garlic_value.py_value())

    @classmethod
    def from_dict(cls, dict value):
        """
        Instantiate a config model and load it using the given dict.
        """
        new_instance = cls()
        cdef str key
        cdef ConfigField field
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
        cdef dict obj = {}
        cdef str key
        cdef ConfigField field
        for key, field in six.iteritems(cls.__meta__.fields):
            obj[key] = field.get_field_desc_dict()
        return obj

    def garlic_value(self):
        """
        Returns an instance of GarlicValue representing this model.
        """
        cdef ObjectValue* obj = new ObjectValue()
        cdef str key
        cdef ConfigField field
        for key, field in six.iteritems(self.__meta__.fields):
            model_value = getattr(self, key)
            garlic_value = field.to_garlic_value(model_value)
            if garlic_value is not None:
                deref(obj).set(key, GarlicValue.init_layer_value(garlic_value))
        return GarlicValue.native_load(shared_ptr[LayerValue](obj))

    def py_value(self):
        """
        Returns an instance of python dictionary containing only basic types so it can be used for encoding.
        """
        cdef dict obj = {}
        for key, field in six.iteritems(self.__meta__.fields):
            dict_value = field.to_garlic_value(getattr(self, key))
            if dict_value is not None:
                obj[key] = dict_value
        return obj

    def validate(self):
        """
        Validates the current model.
        """
        cdef str key
        cdef ConfigField field
        for key, field in six.iteritems(self.__meta__.fields):
            field.native_validate(getattr(self, key), True)


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
        return {
            'model_info': {
                'name': self.model_class.__name__,
                'fields': self.model_class.get_model_desc_dict(),
            }
        }
