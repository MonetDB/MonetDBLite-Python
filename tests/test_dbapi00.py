#simple DB API testcase

import numpy
import pytest
import tempfile
import monetdblite as mdbl


class TestSimpleDBAPI(object):
    def test_double_initialization(self):
        dbdir = tempfile.mkdtemp()
        mdbl.init(dbdir)
        with pytest.raises(mdbl.exceptions.DatabaseError):
            mdbl.init(dbdir)
        mdbl.shutdown()

    def test_regular_selection(self, monetdblite_cursor):
        monetdblite_cursor.execute('SELECT * FROM integers')
        result = monetdblite_cursor.fetchall()
        assert result == [[0],[1],[2],[3],[4],[5],[6],[7],[8],[9], [None]], "Incorrect result returned"

    def test_numpy_selection(self, monetdblite_cursor):
        monetdblite_cursor.execute('SELECT * FROM integers')
        result = monetdblite_cursor.fetchnumpy()
        arr = numpy.ma.masked_array(numpy.arange(11))
        arr.mask = [False] * 10 + [True]
        arr = {'i': arr}
        assert str(result) == str(arr), "Incorrect result returned"

    def test_pandas_selection(self, monetdblite_cursor):
        try:
            import pandas
        except:
            # no pandas, skip this test
            return
        monetdblite_cursor.execute('SELECT * FROM integers')
        result = monetdblite_cursor.fetchdf()
        arr = numpy.ma.masked_array(numpy.arange(11))
        arr.mask = [False] * 10 + [True]
        arr = {'i': arr}
        arr = pandas.DataFrame.from_dict(arr)
        assert str(result) == str(arr), "Incorrect result returned"
