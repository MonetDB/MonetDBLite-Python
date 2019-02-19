# test proper escaping

import monetdblite
import numpy

identifier_escape = monetdblite.monetize.monet_identifier_escape


class TestMultipleResultSets(object):
    def test_string_insertion(self, monetdblite_cursor):
        monetdblite_cursor.execute('CREATE TABLE strings(s STRING)')
        monetdblite_cursor.executemany('INSERT INTO strings VALUES (%s)', ["'hello\" world\"'"])
        monetdblite_cursor.execute('SELECT * FROM strings')
        result = monetdblite_cursor.fetchall()
        assert result == [["'hello\" world\"'"]], "Incorrect result returned"

    def test_table_name(self, monetdblite_cursor):
        sname = "table"
        tname = 'integer'
        monetdblite_cursor.execute('CREATE SCHEMA %s' % identifier_escape(sname))
        monetdblite_cursor.create(tname, {'i': numpy.arange(3)}, schema=sname)
        monetdblite_cursor.execute('SELECT * FROM %s.%s' % (identifier_escape(sname), identifier_escape(tname)))
        result = monetdblite_cursor.fetchall()
        assert result == [[0],[1],[2]], "Incorrect result returned"
