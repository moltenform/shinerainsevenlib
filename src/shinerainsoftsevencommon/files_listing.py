
# allowedexts in the form ['png', 'gif']
def _listchildrenUnsorted(dir, *, filenamesOnly=False, allowedexts=None):
    for filename in _os.listdir(dir):
        if not allowedexts or getext(filename) in allowedexts:
            yield filename if filenamesOnly else (dir + _os.path.sep + filename, filename)


if sys.platform.startswith('win'):
    exeSuffix = '.exe'
    listchildren = _listchildrenUnsorted
else:
    exeSuffix = ''
    def listchildren(*args, **kwargs):
        return sorted(_listchildrenUnsorted(*args, **kwargs))

def listdirs(dir, *, filenamesOnly=False, allowedexts=None):
    for full, name in listchildren(dir, allowedexts=allowedexts):
        if _os.path.isdir(full):
            yield name if filenamesOnly else (full, name)

def listfiles(dir, *, filenamesOnly=False, allowedexts=None):
    for full, name in listchildren(dir, allowedexts=allowedexts):
        if not _os.path.isdir(full):
            yield name if filenamesOnly else (full, name)

def recursefiles(root, *, filenamesOnly=False, allowedexts=None,
        fnFilterDirs=None, includeFiles=True, includeDirs=False, topdown=True, followSymlinks=False):
    assert isdir(root)

    for (dirpath, dirnames, filenames) in _os.walk(root, topdown=topdown, followlinks=followSymlinks):
        if fnFilterDirs:
            newdirs = [dir for dir in dirnames if fnFilterDirs(join(dirpath, dir))]
            dirnames[:] = newdirs

        if includeFiles:
            for filename in (filenames if sys.platform.startswith('win') else sorted(filenames)):
                if not allowedexts or getext(filename) in allowedexts:
                    yield filename if filenamesOnly else (dirpath + _os.path.sep + filename, filename)

        if includeDirs:
            yield getname(dirpath) if filenamesOnly else (dirpath, getname(dirpath))

def recursedirs(root, *, filenamesOnly=False, fnFilterDirs=None,
        topdown=True, followSymlinks=False):
    return recursefiles(root, filenamesOnly=filenamesOnly, fnFilterDirs=fnFilterDirs, includeFiles=False,
        includeDirs=True, topdown=topdown, followSymlinks=followSymlinks)

class FileInfoEntryWrapper(object):
    def __init__(self, obj):
        self.obj = obj
        self.path = obj.path

    def is_dir(self, *args):
        return self.obj.is_dir(*args)

    def is_file(self, *args):
        return self.obj.is_file(*args)

    def short(self):
        return _os.path.split(self.path)[1]

    def size(self):
        return self.obj.stat().st_size

    def mtime(self):
        return self.obj.stat().st_mtime

    def metadatachangetime(self):
        assertTrue(not sys.platform.startswith('win'))
        return self.obj.stat().st_ctime

    def createtime(self):
        assertTrue(sys.platform.startswith('win'))
        return self.obj.stat().st_ctime

def recursefileinfo(root, recurse=True, followSymlinks=False, filesOnly=True,
        fnFilterDirs=None, fnDirectExceptionsTo=None):
    assertTrue(isPy3OrNewer)

    # scandir's resources are released in destructor,
    # do not create circular references holding it
    for entry in _os.scandir(root):
        if entry.is_dir(follow_symlinks=followSymlinks):
            if not filesOnly:
                yield FileInfoEntryWrapper(entry)
            if recurse and (not fnFilterDirs or fnFilterDirs(entry.path)):
                try:
                    for subentry in recursefileinfo(entry.path, recurse=recurse,
                            followSymlinks=followSymlinks, filesOnly=filesOnly,
                            fnFilterDirs=fnFilterDirs, fnDirectExceptionsTo=fnDirectExceptionsTo):
                        yield subentry
                except:
                    e = sys.exc_info()[1]
                    if fnDirectExceptionsTo and isinstance(e, OSError):
                        fnDirectExceptionsTo(entry.path, e)
                    else:
                        raise

        if entry.is_file():
            yield FileInfoEntryWrapper(entry)

def listfileinfo(root, followSymlinks=False, filesOnly=True):
    return recursefileinfo(root, recurse=False,
        followSymlinks=followSymlinks, filesOnly=filesOnly)