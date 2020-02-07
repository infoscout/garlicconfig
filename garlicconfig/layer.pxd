from libcpp cimport bool as cbool
from libcpp.map cimport map
from libcpp.memory cimport shared_ptr
from libcpp.string cimport string
from libcpp.vector cimport vector

from garlicconfig.encoding cimport Decoder
from garlicconfig.repositories cimport ConfigRepository


cdef extern from "GarlicConfig/garlicconfig.h" namespace "garlic":

    cdef cppclass LayerValue:

        cbool is_string()
        cbool is_bool()
        cbool is_int()
        cbool is_double()
        cbool is_array()
        cbool is_object()
        cbool is_null()

        const string& get_string()
        const int& get_int()
        const double& get_double()
        const cbool& get_bool()

        void set(const string& key, const shared_ptr[LayerValue]& value)
        void set(const string& key, shared_ptr[LayerValue]&& value)

        void add(const shared_ptr[LayerValue]& value)
        void add(const shared_ptr[LayerValue]&& value)

        map[string, shared_ptr[LayerValue]].const_iterator begin_member()
        map[string, shared_ptr[LayerValue]].const_iterator end_member()

        vector[shared_ptr[LayerValue]].const_iterator begin_element()
        vector[shared_ptr[LayerValue]].const_iterator end_element()

        const shared_ptr[LayerValue]& resolve(const string& path)
        void apply(const shared_ptr[LayerValue]& layer)

        shared_ptr[LayerValue] clone()

    cdef cppclass StringValue(LayerValue):
        StringValue(const string& value) except +

    cdef cppclass IntegerValue(LayerValue):
        IntegerValue(const int& value) except +

    cdef cppclass DoubleValue(LayerValue):
        DoubleValue(const double& value) except +

    cdef cppclass BoolValue(LayerValue):
        BoolValue(const cbool& value) except +

    cdef cppclass ObjectValue(LayerValue):
        ObjcetValue() except +

    cdef cppclass ListValue(LayerValue):
        ListValue() except +

    cdef cppclass NullValue(LayerValue):
        NullValue() except +

    cdef shared_ptr[LayerValue] NotFoundPtr


cdef class GarlicValue(object):

    cdef shared_ptr[LayerValue] native_value

    @staticmethod
    cdef map_object(const shared_ptr[LayerValue]& value)

    @staticmethod
    cdef map_list(const shared_ptr[LayerValue]& value)

    @staticmethod
    cdef map_value(const shared_ptr[LayerValue]& value)

    @staticmethod
    cdef GarlicValue native_load(const shared_ptr[LayerValue]& value)

    @staticmethod
    cdef shared_ptr[LayerValue] init_layer_value(object value) except +


cdef class LayerRetriever(object):

    cdef ConfigRepository repo
    cdef Decoder decoder

