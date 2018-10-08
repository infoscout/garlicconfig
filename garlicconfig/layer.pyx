from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.map cimport map
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr

from encoding cimport NativeDecoder, JsonDecoder
from exceptions cimport raise_py_error
from repositories cimport NativeConfigRepository


cdef class GarlicValue(object):

    @staticmethod
    cdef map_object(const shared_ptr[LayerValue]& value):
        cdef dict return_value = {}
        cdef map[string, shared_ptr[LayerValue]].const_iterator it = deref(value).begin_member()
        cdef map[string, shared_ptr[LayerValue]].const_iterator end = deref(value).end_member()
        while it != end:
            return_value[deref(it).first] = GarlicValue.map_value(deref(it).second)
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
            return deref(value).get_string().decode("utf-8")
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

    def as_dict(self):
        return GarlicValue.map_value(self.native_value)

    def resolve(self, const string& path):
        cdef const shared_ptr[LayerValue]* result = &deref(self.native_value).resolve(path)
        if deref(result) != NotFoundPtr:
            return GarlicValue.map_value(deref(result))

    def clone(self):
        return GarlicValue.native_load(deref(self.native_value).clone())

    def apply(self, GarlicValue value):
        deref(self.native_value).apply(value.native_value)

    @staticmethod
    cdef native_load(const shared_ptr[LayerValue]& value):
        garlic_value = GarlicValue()
        garlic_value.native_value = value
        return garlic_value


cdef extern from "utility.cpp":

    cdef shared_ptr[LayerValue] load_value(NativeConfigRepository* repo, NativeDecoder* decoder, const string& name) except +raise_py_error


cdef class LayerRetriever(object):

    def __init__(self, ConfigRepository repository, Decoder decoder=None):
        self.decoder = decoder or JsonDecoder()
        self.repo = repository

    def retrieve(self, const string& name):
        return GarlicValue.native_load(load_value(self.repo.native_repo, self.decoder.native_decoder, name))
