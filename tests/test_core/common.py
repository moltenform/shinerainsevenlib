

import pytest
import tempfile
from src.shinerainsevenlib.standard import *


@pytest.fixture()
def fxDirPlain():
    "A fixture providing a empty directory for testing."
    basedir = files.join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'empty')
    files.ensureEmptyDirectory(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)

def _fxTreeImpl():
    basedir = files.join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'tree')
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
    return basedir

@pytest.fixture()
def fxTree():
    basedir = _fxTreeImpl()
    ret = Bucket(basedir=basedir)
    ret.pathSmallFile = basedir + '/r3.txt'
    ret.pathFileExists = basedir + '/foobar/a/foobar/c/c0.txt'
    ret.pathFileToLock = basedir + '/foobar/a/foobar/c/c1.txt'
    ret.pathNotExist = basedir + '/notexist.txt'
    ret.pathDir = basedir + '/foobar/a/foobar'
    ret.pathFewChildren = basedir + '/foobar/foobar'
    ret.pathManyChildren = basedir + '/foobar/a/foobar'
    ret.pathDirNotExist = basedir + '/newdir'
    yield ret
    files.ensureEmptyDirectory(basedir)

@pytest.fixture()
def fxTreePlain():
    basedir = _fxTreeImpl()
    yield basedir
    files.ensureEmptyDirectory(basedir)

def _fxFilesImpl():
    basedir = files.join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'files')
    files.ensureEmptyDirectory(basedir)
    lst = [
        'a1.txt',
        'bb2.txt',
        'ccc3.txt',
        'd4.txt',
        'ee5.txt',
        u'1\u1101.txt',
        u'2\u1101.txt',
    ]
    for item in lst:
        # contents are like the filname without the txt
        fullpath = files.join(basedir, item)
        files.writeAll(fullpath, item.replace('.txt', ''))

    return basedir

@pytest.fixture()
def fxFiles():
    basedir = _fxFilesImpl()
    ret = Bucket(basedir=basedir)
    ret.f1 = basedir + '/1\u1101.txt'
    ret.f2 = basedir + '/2\u1101.txt'
    ret.f3notExistYet = basedir + '/3\u1101.txt'
    yield ret
    files.ensureEmptyDirectory(basedir)

@pytest.fixture()
def fxFilesPlain():
    basedir = _fxFilesImpl()
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
    result.sort() # important for non-windows platforms
    return result

