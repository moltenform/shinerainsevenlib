

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

@pytest.fixture()
def fixture_dir_with_many():
    basedir = files.join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'many')
    files.ensureEmptyDirectory(basedir)
    lst = [
        'foobar/a/foobar/a.txt',
        'foobar/a/foobar/b.txt',
        'foobar/a/foobar/c/c0.txt',
        'foobar/a/foobar/c/c1.txt',
        'foobar/a/baz/aa.txt',
        'foobar/a/baz/bb.txt',
        'foobar/a/baz/foobar/cc.txt',
        'foobar/a/baz/zz.txt',
        'foobar/a/r1.txt',
        'foobar/foobar/cc.txt',
        'foobar/r2.txt',
        'r3.txt'
    ]
    for item in lst:
        fullpath = files.join(basedir, item)
        files.makeDirs(files.getParent(fullpath))
        files.writeAll(fullpath, 'test')

    yield basedir
    files.ensureEmptyDirectory(basedir)

def fileInfoListToList(root, incoming):
    """Supports files.recurseFiles, files.recurseDirs, files.recurseFileInfo
    truncates the absolute path to a relative path for easy comparison."""
    if callable(incoming):
        incoming = incoming(root)
    
    result = [o for o in incoming]
    if isinstance(result[0], tuple):
        result = [o[0] for o in result]
    else:
        # this came from recurseFileInfo
        result = [o.path for o in result]

    result = [srss.replaceMustExist(s, root, '') for s in result]
    result = [s.replace('\\', '/') for s in result]
    return result

