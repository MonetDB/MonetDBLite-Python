
#simple DB API testcase

import monetdblitetest
import monetdblite
import numpy
import unittest

class SimpleDBAPITest(unittest.TestCase):
    def setUp(self):
        global conn, c
        conn = monetdblite.connect(':memory:')
        c = conn.cursor()
        c.create('integers', {'i': numpy.arange(10)})
        c.execute('INSERT INTO integers VALUES (NULL)')

    def tearDown(self):
        conn.close()

    def test_regular_selection(self):
        c.execute('SELECT * FROM integers')
        result = c.fetchall()
        self.assertEqual(result, [[0],[1],[2],[3],[4],[5],[6],[7],[8],[9], [None]], 
            "Incorrect result returned")

if __name__ == '__main__':
    unittest.main()
