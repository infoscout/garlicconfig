from . import ConfigField, assert_value_type
from garlicconfig.models import ConfigModel
from garlicconfig.exceptions import ValidationError


class ModelField(ConfigField):
    def __init__(self, model_class, nullable=True, desc=None):
        if not isinstance(model_class, type):
            raise TypeError("'model_class' has to be a type.")
        if not issubclass(model_class, ConfigModel):
            raise ValueError("'model_class' has to implement ConfigModel")
        self.model_class = model_class
        instance = self.model_class()  # initialize an instance
        super(ModelField, self).__init__(default=instance, nullable=nullable, desc=desc)

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