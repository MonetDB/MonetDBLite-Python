import numpy


class TestDescription(object):
    def test_description(self, monetdblite_cursor):
        monetdblite_cursor.execute('select * from sys.tables')
        assert monetdblite_cursor.description is not None

    def test_description_fields(self, monetdblite_cursor):
        monetdblite_cursor.execute('select name from sys.tables')
        assert monetdblite_cursor.description[0][0] == "name"
        assert monetdblite_cursor.description[0][1] == numpy.dtype('O')
