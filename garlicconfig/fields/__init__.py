from garlicconfig.exceptions import ValidationError


def assert_value_type(value, type, name):
    if not isinstance(value, type):
        raise ValidationError("Value for '{key}' must be of type '{type}'".format(type=type.__name__, key=name))


class ConfigField(object):
    def __init__(self, default=None, nullable=True, desc=None):
        """
        Base configuration model, holds most basic data about a field.

        Parameters:
            default : the default value, note that it still has to pass all the validation tests.
            nullable (bool) : determines whether this field is permitted to have to no value at all.
            desc (str) : a short description of what this field is.
        """
        self.name = type(self).__name__  # optional friendly name for this field. defaults to the field type's name
        self.nullable = nullable
        self.__validate__(default)  # make sure default value is valid
        self.default = default
        self.desc = desc

    def __validate__(self, value):
        """
        Low level method for validation. Do not use this method outside of this package, it's prone to change
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

    def to_dict_value(self, value, include_null_values):
        """
        Given a model value, return a basic value type to be stored in a python dictionary.
        Note that this value must only hold basic types: list of integers is acceptable but a custom class is not.
        """
        return value


class StringField(ConfigField):
    def __init__(self, default=None, nullable=True, desc=None, choices=None):
        if choices and not hasattr(choices, '__iter__'):
            raise TypeError("'choices' has to be a sequence of string elements.")
        self.choices = choices
        super(StringField, self).__init__(default, nullable, desc)

    def validate(self, value):
        super(StringField, self).validate(value)
        assert_value_type(value, str, self.name)
        if self.choices and value not in self.choices:
            raise ValidationError("Value '{given}' for '{key}' is not accepted. Choices are '{choices}'".format(
                given=value,
                key=self.name,
                choices="', '".join(self.choices)
            ))


class BooleanField(ConfigField):
    def validate(self, value):
        super(BooleanField, self).validate(value)
        assert_value_type(value, bool, self.name)


class IntegerField(ConfigField):
    def validate(self, value):
        super(IntegerField, self).validate(value)
        assert_value_type(value, int, self.name)


class ArrayField(ConfigField):
    def __init__(self, field, default=None, nullable=True, desc=None):
        if not isinstance(field, ConfigField):
            raise TypeError("'field' has to be a ConfigField.")
        self.field = field
        super(ArrayField, self).__init__(default, nullable, desc)

    def validate(self, value):
        super(ArrayField, self).validate(value)
        assert_value_type(value, list, self.name)
        for item in value:
            self.field.validate(item)

    def to_model_value(self, value):
        return map(lambda x: self.field.to_model_value(x), value)

    def to_dict_value(self, value, include_null_values):
        return map(lambda x: self.field.to_dict_value(x, include_null_values), value)
