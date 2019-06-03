# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.  If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright 1997 - July 2008 CWI, August 2008 - 2019 MonetDB B.V.

import numpy
import pandas


class TestSimpleDBAPI(object):
    def test_regular_selection(self, monetdblite_cursor):
        monetdblite_cursor.execute('SELECT * FROM integers')
        result = monetdblite_cursor.fetchall()
        assert result == [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9],
                          [None]], "Incorrect result returned"

    def test_numpy_selection(self, monetdblite_cursor):
        monetdblite_cursor.execute('SELECT * FROM integers')
        result = monetdblite_cursor.fetchnumpy()
        arr = numpy.ma.masked_array(numpy.arange(11))
        arr.mask = [False] * 10 + [True]
        numpy.testing.assert_array_equal(result['i'], arr,
                                         "Incorrect result returned")

    def test_pandas_selection(self, monetdblite_cursor):
        monetdblite_cursor.execute('SELECT * FROM integers')
        result = monetdblite_cursor.fetchdf()
        arr = numpy.ma.masked_array(numpy.arange(11))
        arr.mask = [False] * 10 + [True]
        arr = {'i': arr}
        arr = pandas.DataFrame.from_dict(arr)
        # assert str(result) == str(arr), "Incorrect result returned"
        pandas.testing.assert_frame_equal(result, arr)

    def test_numpy_creation(self, monetdblite_cursor):
        # numpyarray = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=(1, 10))}  # segfaults
        data_dict = {
            'i': numpy.arange(10),
            'v': numpy.random.randint(100, size=10)
        }
        monetdblite_cursor.create('numpy_creation', data_dict)
        monetdblite_cursor.commit()

        monetdblite_cursor.execute('SELECT * FROM numpy_creation')
        result = monetdblite_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
        numpy.testing.assert_array_equal(result['v'], data_dict['v'])

    def test_pandas_creation(self, monetdblite_cursor):
        data_dict = {
            'i': numpy.arange(10),
            'v': numpy.random.randint(100, size=10)
        }
        dframe = pandas.DataFrame.from_dict(data_dict)
        monetdblite_cursor.create('dframe_creation', dframe)

        monetdblite_cursor.execute('SELECT * FROM dframe_creation')
        result = monetdblite_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
        numpy.testing.assert_array_equal(result['v'], data_dict['v'])

    def test_numpy_insertion(self, monetdblite_cursor):
        data_dict = {
            'i': numpy.arange(10),
            'v': numpy.random.randint(100, size=10)
        }
        monetdblite_cursor.execute(
            "CREATE TABLE numpy_insertion (i INT, v INT)")
        monetdblite_cursor.insert('numpy_insertion', data_dict)
        monetdblite_cursor.commit()

        monetdblite_cursor.execute("SELECT * FROM numpy_insertion")
        result = monetdblite_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
        numpy.testing.assert_array_equal(result['v'], data_dict['v'])

    def test_pandas_insertion(self, monetdblite_cursor):
        data_dict = {
            'i': numpy.arange(10),
            'v': numpy.random.randint(100, size=10)
        }
        dframe = pandas.DataFrame.from_dict(data_dict)
        monetdblite_cursor.execute(
            "CREATE TABLE pandas_insertion (i INT, v INT)")
        monetdblite_cursor.insert('pandas_insertion', dframe)
        monetdblite_cursor.commit()

        monetdblite_cursor.execute("SELECT * FROM pandas_insertion")
        result = monetdblite_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
        numpy.testing.assert_array_equal(result['v'], data_dict['v'])

    def test_masked_array_insertion(self, monetdblite_cursor):
        data_dict = {
            'i':
            numpy.ma.masked_array(numpy.arange(10),
                                  mask=([False] * 9 + [True]))
        }
        monetdblite_cursor.execute(
            "CREATE TABLE masked_array_insertion (i INT)")
        monetdblite_cursor.insert("masked_array_insertion", data_dict)
        monetdblite_cursor.commit()

        monetdblite_cursor.execute("SELECT * FROM masked_array_insertion")
        result = monetdblite_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
