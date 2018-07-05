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
from setuptools.command.build_py import build_py
from os import path
import numpy
import glob

basedir = os.path.dirname(os.path.realpath(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert_file(os.path.join(basedir, 'README.md'), 'rst')
except(IOError, ImportError):
    long_description = ''

print(long_description)

def build_monetdblite():
    def getvar(n):
        val = sysconfig.get_config_var(n)
        if (val is None):
            val = ''
        return val

    def get_python_include_flags():
        flags = ['-I' + sysconfig.get_python_inc(),
                 '-I' + sysconfig.get_python_inc(plat_specific=True)]
        flags.extend(getvar('CFLAGS').split())
        flags.append('-I' + numpy.get_include())
        return ' '.join(flags)


    def get_python_link_flags_unix():
        libs = ['-L' + getvar('LIBDIR') +
               ' -l' + getvar('LIBRARY').replace('.a', '').replace('.so', '').replace('.so', '').replace('.dylib', '').replace('lib', '')]
        libs += getvar('LIBS').split()
        libs += getvar('SYSLIBS').split()
        if getvar('Py_ENABLE_SHARED') != '':
            libs.insert(0, '-L' + getvar('LIBPL'))
        if getvar('PYTHONFRAMEWORK') != '':
            libs.extend(getvar('LINKFORSHARED').split())
        return re.sub('\S+stack_size\S+', '', ' '.join(libs))

    if os.name == 'nt':
        so_extension = '.dll'
        makecmd = 'mingw32-make -C src OPT=true'
        linkerflags = '-L' + getvar('prefix') + ' -L' + path.join(getvar('prefix'),'libs') + ' -lpython' + sysconfig.get_python_version().replace('.','')
    else:
        so_extension = '.so'
        makecmd = 'make -C src -j OPT=true'
        linkerflags = get_python_link_flags_unix()

    # build the dynamic library (.so/.dylib) on linux/osx
    os.environ['MONETDBLITE_PYTHON_INCLUDE_FLAGS'] = get_python_include_flags()
    os.environ['MONETDBLITE_PYTHON_LINK_FLAGS'] = linkerflags
    current_directory = os.getcwd()
    os.chdir(basedir)
    proc = subprocess.Popen(makecmd, shell=True)
    if proc.wait() != 0:
        raise Exception('Failed to compile MonetDBLite sources. Check output for error messages.')

    os.chdir(current_directory)
    monetdb_shared_lib_base = "libmonetdb5" + so_extension
    monetdb_shared_lib = os.path.join(basedir, 'src', 'build', monetdb_shared_lib_base)

    final_shared_library = os.path.join('monetdblite', monetdb_shared_lib_base)
    if (not os.path.isfile(monetdb_shared_lib)):
        raise Exception('Failed to compile MonetDBLite sources. Check output for error messages.')

    copyfile(monetdb_shared_lib, final_shared_library)
    if (not os.path.isfile(final_shared_library)):
        raise Exception('Failed to move MonetDBLite library. Check output for error messages.')

    return monetdb_shared_lib_base

# hook to call our build script only when building
# TODO this should really use build_ext instead of build_py
class CustomBuild(build_py):
    def run(self):
        # needless to say, this is a hack
        self.data_files[0][3].append(build_monetdblite())
        build_py.run(self)

# now actually create the package
# the package is a single C file that only dynamically
# loads functions from libmonetdb5.[so|dylib|dll]
setup(
    name = "monetdblite",
    version = '0.6.0.post6',
    description = 'Embedded MonetDB Python Database.',
    author = 'Mark Raasveldt, Hannes Mühleisen',
    author_email = 'm.raasveldt@cwi.nl',
    keywords = 'MonetDB, MonetDBLite, Database',
    packages = ['monetdblite'],
    url="https://github.com/hannesmuehleisen/MonetDBLite-Python",
    long_description = long_description,
    install_requires=[
        'numpy',
    ],
    zip_safe = True,
    cmdclass={'build_py': CustomBuild}
)
