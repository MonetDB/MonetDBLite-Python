#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy
import sys
from setuptools import setup, Extension


basedir = os.path.dirname(os.path.realpath(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert_file(os.path.join(basedir, 'README.md'), 'rst')
except(IOError, ImportError):
    long_description = ''

sources = []
includes = [numpy.get_include()]
excludes = ['strptime.c', 'inlined_scripts.c', 'decompress.c', 'fsync.c']


def generate_sources_includes(dir):
    includes.append(dir)
    for root, dirs, files in os.walk(dir):
        for name in files:
            if name.endswith('.c') and name not in excludes:
                sources.append(os.path.join(root, name))
        for name in dirs:
            includes.append(os.path.join(root, name))


generate_sources_includes('src/embeddedpy')
generate_sources_includes('src/monetdblite/src')

libmonetdb5 = Extension('monetdblite.libmonetdb5',
                        define_macros=[('LIBGDK',              None),
                                       ('LIBMAL',              None),
                                       ('LIBOPTIMIZER',        None),
                                       ('LIBSTREAM',           None),
                                       ('LIBSQL',              None),
                                       ('LIBPYAPI',            None),
                                       ('MONETDBLITE_COMPILE', None)],
    include_dirs=includes,
    sources=sources,
    extra_compile_args=['-std=c99'],  # needed for linux build
    language='c')

setup(
    name = "monetdblite_test",
    version = '0.7.0.dev0',
    # version = '0.7.0.dev0+Aug2018.C-d8b1b5e',
    description = 'Embedded MonetDB Python Database.',
    author = 'Mark Raasveldt, Hannes Mühleisen',
    author_email = 'm.raasveldt@cwi.nl',
    keywords = 'MonetDB MonetDBLite Database SQL OLAP',
    packages = ['monetdblite'],
    package_dir = {'': 'lib'},
    url="https://github.com/hannesmuehleisen/MonetDBLite-Python",
    long_description = long_description,
    install_requires=[
        'numpy>=1.7',
        'pandas>=0.20'
    ],
    # zip_safe = False,
    classifiers = [
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: C',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha'
    ],
    ext_modules = [libmonetdb5]
)
