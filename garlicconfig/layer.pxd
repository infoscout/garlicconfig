from libcpp.map cimport map
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr

from encoding cimport Decoder
from repositories cimport ConfigRepository


cdef extern from "GarlicConfig/garlicconfig.h" namespace "garlic":

    cdef cppclass LayerValue:

        bool is_string()
        bool is_bool()
        bool is_int()
        bool is_double()
        bool is_array()
        bool is_object()

        const string& get_string()
        const int& get_int()
        const double& get_double()
        const bool& get_bool()

        map[string, shared_ptr[LayerValue]].const_iterator begin_member()
        map[string, shared_ptr[LayerValue]].const_iterator end_member()

        vector[shared_ptr[LayerValue]].const_iterator begin_element()
        vector[shared_ptr[LayerValue]].const_iterator end_element()

        const shared_ptr[LayerValue]& resolve(const string& path)
        void apply(const shared_ptr[LayerValue]& layer)

        shared_ptr[LayerValue] clone()


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
    cdef native_load(const shared_ptr[LayerValue]& value)


cdef class LayerRetriever(object):

    cdef ConfigRepository repo
    cdef Decoder decoder

