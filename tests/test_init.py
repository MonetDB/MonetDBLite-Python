import os
import shutil
import tempfile
import monetdblite as mdbl
import pytest


class TestInitialization(object):
    def test_double_initialization(self, initialize_monetdblite):
        with pytest.raises(mdbl.exceptions.DatabaseError):
            mdbl.init(initialize_monetdblite)

    def test_relative_initialization(self):
        tmpdir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            mdbl.init("./relative_path")
        except Exception:
            mdbl.shutdown()
            shutil.rmtree(tmpdir)
            assert False

        res = mdbl.sql("SELECT id FROM _tables limit 10")
        mdbl.shutdown()
        os.chdir(cwd)
        shutil.rmtree(tmpdir)

        assert len(res.get('id')) == 10
