# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod

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
