# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

from garlicconfig.exceptions import ValidationError
from garlicconfig.fields import ConfigField

import six


class ModelMetaInfo(object):

    def __init__(self):
        self.fields = {}  # map name to fields


class ModelMetaClass(type):

    def __new__(mcs, name, bases, attributes):
        new_class = super(ModelMetaClass, mcs).__new__(mcs, str(name), bases, attributes)
        meta = ModelMetaInfo()
        for key in attributes:
            field = attributes[key]
            if isinstance(attributes[key], ConfigField):
                # if a friendly name is provided, skip this step.
                if not field.friendly_name:
                    field.friendly_name = key
                meta.fields[key] = field
                delattr(new_class, key)
        for base in bases:
            if isinstance(base, ModelMetaClass):
                meta.fields.update(base.__meta__.fields)
        setattr(new_class, '__meta__', meta)
        return new_class


@six.add_metaclass(ModelMetaClass)
class ConfigModel(object):

    def __init__(self):
        for field_name in self.__meta__.fields:
            setattr(self, field_name, copy.deepcopy(self.__meta__.fields[field_name].default))

    @classmethod
    def load_dict(cls, obj):
        """
        Instantiate a config model and load it using the given dictionary.
        """
        new_instance = cls()
        for field_name in cls.__meta__.fields:
            field = cls.__meta__.fields[field_name]
            if obj and field_name in obj:
                value = field.to_model_value(obj[field_name])
                setattr(new_instance, field_name, value)
            elif not field.nullable:
                raise ValidationError("Value for '{key}' cannot be null.".format(key=field_name))
        return new_instance

    @classmethod
    def get_model_desc_dict(cls):
        """
        Returns a python dictionary containing description for the current model and its children.
        """
        obj = {}
        for field_name in cls.__meta__.fields:
            field = cls.__meta__.fields[field_name]
            obj[field_name] = field.get_field_desc_dict()
        return obj

    def get_dict(self):
        """
        Returns a python dictionary containing only basic types so it can be used for encoding.
        """
        obj = {}
        for field_name in self.__meta__.fields:
            model_value = getattr(self, field_name)
            dict_value = self.__meta__.fields[field_name].to_dict_value(model_value)
            if dict_value is None:
                continue
            obj[field_name] = dict_value
        return obj

    def __setattr__(self, name, value):
        if name in self.__meta__.fields:
            self.__meta__.fields[name].__validate__(value)
        super(ConfigModel, self).__setattr__(name, value)
