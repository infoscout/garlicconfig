cdef extern from "GarlicConfig/garlicconfig.h" namespace "garlic":

    cdef cppclass NativeDecoder "garlic::Decoder":
        pass

    cdef cppclass NativeJsonDecoder "garlic::JsonDecoder" (NativeDecoder):
        pass


cdef class Decoder(object):

    cdef NativeDecoder* native_decoder


cdef class JsonDecoder(Decoder):

    cdef NativeJsonDecoder* json_decoder
