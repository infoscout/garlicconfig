from libcpp.string cimport string
from libcpp.vector cimport vector


class ValidationError(Exception):
    """The provided value is not valid."""
    pass


class ConfigNotFound(Exception):
    """No configuration with such key name was found."""
    pass


error_map = {
    'ConfigNotFound': ConfigNotFound,
    'RuntimeError': RuntimeError,
}


cdef extern from "error_handling_utility.cpp":
    cdef vector[string] get_native_error()


cdef int raise_py_error() except *:
    cdef vector[string] ex_info = get_native_error()
    raise error_map[ex_info[0].decode('utf-8')](ex_info[1].decode('utf-8'))
