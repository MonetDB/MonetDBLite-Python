# multiple result sets

import numpy


class MultipleResultSets(object):
    def test_regular_selection(self, monetdblite_cursor):
        monetdblite_cursor.execute('SELECT * FROM integers')
        monetdblite_cursor.execute('SELECT * FROM integers')
        result = monetdblite_cursor.fetchall()
        assert result == [[0],[1],[2],[3],[4],[5],[6],[7],[8],[9]], "Incorrect result returned"

    def test_numpy_selection(self, monetdblite_cursor):
        monetdblite_cursor.execute('SELECT * FROM integers')
        monetdblite_cursor.execute('SELECT * FROM integers')
        result = monetdblite_cursor.fetchnumpy()
        assert str(result) == str({'i': numpy.ma.masked_array(numpy.arange(10))}), "Incorrect result returned"
