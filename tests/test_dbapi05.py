import monetdblitetest
import monetdblite
import numpy
import unittest


class DescriptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dbfarm = monetdblitetest.tempdir()
        cls.conn = monetdblite.connect(dbfarm)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        monetdblitetest.cleantempdir()

    def setUp(self):
        self.cursor = self.conn.cursor()

    def test_description(self):
        self.cursor.execute('select * from sys.tables')
        self.assertNotEqual(self.cursor.description, None)

    def test_description_fields(self):
        self.cursor.execute('select name from sys.tables')
        self.assertEqual(self.cursor.description[0][0], "name")
        self.assertEqual(self.cursor.description[0][1], numpy.dtype('O'))
