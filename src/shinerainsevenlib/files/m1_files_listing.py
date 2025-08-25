
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import os as _os
import sys as _sys
from .m0_files_wrappers import *
from ..core import (
    alert as _alert,
    trace as _trace,
    assertTrue as _assertTrue,
)

def listDirs(path, *, filenamesOnly=False, recurse=False, **kwargs):
    """Return subdirectories within a directory. Doesn't include the root,
    unless recurse=True.
    
    Returns iterator of tuples ``(f, short)`` where ``f`` is full path
    and ``short`` is just the name.
    
    If you pass in filenamesOnly=True, returns iterator of just the names."""
    if recurse:
        return recurseDirs(
            path,
            filenamesOnly=filenamesOnly, **kwargs
        )
    else:
        return listChildren(path, filenamesOnly=filenamesOnly, 
                            includeFiles=False, includeDirs=True, **kwargs)

def listFiles(path, *, filenamesOnly=False, recurse=False, **kwargs):
    """Return files within a directory,

    For convenience, the results are sorted, regardless of the operating system.
    
    Returns iterator of tuples ``(f, short)`` where ``f`` is full path
    and ``short`` is just the filename.
    
    You can filter extensions by passing something like allowedExts=['png', 'gif']
    
    If you pass in filenamesOnly=True, returns iterator of just the filenames."""
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

# on windows platforms we can generally assume dir list results are sorted.
# for convenience, on other platforms, sort the results.
if _sys.platform.startswith('win'):
    exeSuffix = '.exe'
    "Default extension for executable files, like '.exe' on Windows."
    listChildren = _listChildrenUnsorted
else:
    exeSuffix = ''
    "Default extension for executable files, like '.exe' on Windows."

    def listChildren(*args, **kwargs):
        return sorted(_listChildrenUnsorted(*args, **kwargs))

def _checkAllowedExts(allowedExts):
    if isinstance(allowedExts, list):
        for ext in allowedExts:
            _assertTrue(not '.' in ext, 'provide a list like ["png", "gif"]')
        allowedExts = set(allowedExts)
    elif allowedExts and not isinstance(allowedExts, set):
        _assertTrue(False, 'allowedExts must be a list or set')

    return allowedExts

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
    
    You can filter extensions by passing something like allowedExts=['png', 'gif']

    You can provide a fnFilterDirs callback, to skip over certain directories.
    
    Returns iterator of tuples ``(f, short)`` where ``f`` is full path
    and ``short`` is just the filename.
    
    If you pass in filenamesOnly=True, returns iterator of just the filenames."""
    assert isDir(root)
    allowedExts = _checkAllowedExts(allowedExts)

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

    You can provide a fnFilterDirs callback, to skip over certain directories.
    
    Returns iterator of tuples ``(f, short)`` where ``f`` is full path
    and ``short`` is just the name.
    
    If you pass in filenamesOnly=True, returns iterator of just the names.

    Includes the root directory."""
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
    "When you call recurseFileInfo, the results are instances of this class."

    def __init__(self, obj):
        self.obj = obj
        self.path = obj.path

    def isDir(self, *args):
        "Is this a directory?"
        return self.obj.is_dir(*args)

    def isFile(self, *args):
        "Is this a file?"
        return self.obj.is_file(*args)

    def short(self):
        "The short name aka leaf of the file"
        return _os.path.split(self.path)[1]

    def size(self):
        "The size of the file, in bytes"
        return self.obj.stat().st_size

    def mtime(self):
        "The modified time of the file, in unix seconds"
        return self.obj.stat().st_mtime

    def getLastModTime(self, units=TimeUnits.Seconds):
        "The last-modified time, in units that you specify"
        mtime = self.mtime()

        if units == TimeUnits.Nanoseconds:
            return int(mtime * 1.0e6)
        elif units == TimeUnits.Milliseconds:
            return int(mtime * 1000)
        elif units == TimeUnits.Seconds:
            return int(mtime)
        else:
            raise ValueError('unknown unit')

def recurseFileInfo(
    root,
    allowedExts=None,
    **kwargs,
):
    """Convenient interface to python 3's file iterator.
    On Windows this can be very fast because calls to get file properties like size
    don't require an extra system call.
    
    >>> for f in recurseFileInfo('/path/to/files'):
    >>>     print("For the file", f.path)
    >>>     print("The size is", str(f.size()))

    You can provide a fnFilterDirs to filter out any directories not to traverse into.
    
    You can provide a fnDirectExceptionsTo to handle errors that occur during iteration-
    for example, upon encountering broken symlinks or accesss-denied errors to just log
    and continue to the next file.

    You can filter extensions by passing something like allowedExts=['png', 'gif']
    
    Other parameters include:

    recurse (True|False),
    
    followSymlinks (True|False),
    
    includeFiles (True|False),
    
    includeDirs (True|False),

    Does not include root directory."""
    allowedExts = _checkAllowedExts(allowedExts)
    return _recurseFileInfoRecurse(root, allowedExts=allowedExts, **kwargs)

def _recurseFileInfoRecurse(
    root,
    *,
    recurse=True,
    followSymlinks=False,
    includeFiles=True,
    includeDirs=False,
    fnFilterDirs=None,
    fnDirectExceptionsTo=None,
    allowedExts=None
):
    "Implementation of recurseFileInfo"
    # note that scandir's resources are released in a destructor,
    # so do not create circular references holding it.
    for entry in _os.scandir(root):
        if entry.is_dir(follow_symlinks=followSymlinks):
            if includeDirs and (not fnFilterDirs or fnFilterDirs(entry.path)):
                yield FileInfoEntryWrapper(entry)
                
            if recurse and (not fnFilterDirs or fnFilterDirs(entry.path)):
                try:
                    for subentry in _recurseFileInfoRecurse(
                        entry.path,
                        recurse=recurse,
                        followSymlinks=followSymlinks,
                        includeFiles=includeFiles,
                        includeDirs=includeDirs,
                        fnFilterDirs=fnFilterDirs,
                        fnDirectExceptionsTo=fnDirectExceptionsTo,
                        allowedExts=allowedExts
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
                if includeFiles:
                    yield FileInfoEntryWrapper(entry)

def listFileInfo(root, *, recurse=False, followSymlinks=False, includeFiles=True, includeDirs=False, ):
    "Like recurseFileInfo, but does not recurse."
    return recurseFileInfo(root, recurse=recurse, followSymlinks=followSymlinks,
                           includeFiles=includeFiles, includeDirs=includeDirs)

def getDirectorySizeRecurse(
    dirPath, *, followSymlinks=False, fnFilterDirs=None, fnDirectExceptionsTo=None
):
    "Calculate the total size of a directory"
    total = 0
    for obj in recurseFileInfo(
        dirPath,
        followSymlinks=followSymlinks,
        fnFilterDirs=fnFilterDirs,
        fnDirectExceptionsTo=fnDirectExceptionsTo,
    ):
        total += obj.size()
    
    return total
