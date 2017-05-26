from setuptools import find_packages, setup

with open('VERSION', 'r') as f:
    version = f.read().strip()

setup(
    name='garlicconfig',
    packages=find_packages(),
    include_package_data=True,
    description='InfoScout GarlicConfig',
    url='http://github.com/infoscout/garlicconfig',
    version=version,
)
