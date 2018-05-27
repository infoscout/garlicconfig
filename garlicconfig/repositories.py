# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
from abc import ABCMeta, abstractmethod

from garlicconfig.exceptions import ConfigNotFound

import six


@six.add_metaclass(ABCMeta)
class ConfigRepository(object):

    @abstractmethod
    def all(self):
        """
        Returns a generator containing the name of all available configs.
        """
        pass

    @abstractmethod
    def retrieve(self, name):
        """
        Returns the string data for this config if it exists.
        """
        pass

    @abstractmethod
    def save(self, name, data):
        """
        Saves the string data for the given config.
        """
        pass


class FileConfigRepository(ConfigRepository):

    def __init__(self, root_dir):
        self.root = root_dir

    def all(self):
        rule = re.compile('(.*)\.garlic')
        for fname in os.listdir(self.root):
            config_name = rule.match(fname)
            if not config_name:
                continue
            yield config_name.group(1)

    def retrieve(self, name):
        try:
            with open(os.path.join(self.root, name + '.garlic'), 'r') as config_data:
                return config_data.read()
        except IOError:
            raise ConfigNotFound()

    def save(self, name, data):
        with open(os.path.join(self.root, name + '.garlic'), 'w') as config_file:
            config_file.write(data)


class MemoryConfigRepository(ConfigRepository):

    def __init__(self):
        self.storage = {}

    def all(self):
        return self.storage.keys()

    def retrieve(self, name):
        if name in self.storage:
            return self.storage[name]
        else:
            raise ConfigNotFound

    def save(self, name, data):
        self.storage[name] = data
