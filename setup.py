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

# else:
#     os.chdir(os.path.join(basedir, 'src'))
#     os.system('make clean')
#     os.system('rm ../monetdblite/*.so ../monetdblite/*.dylib ../monetdblite/*.dll')
#     os.chdir(current_directory)
#     try:
#         import pypandoc
#         long_description = pypandoc.convert('README.md', 'rst')
#     except(IOError, ImportError):
#         long_description = open('README.md').read()


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


    def get_python_link_flags():
        libpythonlib = 'python' + sysconfig.get_python_version()
        libs = ['-L' + getvar('prefix') + ' -L' + path.join(getvar('prefix'),'libs') +  ' -L' + path.join(getvar('prefix'),'lib') + ' -l' + libpythonlib]
        libs += getvar('LIBS').split()
        libs += getvar('SYSLIBS').split()
        if getvar('Py_ENABLE_SHARED') == '' and getvar('LIBPL') != '':
            libs.insert(0, '-L' + getvar('LIBPL'))
        if getvar('PYTHONFRAMEWORK') == '':
            libs.extend(getvar('LINKFORSHARED').split())
        return re.sub('\S+stack_size\S+', '', ' '.join(libs))

    basedir = os.path.dirname(os.path.realpath(__file__))
    if os.name == 'nt':
        so_extension = '.dll'
        makecmd = 'mingw32-make -C src OPT=true'
    else:
        so_extension = '.so'
        makecmd = 'make -C src -j OPT=true'

    # build the dynamic library (.so/.dylib) on linux/osx
    os.environ['MONETDBLITE_PYTHON_INCLUDE_FLAGS'] = get_python_include_flags()
    os.environ['MONETDBLITE_PYTHON_LINK_FLAGS'] = get_python_link_flags()
    current_directory = os.getcwd()
    os.chdir(basedir)
    proc = subprocess.Popen(makecmd, shell=True)
    if proc.wait() != 0:
        raise Exception('Failed to compile MonetDBLite sources. Check output for error messages.')

    os.chdir(current_directory)
    monetdb_shared_lib_base = "libmonetdb5" + so_extension
    monetdb_shared_lib = os.path.join(basedir, 'src', 'build', monetdb_shared_lib_base)
    final_shared_library = os.path.join('monetdblite', monetdb_shared_lib_base)
    copyfile(monetdb_shared_lib, final_shared_library)

# hook to call our build script only when building
class CustomBuild(build_py):
    def run(self):
        build_monetdblite()
        super().run()

# now actually create the package
# the package is a single C file that only dynamically
# loads functions from libmonetdb5.[so|dylib|dll]
setup(
    name = "monetdblite",
    version = '0.6.0.post34',
    description = 'Embedded MonetDB Python Database.',
    author = 'Mark Raasveldt, Hannes Mühleisen',
    author_email = 'm.raasveldt@cwi.nl',
    keywords = 'MonetDB, MonetDBLite, Database',
    packages = ['monetdblite'],
    package_data={
        'monetdblite': ['*.so', '*.dylib', '*.dll'],
    },
    url="https://github.com/hannesmuehleisen/MonetDBLite-Python",
    long_description = "", # FIXME
    install_requires=[
        'numpy',
    ],
    cmdclass={'build_py': CustomBuild}
)
