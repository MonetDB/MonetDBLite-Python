# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.  If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright 1997 - July 2008 CWI, August 2008 - 2019 MonetDB B.V.
import numpy


class TestDescription(object):
    def test_description(self, monetdblite_cursor):
        monetdblite_cursor.execute('select * from sys.tables')
        assert monetdblite_cursor.description is not None

    def test_description_fields(self, monetdblite_cursor):
        monetdblite_cursor.execute('select name from sys.tables')
        assert monetdblite_cursor.description[0][0] == "name"
        assert monetdblite_cursor.description[0][1] == numpy.dtype('O')
