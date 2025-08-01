

import pytest
import tempfile
from src.shinerainsevenlib.standard import *


@pytest.fixture()
def fixture_dir():
    "A fixture providing a empty directory for testing."
    basedir = files.join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'empty')
    files.ensureEmptyDirectory(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)


