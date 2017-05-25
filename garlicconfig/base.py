from garlicconfig.fields import ConfigField


class ConfigurationModelMeta(type):

    def __new__(cls, name, bases, attributes):
        model_fields = ()
        sub_models = ()
        for key in attributes:
            if isinstance(attributes[key], ConfigField):
                model_fields += (key,)
            elif isinstance(type(attributes[key]), ConfigurationModelMeta):
                sub_models += (key,)
        for base in bases:
            if isinstance(base, ConfigurationModelMeta):
                model_fields += getattr(base, '__modelfields__')
        new_class = super(ConfigurationModelMeta, cls).__new__(cls, str(name), bases, attributes)
        setattr(new_class, '__modelfields__', model_fields)
        setattr(new_class, '__submodels__', sub_models)
        return new_class


class ConfigurationModel(object):

    __metaclass__ = ConfigurationModelMeta

    @classmethod
    def load_dict(cls, obj):
        new_instance = cls()
        if not obj:
            return new_instance

        for key in obj:
            if key in cls.__modelfields__:
                setattr(new_instance, key, obj[key])
            elif key in cls.__submodels__:
                getattr(new_instance, key).load_dict(obj[key])
        return new_instance

    def get_dict(self):
        obj = {}
        for field in self.__modelfields__:
            value = getattr(self, field).value
            if value is not None:
                obj[field] = value
        for field in self.__submodels__:
            value = getattr(self, field).get_dict()
            if value is not None:
                obj[field] = value
        return obj if len(obj) > 0 else None

    def __setattr__(self, name, value):
        if name in self.__modelfields__:
            getattr(self, name).value = value
        else:
            super(ConfigurationModel, self).__setattr__(name, value)

    def __getattr__(self, name):
        if name in self.__modelfields__:
            return getattr(self, name).value
        else:
            super(ConfigurationModel, self).__getattribute__(name)
