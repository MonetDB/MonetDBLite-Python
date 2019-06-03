# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.  If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright 1997 - July 2008 CWI, August 2008 - 2019 MonetDB B.V.
import monetdblite
import numpy
import os
import shutil
import sys
import pytest

PY26 = sys.version_info[0] == 2 and sys.version_info[1] <= 6


class TestMonetDBLiteBase(object):
    def test_uninitialized(self):
        # select before init
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.sql('select * from tables')

    def test_regular_selection(self, initialize_monetdblite):
        monetdblite.sql('CREATE TABLE pylite00 (i INTEGER)')
        monetdblite.sql('INSERT INTO pylite00 VALUES (1), (2), (3), (4), (5)')
        result = monetdblite.sql('SELECT * FROM pylite00')
        assert len(result['i']) == 5, "Incorrect result"

    def test_monetdblite_create(self, initialize_monetdblite):
        monetdblite.create('pylite01', {'i': numpy.arange(100000)})
        result = monetdblite.sql('select * from pylite01')
        assert len(result['i']) == 100000, "Incorrect result"

    def test_monetdblite_insert(self, initialize_monetdblite):
        monetdblite.create('pylite02', {'i': numpy.arange(100000)})
        monetdblite.insert('pylite02', numpy.arange(100000))
        result = monetdblite.sql('select * from pylite02')
        assert len(result['i']) == 200000, "Incorrect result"

    def test_monetdblite_create_multiple_columns(self, initialize_monetdblite):
        arrays = numpy.arange(100000).reshape((5, 20000))
        monetdblite.create(
            'pylite03', {
                'i': arrays[0],
                'j': arrays[1],
                'k': arrays[2],
                'l': arrays[3],
                'm': arrays[4]
            })
        result = monetdblite.sql('select * from pylite03')
        assert len(result) == 5, "Incorrect amount of columns"
        assert len(result['i']) == 20000, "Incorrect amount of rows"

    def test_sql_types(self, initialize_monetdblite):
        monetdblite.sql('CREATE TABLE pylite04_decimal(d DECIMAL(18,3))')
        monetdblite.insert('pylite04_decimal', {'d': numpy.arange(100000)})
        result = monetdblite.sql('SELECT * FROM pylite04_decimal')
        assert result['d'][0] == 0, "Incorrect result"

        monetdblite.sql('CREATE TABLE pylite04_date(d DATE)')
        monetdblite.sql("INSERT INTO pylite04_date VALUES ('2000-01-01')")
        result = monetdblite.sql('SELECT d FROM pylite04_date')
        assert result['d'][0] == '2000-01-01', "Incorrect result"

    def test_connections(self, initialize_monetdblite):
        # create two clients
        conn = monetdblite.connectclient()
        conn2 = monetdblite.connectclient()
        # create a table within a transaction in one client
        monetdblite.sql('START TRANSACTION', client=conn)
        monetdblite.create('pylite05', {'i': numpy.arange(100000)},
                           client=conn)

        # check that table was successfully created
        result = monetdblite.sql('SELECT MIN(i) AS minimum FROM pylite05',
                                 client=conn)
        assert result['minimum'][0] == 0, "Incorrect result"
        # attempt to query the table from another client
        if not PY26:
            with pytest.raises(monetdblite.DatabaseError):
                monetdblite.sql('SELECT * FROM pylite05', client=conn2)

        # now commit the table
        monetdblite.sql('COMMIT', client=conn)
        # query the table again from the other client, this time it should be there
        result = monetdblite.sql('SELECT MIN(i) AS minimum FROM pylite05',
                                 client=conn2)
        assert result['minimum'][0] == 0, "Incorrect result"

    def test_erroneous_initialization(self):
        # init with weird argument
        with pytest.raises(Exception):
            monetdblite.init(33)

    def test_non_existent_table(self, initialize_monetdblite):
        # select from non-existent table
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.sql('select * from nonexistenttable')

    def test_invalid_connection_object(self, initialize_monetdblite):
        # invalid connection object
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.sql('select * from tables', client=33)

    def test_invalid_colnames(self, initialize_monetdblite):
        # invalid colnames
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.create('pylite06', {33: []})

    @pytest.mark.xfail(reason='Bug in upstream MonetDB')
    def test_empty_colnames(self, initialize_monetdblite):
        # empty colnames
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.create('pylite07', {'': []})

    def test_invalid_key_dict(self, initialize_monetdblite):
        # dictionary with invalid keys
        d = dict()
        d[33] = 44
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.create('pylite08', d)

    @pytest.mark.skip(reason="segfault")
    def test_missing_dict_key(self, initialize_monetdblite):
        # FIXME: segfault
        # missing dict key in insert
        monetdblite.create('pylite09', dict(a=[], b=[], c=[]))
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.insert('pylite09', dict(a=33, b=44))

    def test_bad_column_number(self, initialize_monetdblite):
        # too few columns in insert
        monetdblite.create('pylite10', dict(a=[], b=[], c=[]))
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.insert('pylite10', [[33], [44]])

    def test_many_sql_statements(self, initialize_monetdblite):
        for i in range(5):  # FIXME 1000
            conn = monetdblite.connectclient()
            monetdblite.sql('START TRANSACTION', client=conn)
            monetdblite.sql('CREATE TABLE pylite11 (i INTEGER)', client=conn)
            monetdblite.insert('pylite11', {'i': numpy.arange(10)},
                               client=conn)
            result = monetdblite.sql('SELECT * FROM pylite11', client=conn)
            assert result['i'][0] == 0, "Invalid result"
            monetdblite.sql('DROP TABLE pylite11', client=conn)
            monetdblite.sql('ROLLBACK', client=conn)
            del conn

    def test_null_string_insertion_bug(self, initialize_monetdblite):
        monetdblite.sql("CREATE TABLE pylite12 (s varchar(2))")
        monetdblite.insert('pylite12', {'s': ['a', None]})
        result = monetdblite.sql("SELECT * FROM pylite12")
        expected = numpy.ma.masked_array(['a', 'a'], mask=[0, 1])
        numpy.testing.assert_array_equal(result['s'], expected)

    def test_decimal_insertion_bug(self, initialize_monetdblite):
        monetdblite.sql("CREATE TABLE pylite13 (d DECIMAL(3, 2))")
        monetdblite.insert('pylite13', {'d': [1.3]})
        result = monetdblite.sql("SELECT * FROM pylite13")
        expected = numpy.array([1.3])
        numpy.testing.assert_array_equal(result['d'], expected)

    # This test must be executed after all others because it
    # initializes monetdblite independently out of the fixture
    # initialize_monetdblite
    @pytest.mark.xfail(reason="We should not be testing as root!")
    def test_unwriteable_dir(self):
        # init in unwritable directory
        os.mkdir('/tmp/unwriteabledir')
        os.chmod('/tmp/unwriteabledir', 0o555)
        with pytest.raises(monetdblite.DatabaseError):
            monetdblite.init('/tmp/unwriteabledir')

        monetdblite.shutdown()
        os.chmod('/tmp/unwriteabledir', 0o755)
        shutil.rmtree('/tmp/unwriteabledir')
