# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.  If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright 1997 - July 2008 CWI, August 2008 - 2019 MonetDB B.V.

import ctypes
import os
import sys

from monetdblite import monetize
from monetdblite import exceptions

PY3 = sys.version_info[0] >= 3

basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)

libs = list()
for directory in sys.path:
    if not os.path.isdir(directory):
        continue
    for filename in os.listdir(directory):
        full_filename = os.path.join(directory, filename)
        if os.path.isfile(full_filename) and filename.startswith('libmonetdb5') and (filename.endswith('.so') or filename.endswith('.dylib') or filename.endswith('.dll') or filename.endswith('.pyd')):
            libs.append(full_filename)

if len(libs) == 0:
    raise Exception('Could not locate library file "libmonetdb5.[dll|so|dylib|pyd] in folder %s' % basedir)

try:
    import numpy
except ImportError:
    raise Exception('MonetDBLite requires numpy but import of numpy failed')

try:
    import pandas
except ImportError:
    raise Exception('MonetDBLite requires pandas but importing pandas failed')

if os.name == 'nt':
    os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.abspath(__file__))
# make mal_linker happy
os.environ["MONETDBLITE_LIBNAME"] = libs[0]
dll = ctypes.PyDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                libs[0]), mode=ctypes.RTLD_GLOBAL)

dll.python_monetdblite_init.argtypes = []
dll.python_monetdblite_init.restype = None
dll.python_monetdblite_init()

dll.python_monetdb_init.argtypes = [ctypes.c_char_p, ctypes.c_int]
dll.python_monetdb_init.restype = ctypes.py_object

dll.python_monetdb_sql.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
dll.python_monetdb_sql.restype = ctypes.py_object

dll.python_monetdb_insert.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.py_object
]
dll.python_monetdb_insert.restype = ctypes.py_object

dll.python_monetdb_set_autocommit.argtypes = [ctypes.c_void_p, ctypes.c_int]
dll.python_monetdb_set_autocommit.restype = ctypes.py_object

dll.python_monetdb_client.argtypes = []
dll.python_monetdb_client.restype = ctypes.c_void_p

dll.python_monetdb_disconnect.argtypes = [ctypes.c_void_p]
dll.python_monetdb_disconnect.restype = None

dll.python_monetdb_shutdown.argtypes = []
dll.python_monetdb_shutdown.restype = None

# Global variables. Every function *assinging* to them needs to declare
# them. See: https://docs.python.org/3/reference/simple_stmts.html#the-global-statement
MONETDBLITE_IS_INITIALIZED = False
MONETDBLITE_CURRENT_DATABASE = None


class PyClient:
    def __init__(self):
        self.client = dll.python_monetdb_client()

    def get_client(self):
        return self.client


if PY3:
    def utf8_encode(instr):
        if instr is None:
            return None
        if isinstance(instr, str):
            return instr.encode('utf-8')
        return instr
else:
    def utf8_encode(instr):
        return instr


def __throw_exception(str):
    raise exceptions.DatabaseError(str.replace('MALException:', ''))


def init(directory):
    """Initializes the MonetDBLite database in the specified directory."""
    global MONETDBLITE_CURRENT_DATABASE
    global MONETDBLITE_IS_INITIALIZED
    if is_initialized():
        raise exceptions.DatabaseError('Directory {} has already been initialized'.format(directory))

    if directory == ':memory:':
        directory = None
    else:
        directory = utf8_encode(os.path.abspath(directory))
    retval = dll.python_monetdb_init(directory, 0)
    if retval is not None:
        raise __throw_exception(str(retval) + ' in ' + str(directory))
    MONETDBLITE_IS_INITIALIZED = True
    MONETDBLITE_CURRENT_DATABASE = directory


def is_initialized():
    return MONETDBLITE_IS_INITIALIZED


def dbpath():
    return MONETDBLITE_CURRENT_DATABASE


def sql(query, client=None):
    """Executes a SQL statement on the database if the database
       has been initialized. If no client context is provided,
       the default client context is used. Otherwise the specified
       client context is used to execute the query."""

    if client is not None and not isinstance(client, PyClient):
        raise __throw_exception("client must be of type PyClient")
    client_object = None
    if client is not None:
        client_object = client.get_client()

    retval = dll.python_monetdb_sql(client_object, utf8_encode(query))
    if isinstance(retval, str):
        raise __throw_exception(str(retval))
    else:
        return retval


def __convert_pandas_to_numpy_dict__(df):
    if type(df) == pandas.DataFrame:
        res = {}
        for tpl in df.to_dict().items():
            res[tpl[0]] = numpy.array(list(tpl[1].values()))
        return res
    return df


def insert(table, values, schema=None, client=None):
    """Inserts a set of values into the specified table. The values must
       be either a pandas dataframe or a dictionary of values. If no schema
       is specified, the "sys" schema is used. If no client context is
       provided, the default client context is used. """

    if client is not None and not isinstance(client, PyClient):
        raise __throw_exception("client must be of type PyClient")
    client_object = None
    if client is not None:
        client_object = client.get_client()

    if not isinstance(values, dict):
        values = __convert_pandas_to_numpy_dict__(values)
    else:
        vals = {}
        for tpl in values.items():
            if isinstance(tpl[1], numpy.ma.core.MaskedArray):
                vals[tpl[0]] = tpl[1]
            else:
                vals[tpl[0]] = numpy.array(tpl[1])
        values = vals
    retval = dll.python_monetdb_insert(client_object, utf8_encode(schema),
                                       utf8_encode(table), values)
    if isinstance(retval, str):
        raise __throw_exception(str(retval))
    else:
        return retval


def create(table, values, schema=None, client=None):
    """Creates a table from a set of values or a pandas DataFrame."""
    column_types = []

    if not isinstance(values, dict):
        values = __convert_pandas_to_numpy_dict__(values)
    else:
        vals = {}
        for tpl in values.items():
            if isinstance(tpl[1], numpy.ma.core.MaskedArray):
                vals[tpl[0]] = tpl[1]
            else:
                vals[tpl[0]] = numpy.array(tpl[1])
        values = vals
    if schema is None:
        schema = "sys"
    for key, value in values.items():
        arr = numpy.array(value)
        if arr.dtype == numpy.bool:
            column_type = "BOOLEAN"
        elif arr.dtype == numpy.int8:
            column_type = 'TINYINT'
        elif arr.dtype == numpy.int16 or arr.dtype == numpy.uint8:
            column_type = 'SMALLINT'
        elif arr.dtype == numpy.int32 or arr.dtype == numpy.uint16:
            column_type = 'INT'
        elif arr.dtype == numpy.int64 or arr.dtype == numpy.uint32 or arr.dtype == numpy.uint64:
            column_type = 'BIGINT'
        elif arr.dtype == numpy.float32:
            column_type = 'REAL'
        elif arr.dtype == numpy.float64:
            column_type = 'DOUBLE'
        elif numpy.issubdtype(arr.dtype, numpy.str_) or numpy.issubdtype(arr.dtype, numpy.unicode_):
            column_type = 'STRING'
        else:
            raise Exception('Unsupported dtype: %s' % (str(arr.dtype)))
        column_types.append(column_type)
    query = 'CREATE TABLE %s.%s (' % (monetize.monet_identifier_escape(schema), monetize.monet_identifier_escape(table))
    index = 0
    for key in values.keys():
        query += '%s %s, ' % (monetize.monet_identifier_escape(key), column_types[index])
        index += 1
    query = query[:-2] + ");"
    # create the table
    sql(query, client=client)
    # insert the data into the table
    insert(table, values, schema=schema, client=client)


def connect():
    return PyClient()


def disconnect(client):
    if not isinstance(client, PyClient):
        raise __throw_exception("client must be of type PyClient")
    dll.python_monetdb_disconnect(client.get_client())


def shutdown():
    global MONETDBLITE_CURRENT_DATABASE
    global MONETDBLITE_IS_INITIALIZED

    MONETDBLITE_IS_INITIALIZED = False
    MONETDBLITE_CURRENT_DATABASE = None
    retval = dll.python_monetdb_shutdown()
    if isinstance(retval, str):
        raise __throw_exception(str(retval))
    else:
        return retval


def set_autocommit(val, client=None):
    if client is not None and not isinstance(client, PyClient):
        raise __throw_exception("client must be of type PyClient")
    client_object = None
    if client is not None:
        client_object = client.get_client()

    retval = dll.python_monetdb_set_autocommit(client_object, val)
    if isinstance(retval, str):
        raise __throw_exception(str(retval))
    else:
        return retval
