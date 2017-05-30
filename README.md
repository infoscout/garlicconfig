[![CircleCI](https://circleci.com/gh/infoscout/garlicconfig.svg?style=svg&circle-token=cfc59c65adb4fae414d1665d74d8b520a6326444)](https://circleci.com/gh/infoscout/garlicconfig)
[![codecov](https://codecov.io/gh/infoscout/garlicconfig/branch/master/graph/badge.svg?token=5uJ3VXkNJl)](https://codecov.io/gh/infoscout/garlicconfig)

# GarlicConfig

GarlicConfig is a framework that makes it easy to write complex configurations with ability to validate them easily.

You can define models by inheriting from `ConfigModel`:

```python
from garlicconfig import models

class DatabaseConfig(models.ConfigModel):
    pass
```

For properties, you can use `ConfigField`. There are a set of built-in fields:

* StringField
* IntegerField
* ArrayField
* ModelField
* BooleanField


You can also make your own custom `ConfigModel` and/or `ConfigField`.

for example:

```python
from garlicconfig import fields
from garlicconfig.exceptions import ValidationError

class EvenIntegerField(IntegerField):
    def validate(self, value):
        if value % 2 != 0:
            raise ValidationError('bad integer')
    
    def to_model_value(self, value):
        return int(value)
        
    def to_dict_value(self, value):
        return str(value)
```

This field will use string in the saved python dictionary. However, for the materialized config model, it'll use integer. We're also raising an exception when a given value is not accepted.

for example:

```python
class SomeRandomConfig(ConfigModel):
	value = EvenIntegerField(nullable=False, default=2)
```

You can use `get_dict` method on config models to get a python dictionary with basic value types in it. This is handy to cache it in memory, or to use it for serialization.

`load_dict` will create a new config model from a python dictionary.


# Serialization

You can use the following code to encode/decode configs. The default encoder is Json. However, you can write your own encoder and support other formats as needed.

```python
from garlicconfig import encoder

config = DatabaseConfig()
serialized_string = encoder.encode(config, pretty=True)

# You must provide the config class.
config = encoder.decode(serialized_string, DatabaseConfig)
```


# Merging layers

You merge two configuration layers in order to support inheritance. Python `dict` will get merged but other values will be overridden.

for example:

```python
from garlicconfig.utils import merge

config_dict1 = {
    'name': 'Peyman',
    'numbers': [1, 2, 3]
    'extra': {
        'has_id': True
    }
}

config_dict2 = {
    'name': 'Patrick',
    'numbers': [4, 5, 6]
    'extra': {
        'has_degree': True
    }
}

# this will create a copy of base including config_dict2's data
merge(base=config_dict1, config=config_dict2)

# that will give you the following object.
{
    'name': 'Patrick',
    'numbers': [4, 5, 6],
    'extra': {
        'has_degree': True,
        'has_id': True
    }
}
```
