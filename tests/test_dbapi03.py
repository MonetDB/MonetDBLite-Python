# test database shutdown/startup

import monetdblite
import sys
import pytest


PY26 = sys.version_info[0] == 2 and sys.version_info[1] <= 6

identifier_escape = monetdblite.monetize.monet_identifier_escape


class TestShutdown(object):
    def test_commited_on_restart(self, monetdblite_cursor_autocommit):
        (cursor, connection, dbfarm) = monetdblite_cursor_autocommit
        cursor.transaction()
        cursor.execute('CREATE TABLE integers (i INTEGER)')
        cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(3)])
        cursor.execute('SELECT * FROM integers')
        result = cursor.fetchall()
        assert result == [[0], [1], [2]], "Incorrect result returned"
        cursor.commit()
        connection.close()

        connection = monetdblite.make_connection(dbfarm)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM integers')
        assert result == [[0], [1], [2]], "Incorrect result returned"

    def test_transaction_aborted_on_shutdown(self, monetdblite_cursor_autocommit):
        (cursor, connection, dbfarm) = monetdblite_cursor_autocommit
        cursor.transaction()
        cursor.execute('CREATE TABLE integers (i INTEGER)')
        cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(3)])
        cursor.execute('SELECT * FROM integers')
        result = cursor.fetchall()
        assert result == [[0], [1], [2]], "Incorrect result returned"
        connection.close()

        connection = monetdblite.make_connection(dbfarm)
        cursor = connection.cursor()
        if not PY26:
            with pytest.raises(monetdblite.DatabaseError):
                cursor.execute('SELECT * FROM integers')

    def test_many_shutdowns(self, monetdblite_cursor_autocommit):
        (cursor, connection, dbfarm) = monetdblite_cursor_autocommit
        for i in range(10):
            cursor.transaction()
            cursor.execute('CREATE TABLE integers (i INTEGER)')
            cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(10)])
            cursor.execute('SELECT MIN(i * 3 + 5) FROM integers')
            result = cursor.fetchall()
            assert result == [[5]], "Incorrect result returned"
            connection.close()

            connection = monetdblite.make_connection(dbfarm)
            connection.set_autocommit(True)
            cursor = connection.cursor()

    def test_fetchone_without_executing_raises(self, monetdblite_empty_cursor):
        with pytest.raises(monetdblite.exceptions.ProgrammingError):
            monetdblite_empty_cursor.fetchone()

    def test_fetchall_without_executing_raises(self, monetdblite_empty_cursor):
        with pytest.raises(monetdblite.exceptions.ProgrammingError):
            monetdblite_empty_cursor.fetchall()

    def test_fetchnumpy_without_executing_raises(self, monetdblite_empty_cursor):
        with pytest.raises(monetdblite.exceptions.ProgrammingError):
            monetdblite_empty_cursor.fetchnumpy()

    def test_fetchdf_without_executing_raises(self, monetdblite_empty_cursor):
        with pytest.raises(monetdblite.exceptions.ProgrammingError):
            monetdblite_empty_cursor.fetchdf()

    def test_execute_with_closed_cursor_raises(self, monetdblite_empty_cursor):
        monetdblite_empty_cursor.close()
        with pytest.raises(monetdblite.exceptions.ProgrammingError):
            monetdblite_empty_cursor.execute("SELECT * FROM _tables")

    def test_fetchmany(self, monetdblite_cursor):
        monetdblite_cursor.execute("SELECT * FROM integers")

        counter = 0
        while counter < 10:
            r = monetdblite_cursor.fetchmany(2)
            assert len(r) == 2
            counter += len(r)

        assert counter == 10

    def test_fetchmany_without_explicit_size(self, monetdblite_cursor):
        assert monetdblite_cursor.arraysize == 1, "Incorrect default value for cursor.arraysize"
        monetdblite_cursor.arraysize = 2
        monetdblite_cursor.execute("SELECT * FROM integers")

        counter = 0
        while counter < 10:
            r = monetdblite_cursor.fetchmany()
            assert len(r) == 2
            counter += len(r)

        assert counter == 10

    def test_scroll(self, monetdblite_cursor):
        monetdblite_cursor.execute("SELECT * FROM integers")
        monetdblite_cursor.scroll(5)

        x = monetdblite_cursor.fetchone()
        assert x[0] == 6

    def test_scroll_raises_for_incorrect_mode(self, monetdblite_cursor):
        monetdblite_cursor.execute("SELECT * FROM integers")
        with pytest.raises(monetdblite.exceptions.ProgrammingError):
            monetdblite_cursor.scroll(5, mode='abc')

    def test_scroll_raises_for_out_of_bounds_offset(self, monetdblite_cursor):
        monetdblite_cursor.execute("SELECT * FROM integers")
        with pytest.raises(IndexError):
            monetdblite_cursor.scroll(20)

    # TODO: rewrite this one
    # def test_use_old_cursor(self, monetdblite_cursor):
    #     self.connection.close()

    #     self.connection = monetdblite.connect(self.dbfarm)
    #     if not PY26:
    #         with self.assertRaises(monetdblite.ProgrammingError):
    #             monetdblite_cursor.execute('SELECT * FROM integers')
