from garlicconfig.fields import ConfigField


class ModelMetaInfo(object):
    def __init__(self):
        self.fields = {}  # map name to fields


class ModelMetaClass(type):

    def __new__(cls, name, bases, attributes):
        new_class = super(ModelMetaClass, cls).__new__(cls, str(name), bases, attributes)
        meta = ModelMetaInfo()
        for key in attributes:
            field = attributes[key]
            if isinstance(attributes[key], ConfigField):
                field.name = key
                meta.fields[key] = field
                setattr(new_class, key, field.default)
        for base in bases:
            if isinstance(base, ModelMetaClass):
                pass
                meta.fields.update(base.__meta__.fields)
        setattr(new_class, '__meta__', meta)
        return new_class


class ConfigModel(object):

    __metaclass__ = ModelMetaClass

    @classmethod
    def load_dict(cls, obj):
        new_instance = cls()
        if not obj:
            return new_instance
        for key in obj:
            if key in cls.__meta__.fields:
                value = cls.__meta__.fields[key].to_model_value(obj[key])
                setattr(new_instance, key, value)
        return new_instance

    def get_dict(self, include_null_values=False):
        obj = {}
        for field_name in self.__meta__.fields:
            value = getattr(self, field_name)
            if value is None and not include_null_values:
                continue
            obj[field_name] = self.__meta__.fields[field_name].to_dict_value(value, include_null_values)
        return obj

    def __setattr__(self, name, value):
        if name in self.__meta__.fields:
            self.__meta__.fields[name].__validate__(value)
        super(ConfigModel, self).__setattr__(name, value)
