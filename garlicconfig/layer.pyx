from collections import Iterable

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.map cimport map
from libcpp.memory cimport shared_ptr
from libcpp.string cimport string
from libcpp.vector cimport vector
import six

from garlicconfig.encoding cimport NativeDecoder, JsonDecoder
from garlicconfig.exceptions cimport raise_py_error
from garlicconfig.repositories cimport NativeConfigRepository


try:
    available_str = basestring
except NameError:
    available_str = six.text_type


cdef class GarlicValue(object):

    def __init__(self, value):
        self.native_value = GarlicValue.init_layer_value(value)

    @staticmethod
    cdef shared_ptr[LayerValue] init_layer_value(object value) except +:
        cdef ObjectValue* object_value = NULL
        cdef ListValue* list_value = NULL
        if isinstance(value, bool):
            return shared_ptr[LayerValue](new BoolValue(value))
        elif isinstance(value, int):
            return shared_ptr[LayerValue](new IntegerValue(value))
        elif isinstance(value, float):
            return shared_ptr[LayerValue](new DoubleValue(value))
        elif isinstance(value, available_str):
            return shared_ptr[LayerValue](new StringValue(value.encode('utf-8')))
        elif isinstance(value, dict):
            object_value = new ObjectValue()
            for key in value:
                deref(object_value).set(key.encode('utf-8'), GarlicValue.init_layer_value(value[key]))
            return shared_ptr[LayerValue](object_value)
        elif isinstance(value, Iterable):
            list_value = new ListValue()
            for item in value:
                deref(list_value).add(GarlicValue.init_layer_value(item))
            return shared_ptr[LayerValue](list_value)
        elif value is None:
            return shared_ptr[LayerValue](new NullValue())
        else:
            raise TypeError('Unsupported Type: {invalid_type}'.format(invalid_type=type(value).__name__))

    @staticmethod
    cdef map_object(const shared_ptr[LayerValue]& value):
        cdef dict return_value = {}
        cdef map[string, shared_ptr[LayerValue]].const_iterator it = deref(value).begin_member()
        cdef map[string, shared_ptr[LayerValue]].const_iterator end = deref(value).end_member()
        while it != end:
            return_value[deref(it).first.decode("utf-8")] = GarlicValue.map_value(deref(it).second)
            inc(it)
        return return_value

    @staticmethod
    cdef map_list(const shared_ptr[LayerValue]& value):
        cdef list return_value = []
        cdef vector[shared_ptr[LayerValue]].const_iterator it = deref(value).begin_element()
        cdef vector[shared_ptr[LayerValue]].const_iterator end = deref(value).end_element()
        while it != end:
            return_value.append(GarlicValue.map_value(deref(it)))
            inc(it)
        return return_value

    @staticmethod
    cdef map_value(const shared_ptr[LayerValue]& value):
        if deref(value).is_string():
            return deref(value).get_string().decode('utf-8')
        elif deref(value).is_bool():
            return deref(value).get_bool()
        elif deref(value).is_int():
            return deref(value).get_int()
        elif deref(value).is_double():
            return deref(value).get_double()
        elif deref(value).is_object():
            return GarlicValue.map_object(value)
        elif deref(value).is_array():
            return GarlicValue.map_list(value)
        elif deref(value).is_null():
            return None

    def py_value(self):
        return GarlicValue.map_value(self.native_value)

    def resolve(self, path):
        cdef const shared_ptr[LayerValue]* result = &deref(self.native_value).resolve(path.encode('utf-8'))
        if deref(result) != NotFoundPtr:
            return GarlicValue.map_value(deref(result))

    def clone(self):
        return GarlicValue.native_load(deref(self.native_value).clone())

    def apply(self, GarlicValue value):
        deref(self.native_value).apply(value.native_value)

    @staticmethod
    cdef GarlicValue native_load(const shared_ptr[LayerValue]& value):
        cdef GarlicValue garlic_value = GarlicValue.__new__(GarlicValue)
        garlic_value.native_value = value
        return garlic_value


cdef extern from "utility.cpp":

    cdef shared_ptr[LayerValue] load_value(NativeConfigRepository* repo, NativeDecoder* decoder, const string& name) except +raise_py_error


cdef class LayerRetriever(object):

    def __init__(self, ConfigRepository repository, Decoder decoder=None):
        self.decoder = decoder or JsonDecoder()
        self.repo = repository

    def retrieve(self, name):
        return GarlicValue.native_load(load_value(self.repo.native_repo, self.decoder.native_decoder, name.encode('utf-8')))
