import json
from abc import ABCMeta, abstractmethod

from garlicconfig.models import ConfigModel


class ConfigEncoder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def encode(self, config, pretty=True):
        pass

    @abstractmethod
    def decode(self, data, config_class):
        pass


class PrettyJSONEncoder(json.JSONEncoder):
    """
    This encoder is not the most efficient at all, but it produces a pretty json format. It solves the problem with
    long arrays. Default encoder puts every single element on a separate line but this encoder does a smart job.
    """
    def __init__(self, *args, **kwargs):
        super(PrettyJSONEncoder, self).__init__(*args, **kwargs)
        self.current_indent = 0
        self.current_indent_str = ''

    def __has_non_primitive(self, obj):
        # since this is a private func, it's safe to assume obj is an iterable.
        for item in obj:
            if isinstance(item, (list, tuple, dict)):
                return True
        return False

    def encode(self, obj):
        if isinstance(obj, (list, tuple)):
            primitives_only = not self.__has_non_primitive(obj)
            output = []
            if primitives_only:
                for item in obj:
                    output.append(super(PrettyJSONEncoder, self).encode(item))
                return '[' + ', '.join(output) + ']'
            else:
                self.current_indent += self.indent
                self.current_indent_str = ''.join([' ' for x in range(self.current_indent)])
                for item in obj:
                    output.append(self.current_indent_str + self.encode(item))
                self.current_indent -= self.indent
                self.current_indent_str = ''.join([' ' for x in range(self.current_indent)])
                return '[\n' + ',\n'.join(output) + '\n' + self.current_indent_str + ']'
        elif isinstance(obj, dict):
            output = []
            self.current_indent += self.indent
            self.current_indent_str = ''.join([' ' for x in range(self.current_indent)])
            for key in sorted(obj):
                value = obj[key]
                output.append(
                    self.current_indent_str + super(PrettyJSONEncoder, self).encode(key) + ': ' + self.encode(value)
                )
            self.current_indent -= self.indent
            self.current_indent_str = "".join([" " for x in range(self.current_indent)])
            return '{\n' + ',\n'.join(output) + '\n' + self.current_indent_str + '}'
        else:
            return super(PrettyJSONEncoder, self).encode(obj)


class JsonEncoder(ConfigEncoder):
    @staticmethod
    def json_loads_byteified(json_text):
        return JsonEncoder.__byteify(
            json.loads(json_text, object_hook=JsonEncoder.__byteify),
            ignore_dicts=True
        )

    @staticmethod
    def __byteify(data, ignore_dicts=False):
        # if this is a unicode string, return its string representation
        if isinstance(data, unicode):
            return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [JsonEncoder.__byteify(item, ignore_dicts=True) for item in data]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            return {
                JsonEncoder.__byteify(key, ignore_dicts=True): JsonEncoder.__byteify(value, ignore_dicts=True)
                for key, value in data.iteritems()
            }
        # if it's anything else, return it in its original form
        return data

    def encode(self, config, pretty=True):
        if not isinstance(config, ConfigModel):
            raise TypeError("'config' must be a ConfigModel.")
        if pretty:
            return json.dumps(config.get_dict(), sort_keys=True, indent=2, cls=PrettyJSONEncoder)
        else:
            return json.dumps(config.get_dict(), sort_keys=True, separators=(',', ':'))

    def decode(self, data, config_class):
        if not issubclass(config_class, ConfigModel):
            raise TypeError("'config_class' must be a ConfigModel.")
        data_dict = JsonEncoder.json_loads_byteified(data)
        return config_class.load_dict(data_dict)


def encode(config, cls=None, pretty=True):
    cls = cls or JsonEncoder  # default to json
    if not issubclass(cls, ConfigEncoder):
        raise TypeError("'cls' must be a ConfigEncoder")
    return cls().encode(config, pretty)


def decode(data, config_class, cls=None):
    cls = cls or JsonEncoder
    if not issubclass(cls, ConfigEncoder):
        raise TypeError("'cls' must be a ConfigEncoder")
    return cls().decode(data, config_class)
