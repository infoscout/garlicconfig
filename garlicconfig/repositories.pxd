from libcpp.set cimport set
from libcpp.string cimport string


cdef extern from "GarlicConfig/garlicconfig.h" namespace "garlic":

    cdef cppclass NativeConfigRepository "garlic::ConfigRepository":
        set[string] list_configs()


    cdef cppclass NativeFileConfigRepository "garlic::FileConfigRepository" (NativeConfigRepository):
        NativeFileConfigRepository(const string& root_path) except +


    cdef cppclass NativeMemoryConfigRepository "garlic::MemoryConfigRepository" (NativeConfigRepository):
        pass


cdef class ConfigRepository(object):
    """
    Base class for garlic config repositories. Repository classes are responsible for loading config files.
    This is a base class, you cannot construct instances of this class.
    """
    cdef NativeConfigRepository* native_repo


cdef class FileConfigRepository(ConfigRepository):
    """
    A repository that uses files with garlic extension to store config data. Note that the content could be in any format.
    """
    cdef NativeFileConfigRepository* file_repo


cdef class MemoryConfigRepository(ConfigRepository):
    """
    A repository that uses memory to store garlic configs, this should be used if temporary access is needed.
    """
    cdef NativeMemoryConfigRepository* memory_repo
