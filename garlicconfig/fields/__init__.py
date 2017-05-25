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
        self.validate(default)
        self._value = default
        self.desc = desc

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.validate(value)
        self._value = value

    def validate(self, value):
        if value is None and not self.nullable:
            raise ValidationError('Value is not allowed to be null.')
