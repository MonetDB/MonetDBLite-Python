# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.  If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright 1997 - July 2008 CWI, August 2008 - 2019 MonetDB B.V.

from monetdblite import cursors
from monetdblite import exceptions
from monetdblite import embeddedmonetdb


class Connection(object):
    """A MonetDBLite SQL database connection"""
    def __init__(self, database=None, autocommit=False):
        """ Initializes the MonetDBLite database.
        args:
            database (str): path to the database directory
            autocommit (bool):  enable/disable auto commit (default: False)

        returns:
            Connection object
        """
        global MONETDBLITE_CURRENT_DATABASE
        if database is None:
            if not embeddedmonetdb.is_initialized():
                raise exceptions.ProgrammingError("No database supplied and MonetDBLite was not initialized")
        elif database != embeddedmonetdb.dbpath():
            if embeddedmonetdb.is_initialized():
                raise exceptions.ProgrammingError("MonetDBLite is already initialized. Close the previous connection first.")
            embeddedmonetdb.init(database)
            MONETDBLITE_CURRENT_DATABASE = database

        self.__monetdblite_connection = embeddedmonetdb.connect()
        self.set_autocommit(autocommit)
        self.replysize = 1
        self.__cursors = []

    def close(self):
        """Close the connection now (rather than whenever .__del__() is called).

The connection will be unusable from this point forward; a
ProgrammingError exception will be raised if any operation is
attempted with the connection. The same applies to all cursor objects
trying to use the connection. Note that closing a connection without
committing the changes first will cause an implicit rollback to be
performed.

        """
        for cursor in self.__cursors:
            cursor.close()
        self.__cursors = []
        embeddedmonetdb.shutdown()

    def commit(self):
        """Commit any pending transaction to the database.

Note that if the database supports an auto-commit feature, this must
be initially off. An interface method (autocommit) may be provided to
turn it back on.

        """
        if not embeddedmonetdb.is_initialized():
            raise exceptions.ProgrammingError("Connection not initialized")
        embeddedmonetdb.sql('COMMIT', self.__monetdblite_connection)

    def rollback(self):
        if not embeddedmonetdb.is_initialized():
            raise exceptions.ProgrammingError("Connection not initialized")
        embeddedmonetdb.sql('ROLLBACK', self.__monetdblite_connection)

    def cursor(self):
        if not embeddedmonetdb.is_initialized():
            raise exceptions.ProgrammingError("This connection has not been initialized or has been closed")
        cursor = cursors.Cursor(self)
        self.__cursors.append(cursor)
        return cursor

    # MonetDB specific API
    # TODO: rename this method to "autocommit"
    def set_autocommit(self, autocommit):
        """Set the autocommit on or off

Toggle autocommit, on or off. The value `autocommit` should be `True` or
`False`. By default autocommit is off (See PEP249).

        """
        embeddedmonetdb.set_autocommit(autocommit, self.__monetdblite_connection)

    def remove_cursor(self, cursor):
        self.__cursors.remove(cursor)

    def transaction(self):
        embeddedmonetdb.sql('START TRANSACTION', self.__monetdblite_connection)

    def execute(self, query):
        return embeddedmonetdb.sql(query, self.__monetdblite_connection)

    def get_connection(self):
        return self.__monetdblite_connection
