from garlicconfig.exceptions import ValidationError


class ConfigField(object):

    def __init__(self, default=None, nullable=True, desc=None):
        """
        Base configuration model, holds most basic data about a field.

        Parameters:
            default : the default value, note that it still has to pass all the validation tests.
            nullable (bool) : determines whether this field is permitted to have to no value at all.
            desc (str) : a short description of what this field is.
        """
        self.nullable = nullable
        self.default = default
        self.__validate(default)
        self._value = default
        self.desc = desc

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.__validate(value)
        self._value = value

    def __validate(self, value):
        if value is None and not self.nullable:
            raise ValidationError("Value is not allowed to be null.")
        elif value is not None:
            self.validate(value)

    def validate(self, value):
        pass


class StringField(ConfigField):

    def __init__(self, default=None, nullable=True, desc=None, choices=None):
        if choices and not hasattr(choices, '__iter__'):
            raise TypeError("'choices' has to be a sequence of string elements.")
        self.choices = choices
        super(StringField, self).__init__(default, nullable, desc)

    def validate(self, value):
        super(StringField, self).validate(value)
        if not isinstance(value, str):
            raise ValidationError("Value must be of type 'str'")
        elif self.choices and value not in self.choices:
            raise ValidationError("Given value '{given}' is not accepted. Choices are '{choices}'".format(
                given=value,
                choices="', '".join(self.choices)
            ))
