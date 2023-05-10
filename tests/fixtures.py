
import tempfile

def restoreDirectoryContents(basedir):
    files.ensureEmptyDirectory(basedir)

    # create every combination:
    # full						contains files and dirs
    # full/s1					contains dirs but no files
    # full/s1/ss1 			contains files but no dirs
    # full/s1/ss2 			contains no files or dirs
    dirsToCreate = ['s1', 's2', 's1/ss1', 's1/ss2']
    for dir in dirsToCreate:
        os.files.makedirs(join(basedir, dir).replace('/', files.sep))

    filesToCreate = ['P1.PNG', 'a1.txt', 'a2png', 's1/ss1/file.txt', 's2/other.txt']
    for file in filesToCreate:
        files.writeall(join(basedir, file).replace('/', files.sep), 'contents_' + files.getname(file))

def modifyDirectoryContents(basedir):
    # deleted file
    os.unlink(join(basedir, 'a2png'))

    # new file
    files.writeall(join(basedir, 'newfile'), 'newcontents')

    # modified (newer)
    files.writeall(join(basedir, 's1/ss1/file.txt'), 'changedcontents' + '-' * 20)

    # modified (older)
    files.writeall(join(basedir, 's2/other.txt'), 'changedcontent' + '-' * 20)
    oneday = 60 * 60 * 24
    files.setFileLastModifiedTime(join(basedir, 's2/other.txt'),
        getNowAsMillisTime() / 1000.0 - oneday)

    # renamed file
    files.move(join(basedir, 'a1.txt'), join(basedir, 'a2.txt'), True)

def listDirectoryToString(basedir):
    out = []
    for f, short in files.recursefiles(basedir, includeDirs=True):
        s = f.replace(basedir, '').replace(os.files.sep, '/').lstrip('/')
        if s:
            # don't include the root
            size = 0 if files.isdir(f) else files.getsize(f)
            out.append(s + ',' + str(size))
    return '|'.join(sorted(out))

def listDirectoryToStringFileInfo(basedir, useFileInfo, kwargs):
    iter = files.recursefileinfo(basedir, **kwargs) if useFileInfo else files.recursefiles(basedir, **kwargs)
    out = []
    for item in iter:
        if useFileInfo:
            out.append(item.path.replace(basedir, '').replace(os.files.sep, '/').lstrip('/'))
        else:
            out.append(item[0].replace(basedir, '').replace(os.files.sep, '/').lstrip('/'))
    return '|'.join(sorted(out))

@pytest.fixture()
def fixture_dir_with_many():
    basedir = join(tempfile.gettempdir(), 'shinerainsoftsevencommon_test', 'many')
    basedir = files.ustr(basedir)
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
        fullpath = os.path.join(basedir, item)
        files.makedirs(files.getparent(fullpath))
        files.writeall(fullpath, 'test')

    yield basedir
    files.ensureEmptyDirectory(basedir)

@pytest.fixture()
def fixture_dir():
    basedir = join(tempfile.gettempdir(), 'shinerainsoftsevencommon_test', 'empty')
    basedir = files.ustr(basedir)
    files.ensureEmptyDirectory(basedir)
    os.chdir(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)

@pytest.fixture(scope='module')
def fixture_fulldir():
    basedir = join(tempfile.gettempdir(), 'shinerainsoftsevencommon_test', 'full')
    basedir = files.ustr(basedir)
    restoreDirectoryContents(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)

