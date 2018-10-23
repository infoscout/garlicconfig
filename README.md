[![CircleCI](https://circleci.com/gh/infoscout/garlicconfig.svg?style=svg&circle-token=cfc59c65adb4fae414d1665d74d8b520a6326444)](https://circleci.com/gh/infoscout/garlicconfig)
[![codecov](https://codecov.io/gh/infoscout/garlicconfig/branch/master/graph/badge.svg?token=5uJ3VXkNJl)](https://codecov.io/gh/infoscout/garlicconfig)

# GarlicConfig

GarlicConfig is a framework that makes it easy to deal with configurations in an easy yet flexible way. The core of this package is written in C++ and this Python package wraps the native code to provide an easy access to the configuration and some extra feature on top of it. The native library allows for quick retrieval of the configurations which can be used on any platform, this wrapper, however allows for defining advanced validation and config retrieval logic. For example, you could define your own conventions for getting localized version of configs.

The whole thing starts by defining the structure of your configs using models.

You can define models by inheriting from `ConfigModel`:

```python
from garlicconfig import models

class DatabaseConfig(models.ConfigModel):
    pass
```

By adding attributes (or properties), you can define what this model recognizes and what format should each one of these attributes have.

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
        
    def to_garlic_value(self, value):
        return str(value)
```

The field class above stores `str` in the python dictionary representation. However, for the materialized config model, `int` is used. It also invalidates unaccepted values by raising `ValidationError`, in this case odd values.

Note that `to_model_value` is responsible for converting a basic type to a more complicated python type, perhaps constructing a Python-defined class.

`to_garlic_value` does the exact opposite, it should convert the value to a basic value. Basic value is defined to be one of the following types:

* **str**
* **int**
* **float**
* **dict**
* **set** & **list**

This is primarily used for ease of encoding/decoding. By default, both of these methods return the given `value` without making any changes and I'd recommend not creating very complicated objects since it'll limit the accessibility of them in different platforms should you need to support them.

Next, you can define your own config model and use the custom `ConfigField` we just created.

for example:

```python
class SomeRandomConfig(ConfigModel):

	value = EvenIntegerField(nullable=False, default=2)
```

You can use `py_value` method on config models to get a python dictionary with basic value types in it. This is handy to cache it in memory, or to use it for serialization.

`from_dict` will create a new config model from a python dictionary.

Furthermore, you can use `garlic_value` to construct a `GarlicValue` from the current config model and use `from_garlic` to construct a model from a `GarlicValue`.

`GarlicValue` is a type that keeps configuration objects in the native code and loads them in Python lazily. This allows you to lower memory usage while speeding up all operations. It also comes with a set of handy methods:

### resolve
Allows for requested a specific value by providing a dot separated path.

for example:

```python
class ParentConfig(models.ConfigModel):
    
    random_config_field = models.ModelField(SomeRandomConfig)


foo = ParentConfig()
foo.random_config_field.value = 8
garlic_value = foo.garlic_value()
print(garlic_value.resolve('random_config_field.value'))
```
In the above code, if value to the given path exists, the python representation of the value gets returned. Otherwise, `None` gets returned. This is helpful because you can simply give the path to the final value and get the requested value. Since all of this is happening in the native code, it's significantly faster to use `GarlicValue` over python dictionary or regular models.

Your goal should be to validate models using `ConfigModel` and store/read configurations using `GarlicValue`.

### clone
Copy operations, specially deep copies in Python are very expensive. You can, however, clone `GarlicValue` instances much faster by using the native clone which copies the object without the need to use deep copy yet accomplish the same result.

for example:

```python
garlic_value_1 = foo.garlic_value()
garlic_value_2 = foo.clone()
```

# Serialization

You can use the following code to encode/decode configs. The default encoder is Json. However, you can write your own encoder and support other formats as needed.

```python
from garlicconfig import encoding

config = DatabaseConfig()
serialized_string = encoding.encode(config, pretty=True)
```


# Merging layers

You merge two configuration layers in order to support inheritance. Something that will come very handy if you plan to use localization or multi-layered configurations.

Any `GarlicValue` instance will have a `apply` method that will basically applies a second `GarlicValue` on top of itself.

for example:

```python
from garlicconfig import models
from garlicconfig import fields


class ExtraConfig(models.ConfigModel):

    has_id = fields.BooleanField(default=False)
    has_degree = fields.BooleanField(default=False)


class DumbConfig(models.ConfigModel):

    name = fields.StringField(nullable=False)
    numbers = fields.ArrayField(IntegerField())
    extra = models.ModelField(ExtraConfig)
    
    def validate(self):
        super(DumbConfig, self).validate()
        if not self.name and not self.numbers:
            raise garlicconfig.exceptions.ValidationError('invalid config for some reason!')


config_1 = DumbConfig.from_dict({
    'name': 'Peyman',
    'numbers': [1, 2, 3]
    'extra': {
        'has_id': True
    }
}).garlic_value()

config_2 = DumbConfig.from_dict({
    'name': 'Patrick',
    'numbers': [4, 5, 6]
    'extra': {
        'has_degree': True
    }
}).garlic_value()

config_1.apply(config_2)
config_1.resolve('numbers')  # returns [4, 5, 6]
config_1.resolve('name')  # returns 'Patrick'
config_1.resolve('extra.has_id')  # returns True (from config_1)
config_1.resolve('extra.has_degree')  # returns True (from config_2)
```