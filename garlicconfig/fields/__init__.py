# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from garlicconfig.exceptions import ValidationError
from garlicconfig.utils import assert_value_type

import six


class ConfigField(object):
    """
    Abstract class for all config fields.
    """

    __init_args = ('name', 'nullable', 'default', 'desc',)

    def __init__(self, **kwargs):
        """
        Base configuration model, holds most basic data about a field.

        Parameters:
            default : the default value, note that it still has to pass all the validation tests.
            nullable (bool) : determines whether this field is permitted to have to no value at all.
            desc (str) : a short description of what this field is.
        """
        self.friendly_name = kwargs.get('name')
        self.nullable = kwargs.get('nullable', True)
        self.default = kwargs.get('default')
        self.desc = kwargs.get('desc')
        self.__validate__(self.default)  # make sure default value is valid

        # it's nice to raise an exception when we get an unexpected argument so it's extra clear we're not handling it.
        unrecognized_args = [arg for arg in kwargs if arg not in self.__init_args]
        if unrecognized_args:
            raise TypeError("Argument '{arg_name}' is not recognized.".format(arg_name=unrecognized_args[0]))

    @property
    def name(self):
        """
        :return: str for the field's name.
        """
        return self.friendly_name or type(self).__name__

    def __validate__(self, value):
        """
        Low level method for validation. Do not use this method outside of this package, it's prone to change without
        further notice.
        """
        if value is None and not self.nullable:
            raise ValidationError("Value for '{key}' is not allowed to be null.".format(key=self.name))
        elif value is not None:
            self.validate(value)

    def validate(self, value):
        """
        Determines whether or not the given value is valid for the current field.

        Parameters:
            value : value is guaranteed to be non-null.
        """
        pass

    def to_model_value(self, value):
        """
        Given a value from a python dictionary, return the appropriate value to store in the model
        For example, if you have a custom class, you should use this method to initialize it.
        """
        return value

    def to_dict_value(self, value):
        """
        Given a model value, return a basic value type to be stored in a python dictionary.
        Note that this value must only hold basic types: list of integers is acceptable but a custom class is not.
        """
        return value

    def get_field_desc_dict(self):
        """
        Generate a dictionary describing the structure of this field.
        """
        extra_obj = self.__extra_desc__() or {}
        extra_obj.update({
            'nullable': self.nullable,
            'default': self.to_dict_value(self.default),
        })
        return {
            'name': self.name,
            'type': type(self).__name__,
            'desc': self.desc,
            'extra': extra_obj,
        }

    def __extra_desc__(self):
        """
        If there is any extra object this field needs to have, return it here.
        It'll be included in the 'extra' field returned in the field description dictionary.
        """
        pass


class StringField(ConfigField):

    def __init__(self, choices=None, **kwargs):
        """
        :param choices: If provided, value has to be one of these values.
        :type choices: iterator
        """
        if choices and not hasattr(choices, '__iter__'):
            raise TypeError("'choices' has to be a sequence of string elements.")
        self.choices = choices
        super(StringField, self).__init__(**kwargs)

    def validate(self, value):
        super(StringField, self).validate(value)
        assert_value_type(value, six.text_type, self.name)
        if self.choices and value not in self.choices:
            raise ValidationError("Value '{given}' for '{key}' is not accepted. Choices are '{choices}'".format(
                given=value,
                key=self.name,
                choices="', '".join(self.choices)
            ))

    def __extra_desc__(self):
        if self.choices:
            return {
                'choices': self.choices,
            }


class BooleanField(ConfigField):

    def validate(self, value):
        super(BooleanField, self).validate(value)
        assert_value_type(value, bool, self.name)


class IntegerField(ConfigField):

    def __init__(self, domain=None, **kwargs):
        """
        :param domain: Specify the domain of accepted values as (min, max,)
        :type domain: tuple
        """
        if domain and (not isinstance(domain, tuple) or len(domain) != 2):
            raise TypeError("'domain' has to be a tuple providing inclusive domain like: (min,max)")
        self.domain = domain
        super(IntegerField, self).__init__(**kwargs)

    def validate(self, value):
        super(IntegerField, self).validate(value)
        assert_value_type(value, int, self.name)
        if self.domain and not (self.domain[0] <= value <= self.domain[1]):
            raise ValidationError(
                "Value '{value}' for '{key}' has to be in range {domain}.".format(
                    value=value,
                    key=self.name,
                    domain=self.domain
                )
            )

    def __extra_desc__(self):
        if self.domain:
            return {
                'domain': self.domain,
            }


class ArrayField(ConfigField):

    def __init__(self, field, **kwargs):
        """
        Stores an array of ConfigField(s).
        :param field: An ConfigField instance describing the values in the list.
        :type field: ConfigField
        """
        if not isinstance(field, ConfigField):
            raise TypeError("'field' has to be a ConfigField.")
        self.field = field
        super(ArrayField, self).__init__(**kwargs)

    def validate(self, value):
        super(ArrayField, self).validate(value)
        assert_value_type(value, list, self.name)
        for item in value:
            self.field.validate(item)

    def to_model_value(self, value):
        return list(map(lambda x: self.field.to_model_value(x), value)) if value else None

    def to_dict_value(self, value):
        return list(map(lambda x: self.field.to_dict_value(x), value)) if value else None

    def __extra_desc__(self):
        return {
            'element_info': self.field.get_field_desc_dict()
        }
