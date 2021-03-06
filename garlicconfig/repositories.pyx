from libcpp.string cimport string

from exceptions cimport raise_py_error
from repositories cimport NativeConfigRepository, NativeFileConfigRepository, NativeMemoryConfigRepository


cdef extern from 'utility.cpp':

    cdef void save_str_to_repo(NativeConfigRepository* repo, const string& name, const string& content) except +raise_py_error
    cdef string read_str_from_repo(NativeConfigRepository* repo, const string& name) except +raise_py_error


cdef class ConfigRepository(object):
    """
    Base class for garlic config repositories. Repository classes are responsible for loading config files.
    This is a base class, you cannot construct instances of this class.
    """

    def list_configs(self):
        """
        List all available configs in this repository.
        :return: set of str
        """
        cdef set[string] configs
        if self.native_repo:
            configs = self.native_repo.list_configs()
            for item in configs:
                yield item.decode('UTF-8')

    def save(self, name, content):
        """
        Save a config.
        :param name: The name of the config. Config data can later be accessed by passing this name to retrieve method.
        :param content: The str content of this config.
        """
        if self.native_repo:
            save_str_to_repo(self.native_repo, name.encode('UTF-8'), content.encode('UTF-8'))

    def retrieve(self, name):
        """
        Retrieve a config. If no config with such name is available, ConfigNotFound exception gets raised.
        :param name: Name of the config.
        :return: str
        """
        if self.native_repo:
            return read_str_from_repo(self.native_repo, name.encode('UTF-8')).decode('UTF-8')

    def __dealloc__(self):
        if self.native_repo:
            del self.native_repo


cdef class FileConfigRepository(ConfigRepository):
    """
    A repository that uses files with garlic extension to store config data. Note that the content could be in any format.
    """

    def __init__(self, root_path):
        self.native_repo = self.file_repo = new NativeFileConfigRepository(root_path.encode('UTF-8'))


cdef class MemoryConfigRepository(ConfigRepository):
    """
    A repository that uses memory to store garlic configs, this should be used if temporary access is needed.
    """

    def __init__(self):
        self.native_repo = self.memory_repo = new NativeMemoryConfigRepository()
