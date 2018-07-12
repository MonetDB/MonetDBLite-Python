import os
import shutil
import tempfile

TEST_DBFARM = tempfile.mkdtemp()

def tempdir():
        global TEST_DBFARM
        if os.path.isdir(TEST_DBFARM):
                shutil.rmtree(TEST_DBFARM)
        TEST_DBFARM = tempfile.mkdtemp()
        return TEST_DBFARM


def cleantempdir():
        shutil.rmtree(TEST_DBFARM)
