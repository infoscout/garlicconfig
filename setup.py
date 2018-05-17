from setuptools import find_packages, setup

with open('VERSION', 'r') as f:
    version = f.read().strip()

setup(
    author='Peyman Mortazavi',
    author_email='pey.mortazavi@gmail.com',
    name='garlicconfig',
    packages=find_packages(),
    include_package_data=True,
    description='InfoScout GarlicConfig',
    url='https://github.com/infoscout/garlicconfig',
    download_url='https://github.com/infoscout/garlicconfig/archive/{version}.tar.gz'.format(version=version),
    version=version,
    keywords=['configs', 'settings', '']
)
