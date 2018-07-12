# test proper escaping

import monetdblitetest
import monetdblite
import numpy
import unittest

identifier_escape = monetdblite.monetize.monet_identifier_escape


class MultipleResultSets(unittest.TestCase):
    def setUp(self):
        dbfarm = monetdblitetest.tempdir()
        self.connection = monetdblite.connect(dbfarm)
        self.cursor = self.connection.cursor()
        self.cursor.create('integers', {'i': numpy.arange(10)})

    def tearDown(self):
        self.connection.close()
        monetdblitetest.cleantempdir()

    def test_string_insertion(self):
        self.cursor.execute('CREATE TABLE strings(s STRING)')
        self.cursor.executemany('INSERT INTO strings VALUES (%s)', ["'hello\" world\"'"])
        self.cursor.execute('SELECT * FROM strings')
        result = self.cursor.fetchall()
        self.assertEqual(result, [["'hello\" world\"'"]],
                         "Incorrect result returned")

    def test_table_name(self):
        sname = "table"
        tname = 'integer'
        self.cursor.execute('CREATE SCHEMA %s' % identifier_escape(sname))
        self.cursor.create(tname, {'i': numpy.arange(3)}, schema=sname)
        self.cursor.execute('SELECT * FROM %s.%s' % (identifier_escape(sname), identifier_escape(tname)))
        result = self.cursor.fetchall()
        self.assertEqual(result, [[0],[1],[2]],
                         "Incorrect result returned")


if __name__ == '__main__':
    unittest.main()
