
import tempfile
import os



@pytest.fixture()
def fixtureFileTree():
    basedir = join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'many')
    basedir = ustr(basedir)
    files.ensureEmptyDirectory(basedir)
    lst = [
        'fb/a/fb/a.txt',
        'fb/a/fb/b.txt',
        'fb/a/fb/c/c0.txt',
        'fb/a/fb/c/c1.txt',
        'fb/a/bz/aa.txt',
        'fb/a/bz/bb.txt',
        'fb/a/bz/fb/cc.txt',
        'fb/a/bz/zz.txt',
        'fb/a/r1.txt',
        'fb/fb/cc.txt',
        'fb/r2.txt',
        'r3.txt'
    ]
    for item in lst:
        fullpath = os.path.join(basedir, item)
        files.makeDirs(files.getParent(fullpath))
        files.writeAll(fullpath, 'test')

    yield basedir
    files.ensureEmptyDirectory(basedir)

@pytest.fixture()
def fxDirPlain():
    basedir = join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'empty')
    basedir = ustr(basedir)
    files.ensureEmptyDirectory(basedir)
    os.chdir(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)


