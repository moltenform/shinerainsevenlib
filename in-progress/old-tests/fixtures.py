
import tempfile
import os

def restoreDirectoryContents(basedir):
    

def modifyDirectoryContents(basedir):
    # deleted file
    os.unlink(join(basedir, 'a2png'))

    # new file
    files.writeAll(join(basedir, 'newfile'), 'newcontents')

    # modified (newer)
    files.writeAll(join(basedir, 's1/ss1/file.txt'), 'changedcontents' + '-' * 20)

    # modified (older)
    files.writeAll(join(basedir, 's2/other.txt'), 'changedcontent' + '-' * 20)
    oneday = 60 * 60 * 24
    files.setLastModTime(join(basedir, 's2/other.txt'),
        getNowAsMillisTime() / 1000.0 - oneday)

    # renamed file
    files.move(join(basedir, 'a1.txt'), join(basedir, 'a2.txt'), True)

def listDirectoryToString(basedir):
    out = []
    for f, short in files.recurseFiles(basedir, includeDirs=True):
        s = f.replace(basedir, '').replace(os.files.sep, '/').lstrip('/')
        if s:
            # don't include the root
            size = 0 if files.isDir(f) else files.getSize(f)
            out.append(s + ',' + str(size))
    return '|'.join(sorted(out))

def listDirectoryToStringFileInfo(basedir, useFileInfo, kwargs):
    iter = files.recurseFileInfo(basedir, **kwargs) if useFileInfo else files.recurseFiles(basedir, **kwargs)
    out = []
    for item in iter:
        if useFileInfo:
            out.append(item.path.replace(basedir, '').replace(os.files.sep, '/').lstrip('/'))
        else:
            out.append(item[0].replace(basedir, '').replace(os.files.sep, '/').lstrip('/'))
    return '|'.join(sorted(out))

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
def fixtureDir():
    basedir = join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'empty')
    basedir = ustr(basedir)
    files.ensureEmptyDirectory(basedir)
    os.chdir(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)


