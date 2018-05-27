# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from setuptools import find_packages, setup

with open('VERSION', 'r') as reader:
    version = reader.read().strip()


def get_long_description():
    with open('README.md', 'r') as reader:
        return reader.read()


setup(
    author='Peyman Mortazavi',
    author_email='pey.mortazavi@gmail.com',
    name='garlicconfig',
    packages=find_packages(),
    include_package_data=True,
    description='InfoScout GarlicConfig',
    long_description=get_long_description(),
    long_description_content_type='text/markdown; charset=UTF-8',
    url='https://github.com/infoscout/garlicconfig',
    download_url='https://github.com/infoscout/garlicconfig/archive/{version}.tar.gz'.format(version=version),
    version=version,
    install_requires=['six'],
    keywords=['configs', 'settings']
)
