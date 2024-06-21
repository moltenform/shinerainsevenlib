
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import os as _os
import sys as _sys
from .m1_files_wrappers import *

def listDirs(path, *, filenamesOnly=False, recurse=False, **kwargs):
    "Return directories within a directory"
    if recurse:
        return recurseDirs(
            path,
            filenamesOnly=filenamesOnly, **kwargs
        )
    else:
        return listChildren(path, filenamesOnly=filenamesOnly, 
                            includeFiles=False, includeDirs=True, **kwargs)

def listFiles(path, *, recurse=False, filenamesOnly=False, **kwargs):
    "Return files within a directory"
    if recurse:
        return recurseFiles(path, filenamesOnly=filenamesOnly, **kwargs)
    else:
        return listChildren(path, filenamesOnly=filenamesOnly, 
                            includeFiles=True, includeDirs=False, **kwargs)

def _listChildrenUnsorted(path, *, filenamesOnly=False, allowedExts=None,
                          includeFiles=True, includeDirs=True):
    "List directory contents. allowedExts in the form ['png', 'gif']"
    
    for filename in _os.listdir(path):
        if not allowedExts or (getExt(filename, removeDot=True) in allowedExts):
            fullPath = path + _os.path.sep + filename
            if not includeFiles and _os.path.isfile(fullPath):
                continue
            if not includeDirs and _os.path.isdir(fullPath):
                continue
            yield filename if filenamesOnly else (fullPath, filename)

# on windows platforms we can typically assume dir list results are sorted
# for consistency, on other platforms, sort the results.
if _sys.platform.startswith('win'):
    exeSuffix = '.exe'
    listChildren = _listChildrenUnsorted
else:
    exeSuffix = ''

    def listChildren(*args, **kwargs):
        return sorted(_listChildrenUnsorted(*args, **kwargs))

def recurseFiles(
    root,
    *,
    filenamesOnly=False,
    allowedExts=None,
    fnFilterDirs=None,
    includeFiles=True,
    includeDirs=False,
    topDown=True,
    followSymlinks=False,
):
    """Return files within a directory (recursively).
    You can provide a fnFilterDirs to filter out any directories not to traverse into."""
    assert isDir(root)

    if isinstance(allowedExts, list):
        allowedExts = set(allowedExts)

    for dirPath, dirNames, fileNames in _os.walk(root, topdown=topDown, followlinks=followSymlinks):
        if fnFilterDirs:
            filteredDirs = [dirPath for dirPath in dirNames if fnFilterDirs(join(dirPath, dirPath))]
            dirNames[:] = filteredDirs

        if includeFiles:
            iterFilenames = fileNames if _sys.platform.startswith('win') else sorted(fileNames)
            for filename in iterFilenames:
                if not allowedExts or (getExt(filename, removeDot=True) in allowedExts):
                    yield (
                        filename if filenamesOnly else (dirPath + _os.path.sep + filename, filename)
                    )

        if includeDirs:
            yield getName(dirPath) if filenamesOnly else (dirPath, getName(dirPath))

def recurseDirs(
    root, *, filenamesOnly=False, fnFilterDirs=None, topDown=True, followSymlinks=False
):
    """Return directories within a directory (recursively).
    You can provide a fnFilterDirs to filter out any directories not to traverse into."""
    return recurseFiles(
        root,
        filenamesOnly=filenamesOnly,
        fnFilterDirs=fnFilterDirs,
        includeFiles=False,
        includeDirs=True,
        topDown=topDown,
        followSymlinks=followSymlinks,
    )

class FileInfoEntryWrapper:
    "Helper class to make recurseFileInfo more convenient to use."

    def __init__(self, obj):
        self.obj = obj
        self.path = obj.path

    def isDir(self, *args):
        return self.obj.is_dir(*args)

    def isFile(self, *args):
        return self.obj.is_file(*args)

    def short(self):
        return _os.path.split(self.path)[1]

    def size(self):
        return self.obj.stat().st_size

    def mtime(self):
        return self.obj.stat().st_mtime

    def getLastModTime(self, units=TimeUnits.Seconds):
        mtime = self.obj.stat().st_mtime

        if units == TimeUnits.Nanoseconds:
            return int(mtime * 1.0e6)
        elif units == TimeUnits.Milliseconds:
            return int(mtime * 1000)
        elif units == TimeUnits.Seconds:
            return int(mtime)
        else:
            raise ValueError('unknown unit')

    def getMetadataChangeTime(self):
        assertTrue(not _sys.platform.startswith('win'))
        return self.obj.stat().st_ctime

    def getCreateTime(self):
        assertTrue(_sys.platform.startswith('win'))
        return self.obj.stat().st_ctime

def recurseFileInfo(
    root,
    allowedExts=None,
    **kwargs,
):
    """Convenient interface to python 3's file iterator.
    On Windows this can be very fast because calls to get file properties like size
    don't require an extra system call.
    You can provide a fnFilterDirs to filter out any directories not to traverse into."""
    if isinstance(allowedExts, list):
        allowedExts = set(allowedExts)
        
    return _recurseFileInfoRecurse(root, allowedExts=allowedExts, **kwargs)

def _recurseFileInfoRecurse(
    root,
    recurse=True,
    followSymlinks=False,
    filesOnly=True,
    fnFilterDirs=None,
    fnDirectExceptionsTo=None,
    allowedExts=None
):
    
    # note that scandir's resources are released in a destructor,
    # so do not create circular references holding it.
    for entry in _os.scandir(root):
        if entry.is_dir(follow_symlinks=followSymlinks):
            if not filesOnly:
                yield FileInfoEntryWrapper(entry)
            if recurse and (not fnFilterDirs or fnFilterDirs(entry.path)):
                try:
                    for subentry in _recurseFileInfoRecurse(
                        entry.path,
                        recurse=recurse,
                        followSymlinks=followSymlinks,
                        filesOnly=filesOnly,
                        fnFilterDirs=fnFilterDirs,
                        fnDirectExceptionsTo=fnDirectExceptionsTo,
                    ):
                        yield subentry
                except:
                    e = srss.getCurrentException()
                    if fnDirectExceptionsTo and isinstance(e, OSError):
                        fnDirectExceptionsTo(entry.path, e)
                    else:
                        raise

        if entry.is_file():
            if not allowedExts or (getExt(entry.path, removeDot=True) in allowedExts):
                yield FileInfoEntryWrapper(entry)

def listFileInfo(root, followSymlinks=False, filesOnly=True):
    "Like recurseFileInfo, but does not recurse."
    return recurseFileInfo(root, recurse=False, followSymlinks=followSymlinks, filesOnly=filesOnly)

def getDirectorySizeRecurse(
    dirPath, followSymlinks=False, fnFilterDirs=None, fnDirectExceptionsTo=None
):
    total = 0
    for obj in recurseFileInfo(
        dirPath,
        followSymlinks=followSymlinks,
        fnFilterDirs=fnFilterDirs,
        fnDirectExceptionsTo=fnDirectExceptionsTo,
    ):
        total += obj.size()
    return total
