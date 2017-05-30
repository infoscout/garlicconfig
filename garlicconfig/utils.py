import copy
from garlicconfig.exceptions import ValidationError


def assert_value_type(value, expected_type, name):
    if not isinstance(value, expected_type):
        raise ValidationError(
            "Expected '{expected}' for '{key}', but got '{got}'.".format(
                expected=type.__name__,
                key=name,
                got=type(value).__name__
            )
        )


def __merge(base, config):
    for key in config:
        if isinstance(config[key], dict):
            if key in base:
                __merge(base[key], config[key])
            else:
                base[key] = config[key]
        else:
            base[key] = config[key]
    return base


def merge(base, config):
    """
    Merge two configuratons.

    Parameters:
        base: dict representation of the configuration.
        config: the configuration that will override base config.
    """
    assert_value_type(base, dict, 'base')
    assert_value_type(config, dict, 'config')
    return __merge(copy.deepcopy(base), config)