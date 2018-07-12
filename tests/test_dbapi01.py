# multiple result sets

import monetdblitetest
import monetdblite
import numpy
import unittest


class MultipleResultSets(unittest.TestCase):
    def setup_method(self, method):
        dbfarm = monetdblitetest.tempdir()
        self.connection = monetdblite.connect(dbfarm)
        self.cursor = self.connection.cursor()
        self.cursor.create('integers', {'i': numpy.arange(10)})

    def teardown_method(self, method):
        self.connection.close()
        monetdblitetest.cleantempdir()

    def test_regular_selection(self):
        self.cursor.execute('SELECT * FROM integers')
        self.cursor.execute('SELECT * FROM integers')
        result = self.cursor.fetchall()
        self.assertEqual(result, [[0],[1],[2],[3],[4],[5],[6],[7],[8],[9]],
            "Incorrect result returned")

    def test_numpy_selection(self):
        self.cursor.execute('SELECT * FROM integers')
        self.cursor.execute('SELECT * FROM integers')
        result = self.cursor.fetchnumpy()
        self.assertEqual(str(result), str({'i': numpy.ma.masked_array(numpy.arange(10))}),
            "Incorrect result returned")


if __name__ == '__main__':
    unittest.main()
