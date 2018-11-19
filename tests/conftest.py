import numpy
import os
import pytest
import shutil

import monetdblite


@pytest.fixture(scope="function")
def monetdblite_empty_cursor(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        monetdblite.shutdown()
        if tmp_path.is_dir():
            shutil.rmtree(test_dbfarm)

    request.addfinalizer(finalizer)
    connection = monetdblite.connect(test_dbfarm)
    cursor = connection.cursor()
    return cursor

@pytest.fixture(scope="function")
def monetdblite_cursor(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        monetdblite.shutdown()
        if tmp_path.is_dir():
            shutil.rmtree(test_dbfarm)

    request.addfinalizer(finalizer)

    connection = monetdblite.connect(test_dbfarm)
    cursor = connection.cursor()
    cursor.create('integers', {'i': numpy.arange(10)})
    cursor.execute('INSERT INTO integers VALUES(NULL)')
    return cursor


@pytest.fixture(scope="function")
def monetdblite_cursor_autocommit(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        monetdblite.shutdown()
        if tmp_path.is_dir():
            shutil.rmtree(test_dbfarm)

    request.addfinalizer(finalizer)

    connection = monetdblite.connect(test_dbfarm)
    connection.set_autocommit(True)
    cursor = connection.cursor()
    return (cursor, connection, test_dbfarm)


@pytest.fixture(scope="function")
def initialize_monetdblite(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        monetdblite.shutdown()
        if tmp_path.is_dir():
            shutil.rmtree(test_dbfarm)

    request.addfinalizer(finalizer)

    monetdblite.init(test_dbfarm)
    return test_dbfarm


@pytest.fixture(scope="function")
def raw_connection(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        monetdblite.shutdown()
        if tmp_path.is_dir():
            shutil.rmtree(test_dbfarm)

    request.addfinalizer(finalizer)

    connection = monetdblite.connect(test_dbfarm)
    return (connection, test_dbfarm)
