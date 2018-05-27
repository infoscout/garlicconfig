# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class ValidationError(Exception):
    """The provided value is not valid."""
    pass


class ConfigNotFound(Exception):
    """No configuration with such key name was found."""
    pass
