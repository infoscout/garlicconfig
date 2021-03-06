import json
from abc import ABCMeta, abstractmethod

from garlicconfig.models import ConfigModel

import six


cdef class Decoder(object):

    def __dealloc__(self):
        if self.native_decoder:
            del self.native_decoder


cdef class JsonDecoder(Decoder):

    def __init__(self):
        self.native_decoder = self.json_decoder = new NativeJsonDecoder()


@six.add_metaclass(ABCMeta)
class ConfigEncoder(object):

    @abstractmethod
    def encode(self, config, pretty=True):
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

    @staticmethod
    def __has_non_primitive(obj):
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

    def encode(self, config, pretty=True):
        if not isinstance(config, ConfigModel):
            raise TypeError("'config' must be a ConfigModel.")
        if pretty:
            return json.dumps(config.py_value(), sort_keys=True, indent=2, cls=PrettyJSONEncoder)
        else:
            return json.dumps(config.py_value(), sort_keys=True, separators=(',', ':'))


def encode(config, cls=None, pretty=True):
    """
    Encodes a config instance.
    :param config: Any instance of ConfigModel.
    :type config: ConfigModel
    :param cls: The encoder class. Must be of type ConfigEncoder.
    :type cls: ConfigEncoder
    :param pretty: Whether or not the encoder should attempt to return a human readable format.
    """
    cls = cls or JsonEncoder  # default to json
    if not issubclass(cls, ConfigEncoder):
        raise TypeError("'cls' must be a ConfigEncoder")
    return cls().encode(config, pretty)
