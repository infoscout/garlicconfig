# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from garlicconfig.exceptions import ValidationError


def assert_value_type(value, expected_type, name):
    if not isinstance(value, expected_type):
        raise ValidationError(
            "Expected '{expected}' for '{key}', but got '{got}'.".format(
                expected=expected_type.__name__,
                key=name,
                got=type(value).__name__
            )
        )
