from encoding cimport NativeJsonDecoder


cdef class Decoder(object):

    def __dealloc__(self):
        if self.native_decoder:
            del self.native_decoder


cdef class JsonDecoder(Decoder):

    def __init__(self):
        self.native_decoder = self.json_decoder = new NativeJsonDecoder()
