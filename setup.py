from setuptools import find_packages, setup
from setuptools.extension import Extension
from Cython.Build import cythonize


common_params = dict(
    language='c++',
    include_dirs=['cget/include'],
    library_dirs=['cget/lib', 'cget/lib64'],
    libraries=['GarlicConfig'],
    extra_compile_args=['-std=c++11']
)


def create_extension(name):
    return Extension(
        name='garlicconfig.{name}'.format(name=name),
        sources=['garlicconfig/{name}.pyx'.format(name=name)],
        **common_params
    )


ext_modules = [
    create_extension('exceptions'),
    create_extension('repositories'),
    create_extension('layer'),
    create_extension('encoding'),
]

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
    keywords=['configs', 'settings'],
    ext_modules=cythonize(ext_modules),
    zip_safe=False
)
