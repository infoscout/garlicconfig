from garlicconfig.layer cimport GarlicValue


cdef class ConfigField(object):

    cdef void native_validate(self, value, null_check) except *
    cdef inline GarlicValue get_garlic_value(self, value) except +:
        return GarlicValue(value)


cpdef validate_model_fields(model)