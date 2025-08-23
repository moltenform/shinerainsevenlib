# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pytest
import tempfile
import os
import sys
from os.path import join
from ..common_util import isPy3OrNewer
from ..common_higher import getNowAsMillisTime


    






@pytest.fixture()
def fxDirPlain():
    basedir = join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'empty')
    ensureEmptyDirectory(basedir)
    chDir(basedir)
    yield basedir
    ensureEmptyDirectory(basedir)

@pytest.fixture(scope='module')
def fxFullDirPlain():
    basedir = join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'full')
    restoreDirectoryContents(basedir)
    yield basedir
    ensureEmptyDirectory(basedir)

