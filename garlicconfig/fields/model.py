# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from garlicconfig.exceptions import ValidationError
from garlicconfig.models import ConfigModel

from . import ConfigField, assert_value_type


class ModelField(ConfigField):

    def __init__(self, model_class, **kwargs):
        """
        A field that stores another config field as a subsection.
        :param model_class: Any class of type ConfigModel to store as a subsection.
        :type model_class: Type[ConfigModel]
        """
        if not isinstance(model_class, type):
            raise TypeError("'model_class' has to be a type.")
        if not issubclass(model_class, ConfigModel):
            raise ValueError("'model_class' has to implement ConfigModel")
        self.model_class = model_class
        instance = self.model_class()  # initialize an instance
        kwargs['default'] = instance
        super(ModelField, self).__init__(**kwargs)

    def validate(self, value):
        super(ModelField, self).validate(value)
        assert_value_type(value, self.model_class, self.name)

    def to_dict_value(self, value):
        dict_data = value.get_dict() if value else None
        return dict_data if dict_data else None  # if data is empty, return None

    def to_model_value(self, value):
        if not value:
            return self.model_class()  # initialize a new instance
        if not isinstance(value, dict):
            raise ValidationError("Value for {key} must be a python dict.".format(key=self.name))
        return self.model_class.load_dict(value)

    def __extra_desc__(self):
        return {
            'model_info': {
                'name': self.model_class.__name__,
                'fields': self.model_class.get_model_desc_dict(),
            }
        }
