import numpy
import os
import pytest
import shutil
import tempfile

import monetdblite


@pytest.fixture(scope="module")
def monetdblite_cursor():
        test_dbfarm = tempfile.mkdtemp()
        connection = monetdblite.make_connection(test_dbfarm)
        cursor = connection.cursor()
        cursor.create('integers', {'i': numpy.arange(10)})
        cursor.execute('INSERT INTO integers VALUES(NULL)')
        yield cursor

        cursor.close()
        connection.close()
        if os.path.isdir(test_dbfarm):
                shutil.rmtree(test_dbfarm)


@pytest.fixture
def monetdblite_cursor_autocommit():
        test_dbfarm = tempfile.mkdtemp()
        connection = monetdblite.make_connection(test_dbfarm)
        connection.set_autocommit(True)
        cursor = connection.cursor()
        yield (cursor, connection, test_dbfarm)

        cursor.close()
        connection.close()
        if os.path.isdir(test_dbfarm):
                shutil.rmtree(test_dbfarm)

@pytest.fixture
def initialize_monetdblite():
        test_dbfarm = tempfile.mkdtemp()
        monetdblite.init(test_dbfarm)
        yield test_dbfarm
        monetdblite.shutdown()
        if os.path.isdir(test_dbfarm):
                shutil.rmtree(test_dbfarm)
