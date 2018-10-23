# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod

from garlicconfig.layer import LayerRetriever

import six


@six.add_metaclass(ABCMeta)
class ConfigManager(object):
    """
    Abstract class for all config managers.
    Use this class to define custom configuration pulling logic.
    For example, if you need to merge all configurations in the same folder.
    """

    @abstractmethod
    def iterconfigs(self):
        """Similar to iteritems method. Iterate through all configurations, this will not cache results."""
        pass

    @abstractmethod
    def resolve(self, path, **filters):
        pass


class FlatConfigManager(ConfigManager):

    def __init__(self, repository, decoder=None, default_config_name=None):
        self.repository = repository
        self.decoder = decoder
        self.default_config_name = default_config_name
        self.__layer_retriever = LayerRetriever(repository, decoder)

    def iterconfigs(self):
        for config in self.repository.list_configs():
            yield config, self.__layer_retriever.retrieve(config)

    def resolve(self, path, **filters):
        return self.__layer_retriever.retrieve(filters.get('name', self.default_config_name)).resolve(path)
