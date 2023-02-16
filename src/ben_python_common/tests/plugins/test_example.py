# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pytest
import tempfile
import os
from ... import files

class TestExample(object):
    def test_addition(self):
        n = 1 + 1
        assert n == 2

    def test_assertFloatNotEqualNegative(self):
        with pytest.raises(ValueError):
            int('abc')

@pytest.fixture()
def fixture_dir():
    basedir = os.path.join(tempfile.gettempdir(), 'ben_python_common_test', 'empty')
    basedir = files.ustr(basedir)
    files.ensureEmptyDirectory(basedir)
    os.chdir(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)

