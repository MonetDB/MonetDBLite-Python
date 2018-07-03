#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils import sysconfig
import ntpath
import os
import sys
from shutil import copyfile
import subprocess
import platform
import re
from setuptools import setup, find_packages

PY3 = sys.version_info[0] >= 3
bits = platform.architecture()[0]

pypi_upload = 'MONETDBLITE_PIP_UPLOAD' in os.environ

def getvar(n):
    val = sysconfig.get_config_var(n)
    if (val is None):
        val = ''
    return val

def get_python_include_flags():
    pyver = sysconfig.get_config_var('VERSION')
    flags = ['-I' + sysconfig.get_python_inc(),
             '-I' + sysconfig.get_python_inc(plat_specific=True)]
    flags.extend(getvar('CFLAGS').split())
    flags.append('-I' + numpy.get_include())
    return ' '.join(flags)


def get_python_link_flags():
    pyver = sysconfig.get_config_var('VERSION')
    libs = ['-L' + sysconfig.get_config_var('LIBDIR') +
           ' -l' + sysconfig.get_config_var('LIBRARY').replace('.a', '').replace('.so', '').replace('.dll', '').replace('.so', '').replace('lib', '')]
    libs += getvar('LIBS').split()
    libs += getvar('SYSLIBS').split()
    if not getvar('Py_ENABLE_SHARED'):
        libs.insert(0, '-L' + getvar('LIBPL'))
    if not getvar('PYTHONFRAMEWORK'):
        libs.extend(getvar('LINKFORSHARED').split())
    return re.sub('\S+stack_size\S+', '', ' '.join(libs))


basedir = os.path.dirname(os.path.realpath(__file__))
if os.name == 'nt':
    so_extension = '.dll'
    makecmd = 'mingw32-make -C src'
else:
    so_extension = '.so'
    makecmd = 'make -C src -j'

try:
    import numpy
except ImportError:
    print('Building MonetDBLite from source requires NumPy to be installed.')
    exit(1)

# build the dynamic library (.so/.dylib) on linux/osx
os.environ['MONETDBLITE_PYTHON_INCLUDE_FLAGS'] = get_python_include_flags()
os.environ['MONETDBLITE_PYTHON_LINK_FLAGS'] = get_python_link_flags()
current_directory = os.getcwd()
os.chdir(basedir)
if not pypi_upload:
    # don't build the package if we are uploading to pip
    proc = subprocess.Popen([makecmd], stderr=subprocess.PIPE, shell=True)
    if proc.wait() != 0:
        error = proc.stderr.read()
        raise Exception('Failed to compile MonetDBLite sources: ' +
            ("No error specified" if error is None else
            (error.decode('utf8') if PY3 else error)))
os.chdir(current_directory)
monetdb_shared_lib_base = "libmonetdb5" + so_extension
monetdb_shared_lib = os.path.join(basedir, 'src', 'build', monetdb_shared_lib_base)
final_shared_library = os.path.join('monetdblite', monetdb_shared_lib_base)

long_description = ""
if not pypi_upload:
    # don't include the [so|dylib|dll] in the packaged version uploaded to pip
    copyfile(monetdb_shared_lib, final_shared_library)

else:
    os.chdir(os.path.join(basedir, 'src'))
    os.system('make clean')
    os.system('rm ../monetdblite/*.so ../monetdblite/*.dylib ../monetdblite/*.dll')
    os.chdir(current_directory)
    try:
        import pypandoc
        long_description = pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError):
        long_description = open('README.md').read()

# now actually create the package
# the package is a single C file that only dynamically
# loads functions from libmonetdb5.[so|dylib|dll]
setup(
    name = "monetdblite",
    version = '0.6.0.post3',
    description = 'Embedded MonetDB Python Database.',
    author = 'Mark Raasveldt, Hannes Mühleisen',
    author_email = 'm.raasveldt@cwi.nl',
    keywords = 'MonetDB, MonetDBLite, Database',
    packages = ['monetdblite'],
    package_data={
        'monetdblite': ['*.so', '*.dylib', '*.dll'],
    },
    url="https://github.com/hannesmuehleisen/MonetDBLite-Python",
    long_description = long_description
    )
