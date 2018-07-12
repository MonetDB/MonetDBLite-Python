# test database shutdown/startup

import monetdblitetest
import monetdblite
import numpy
import unittest
import sys


PY26 = sys.version_info[0] == 2 and sys.version_info[1] <= 6

identifier_escape = monetdblite.monetize.monet_identifier_escape


class ShutdownTests(unittest.TestCase):
    def setUp(self):
        self.dbfarm = monetdblitetest.tempdir()
        self.connection = monetdblite.connect(self.dbfarm)
        self.cursor = self.connection.cursor()
        self.connection.set_autocommit(True)

    def tearDown(self):
        self.connection.close()
        monetdblitetest.cleantempdir()

    def test_commited_on_restart(self):
        self.cursor.transaction()
        self.cursor.execute('CREATE TABLE integers (i INTEGER)')
        self.cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(3)])
        self.cursor.execute('SELECT * FROM integers')
        result = self.cursor.fetchall()
        self.assertEqual(result, [[0],[1],[2]], 
            "Incorrect result returned")
        self.cursor.commit()
        self.connection.close()

        self.connection = monetdblite.connect(self.dbfarm)
        self.cursor = self.connection.cursor()
        self.cursor.execute('SELECT * FROM integers')
        self.assertEqual(result, [[0],[1],[2]], 
            "Incorrect result returned")

    def test_transaction_aborted_on_shutdown(self):
        self.cursor.transaction()
        self.cursor.execute('CREATE TABLE integers (i INTEGER)')
        self.cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(3)])
        self.cursor.execute('SELECT * FROM integers')
        result = self.cursor.fetchall()
        self.assertEqual(result, [[0],[1],[2]], 
            "Incorrect result returned")
        self.connection.close()

        self.connection = monetdblite.connect(self.dbfarm)
        self.cursor = self.connection.cursor()
        if not PY26:
            with self.assertRaises(monetdblite.DatabaseError):
                self.cursor.execute('SELECT * FROM integers')


    def test_many_shutdowns(self):
        for i in range(10):
            self.cursor.transaction()
            self.cursor.execute('CREATE TABLE integers (i INTEGER)')
            self.cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(10)])
            self.cursor.execute('SELECT MIN(i * 3 + 5) FROM integers')
            result = self.cursor.fetchall()
            self.assertEqual(result, [[5]], 
                "Incorrect result returned")
            self.connection.close()

            self.connection = monetdblite.connect(self.dbfarm)
            self.connection.set_autocommit(True)
            self.cursor = self.connection.cursor()

    def test_use_old_cursor(self):
        self.connection.close()

        self.connection = monetdblite.connect(self.dbfarm)
        if not PY26:
            with self.assertRaises(monetdblite.ProgrammingError):
                self.cursor.execute('SELECT * FROM integers')


if __name__ == '__main__':
    unittest.main()
