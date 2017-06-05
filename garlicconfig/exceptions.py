"""
All garlic specific exceptions that can be raised.
"""


class ValidationError(Exception):
    """The provided value is not valid."""
    pass


class ConfigNotFound(Exception):
    """No configuration with such key name was found."""
    pass
