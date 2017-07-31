from abc import ABCMeta, abstractmethod


class ConfigManager(object):
    """
    Abstract class for all config managers.
    Use this class to define custom configuration pulling logic.
    For example, if you need to merge all configurations in the same folder.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def iterconfigs(self):
        """Similar to iteritems method. Iterate through all configurations, this will not cache results."""
        pass

    @abstractmethod
    def resolve(self, path, **filters):
        pass
