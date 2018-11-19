# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.  If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright 1997 - July 2008 CWI, August 2008 - 2016 MonetDB B.V.

import tempfile
import pytest

import monetdblite


class TestPEP249Compliance(object):
    def test_globals(self):
        assert monetdblite.apilevel == "2.0"
        assert monetdblite.threadsafety == 0
        assert monetdblite.paramstyle == "pyformat"

    def test_commit_after_close(self, raw_connection):
        connection = raw_connection[0]
        connection.close()
        with pytest.raises(monetdblite.ProgrammingError):
            connection.commit()

    def test_rollback_after_close(self, raw_connection):
        connection = raw_connection[0]
        connection.close()
        with pytest.raises(monetdblite.ProgrammingError):
            connection.rollback()

    def test_cursor_after_close(self, raw_connection):
        connection = raw_connection[0]
        connection.close()
        with pytest.raises(monetdblite.ProgrammingError):
            connection.cursor()

    def test_closing_rolls_back_changes(self, raw_connection):
        connection = raw_connection[0]
        cursor = connection.cursor()
        # Make changes but don't commit them
        cursor.execute("CREATE TABLE test_tbl (i INTEGER)")
        cursor.execute("INSERT INTO test_tbl VALUES (1), (2), (3)")
        connection.close()

        # Open a new connection
        connection = monetdblite.connect(raw_connection[1])
        cursor = connection.cursor()
        with pytest.raises(monetdblite.DatabaseError):
            cursor.execute("SELECT * FROM test_tbl")

        connection.close()
