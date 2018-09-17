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

    def test_numpy_creation(self, monetdblite_cursor):
        # numpyarray = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=(1, 10))}  # segfaults
        data_dict = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=10)}
        monetdblite_cursor.create('numpy_creation', data_dict)
        monetdblite_cursor.commit()

        monetdblite_cursor.execute('SELECT * FROM numpy_creation')
        result = monetdblite_cursor.fetchnumpy()

        assert str(result['i']) == str(data_dict['i']), "Incorrect result returned"
        assert str(result['v']) == str(data_dict['v']), "Incorrect result returned"


    def test_pandas_creation(self, monetdblite_cursor):
        try:
            import pandas
        except:
            # no pandas, skip this test
            return
        data_dict = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=10)}
        dframe = pandas.DataFrame.from_dict(data_dict)
        monetdblite_cursor.create('dframe_creation', dframe)

        monetdblite_cursor.execute('SELECT * FROM dframe_creation')
        result = monetdblite_cursor.fetchnumpy()
        assert str(result['i']) == str(data_dict['i']), "Incorrect result returned"
        assert str(result['v']) == str(data_dict['v']), "Incorrect result returned"

    def test_numpy_insertion(self, monetdblite_cursor):
        data_dict = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=10)}
        monetdblite_cursor.execute("CREATE TABLE numpy_insertion (i INT, v INT)")
        monetdblite_cursor.insert('numpy_insertion', data_dict)
        monetdblite_cursor.commit()

        monetdblite_cursor.execute("SELECT * FROM numpy_insertion")
        result = monetdblite_cursor.fetchnumpy()

        assert str(result['i']) == str(data_dict['i']), "Incorrect result returned"
        assert str(result['v']) == str(data_dict['v']), "Incorrect result returned"

    def test_pandas_insertion(self, monetdblite_cursor):
        try:
            import pandas
        except:
            # no pandas, skip this test
            return
        data_dict = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=10)}
        dframe = pandas.DataFrame.from_dict(data_dict)
        monetdblite_cursor.execute("CREATE TABLE pandas_insertion (i INT, v INT)")
        monetdblite_cursor.insert('pandas_insertion', dframe)
        monetdblite_cursor.commit()

        monetdblite_cursor.execute("SELECT * FROM pandas_insertion")
        result = monetdblite_cursor.fetchnumpy()

        assert str(result['i']) == str(data_dict['i']), "Incorrect result returned"
        assert str(result['v']) == str(data_dict['v']), "Incorrect result returned"
