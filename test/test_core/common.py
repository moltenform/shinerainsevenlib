
import pytest
import tempfile
from src.shinerainsoftsevenutil.standard import *


@pytest.fixture()
def fixture_dir():
    basedir = files.join(tempfile.gettempdir(), 'shinerainsoftseven_test', 'empty')
    files.ensureEmptyDirectory(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)


