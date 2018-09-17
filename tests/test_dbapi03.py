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

    # TODO: rewrite this one
    # def test_use_old_cursor(self, monetdblite_cursor):
    #     self.connection.close()

    #     self.connection = monetdblite.connect(self.dbfarm)
    #     if not PY26:
    #         with self.assertRaises(monetdblite.ProgrammingError):
    #             monetdblite_cursor.execute('SELECT * FROM integers')
