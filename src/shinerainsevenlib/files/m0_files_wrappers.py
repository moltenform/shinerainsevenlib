
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import sys as _sys
import os as _os
import shutil as _shutil
import enum as _enum
from enum import StrEnum as _StrEnum

from .. import core as srss
from ..core import (
    alert as _alert,
    trace as _trace,
    assertTrue as _assertTrue,
)

exists = _os.path.exists
"Check if a path exists"

join = _os.path.join
"Join a parent directory to a child path fragment, like ``os.path.join``"

split = _os.path.split
"Split a path intto two parts: parent directory and name, like ``os.path.split``"

isDir = _os.path.isdir
"Does the path exist and is it a directory?"

isFile = _os.path.isfile
"Does the path exist and is it a file?"

getSize = _os.path.getsize
"Get the size of a file in bytes"

rmDir = _os.rmdir
"Remove a directory"

chDir = _os.chdir
"Change the current directory"

sep = _os.path.sep
"The directory separator, like /"

lineSep = _os.linesep
"The line separator character for the current operating system"

absPath = _os.path.abspath
"Convert any path to an absolute path"

rmTree = _shutil.rmtree
"Remove a directory, even if it contains files"

class TimeUnits(_StrEnum):
    """When calling a function like getLastModTime, use this enum to specify
    if you want the results in milliseconds, seconds, or nanoseconds.
    
    ``TimeUnits.Milliseconds``

    ``TimeUnits.Seconds``

    ``TimeUnits.Nanoseconds``"""
    Milliseconds = _enum.auto()
    Seconds = _enum.auto()
    Nanoseconds = _enum.auto()

def getParent(path):
    "From /path/to/file.ext to /path/to"
    return _os.path.split(path)[0]

def getName(path):
    "From /path/to/file.ext to file.ext"
    return _os.path.split(path)[1]

def getCreatedTime(path, units=TimeUnits.Seconds):
    "The created time of the file"
    if units == TimeUnits.Nanoseconds:
        return _os.stat(path).st_birthtime_ns
    elif units == TimeUnits.Milliseconds:
        return _os.stat(path).st_birthtime_ns / 1.0e6
    elif units == TimeUnits.Seconds:
        return _os.stat(path).st_birthtime
    else:
        raise ValueError('unknown timeunit')

def getExt(s, removeDot=True, onesToPreserve=None):
    """Get extension. removeDot determines whether result is '.jpg' or 'jpg'"
    onesToPreserve is a list like ['.l.jxl', '.j.jxl']"""
    _before, after = splitExt(s, onesToPreserve=onesToPreserve)
    if removeDot and len(after) > 0 and after[0] == '.':
        return after[1:].lower()
    else:
        return after.lower()

def splitExt(path, onesToPreserve=None):
    """From /a/b/c.ext1 to '/a/b/c' and '.ext1'
    
    onesToPreserve is a list like ['.l.jxl', '.j.jxl']
    , in which case '/a/b/c.l.jxl' will return '/a/b/c' and '.l.jxl'"""
    if onesToPreserve:
        for item in onesToPreserve:
            if path.endswith(item):
                part1 = path[0:-len(item)]
                part2 = item
                return part1, part2
        
        return _os.path.splitext(path)
    else:
        return _os.path.splitext(path)

def getWithDifferentExt(s, extWithDot, onesToPreserve=None):
    """From /a/b/c.ext1 to /a/b/c.ext1
    
    onesToPreserve is a list like ['.l.jxl', '.j.jxl']"""
    name, ext = splitExt(s, onesToPreserve=onesToPreserve)
    _assertTrue(ext, s)
    return name + extWithDot

def acrossDir(path, directoryFrom, directoryTo):
    """Get the other version of a path.
    If path is '/path1/to/file.ext' and directoryFrom is '/path1' and directoryTo is '/path2', then return '/path2/to2/file.ext'"""
    _assertTrue(not directoryTo.endswith(('/', '\\')))
    _assertTrue(not directoryFrom.endswith(('/', '\\')))
    _assertTrue(path.startswith(directoryFrom))
    remainder = path[len(directoryFrom):]
    _assertTrue(remainder == '' or remainder.startswith(('/', '\\')))
    return directoryTo + remainder


def delete(s, doTrace=False):
    "Delete a file"
    if doTrace:
        _trace('delete()', s)

    if exists(s):
        _os.unlink(s)

def deleteSure(s, doTrace=False):
    "Delete a file and confirm it is no longer there"
    delete(s, doTrace=doTrace)
    _assertTrue(not exists(s))

def makeDirs(s):
    "Make dirs, OK if dir already exists. also, creates parent directory(s) if needed."
    try:
        _os.makedirs(s)
    except OSError:
        if isDir(s):
            return
        else:
            raise

def ensureEmptyDirectory(d):
    "Delete all contents, or raise exception if that fails"
    if isFile(d):
        raise OSFileRelatedError('file exists at this location ' + d)

    if isDir(d):
        # delete all existing files in the directory
        for s in _os.listdir(d):
            if isDir(join(d, s)):
                _shutil.rmtree(join(d, s))
            else:
                _os.unlink(join(d, s))

        _assertTrue(isEmptyDir(d))
    else:
        _os.makedirs(d)

def arePathsSame(path1, path2):
    """Check if two paths are the same. For example, a relative path and absolute path to the same file.
    Also, on Windows, two paths with different casing should be considered to be the same."""
    return _os.path.normcase(_os.path.normpath(_os.path.abspath(path1))) == \
        _os.path.normcase(_os.path.normpath(_os.path.abspath(path2)))

def copy(
    srcFile,
    destFile,
    overwrite,
    doTrace=False,
    keepSameModifiedTime=False,
    allowDirs=False,
    createParent=False,
    traceOnly=False):
    """If overwrite is True, always overwrites if destination already exists.
    if overwrite is False, always raises exception if destination already exists.

    Unlike other copy() implementations, we made the behavior consistent on Windows, Mac, and Linux.
    
    To be extra-safe, the overwrite=False checks are safe against race-conditions.
    In the rare case where another process or thread puts a file there exactly at the same time,
    no data will be overwritten.

    Use `doTrace` or `traceOnly` to print out the paths being copied, for logging/debugging.

    (For speed and simplicity, most of the functionality in shinerainsevenlib isn't concerned
    with race-conditions like this, but for copy() and move() we added that capability.)"""
    try:
        return _copyImpl(srcFile, destFile, overwrite=overwrite, 
                        doTrace=doTrace, keepSameModifiedTime=keepSameModifiedTime, allowDirs=allowDirs,
                        createParent=createParent, traceOnly=traceOnly)
    except Exception:
        print(f"Failed to copy {srcFile} to {destFile}", file=_sys.stderr)
        raise

def _copyImpl(
    srcFile,
    destFile,
    overwrite,
    doTrace=False,
    keepSameModifiedTime=False,
    allowDirs=False,
    createParent=False,
    traceOnly=False,
):
    if doTrace:
        _trace('copy()', srcFile, destFile)
    if not exists(srcFile):
        raise OSFileRelatedError('source path does not exist' + srcFile)
    if not allowDirs and not isFile(srcFile):
        raise OSFileRelatedError('allowDirs is False but given a dir' + srcFile)

    toSetModTime = None
    if keepSameModifiedTime and exists(destFile):
        _assertTrue(isFile(destFile), 'not supported for directories')
        toSetModTime = getLastModTime(destFile, units=TimeUnits.Nanoseconds)

    if traceOnly:
        # can be useful for temporary debugging
        return

    if createParent and not exists(getParent(destFile)):
        makeDirs(getParent(destFile))

    if arePathsSame(srcFile, destFile):
        _trace('Paths equal, skipping.')
    elif _sys.platform.startswith('win'):
        _copyFileWin(srcFile, destFile, overwrite)
    else:
        _copyFilePosix(srcFile, destFile, overwrite)

    _assertTrue(exists(destFile))
    if toSetModTime:
        setLastModTime(destFile, toSetModTime, units=TimeUnits.Nanoseconds)

def move(
    srcFile,
    destFile,
    overwrite,
    warnBetweenDrives=False,
    doTrace=False,
    allowDirs=False,
    createParent=False,
    traceOnly=False,):
    """If overwrite is True, always overwrites if destination already exists.
    if overwrite is False, always raises exception if destination already exists.

    Unlike other move() implementations, we made the behavior consistent on Windows, Mac, and Linux.
    
    To be extra-safe, the overwrite=False checks are safe against race-conditions.
    In the rare case where another process or thread puts a file there exactly at the same time,
    no data will be overwritten.

    Use `doTrace` or `traceOnly` to print out the paths being copied, for logging/debugging.

    (For speed and simplicity, most of the functionality in shinerainsevenlib isn't concerned
    with race-conditions like this, but for copy() and move() we added that capability.)"""
    try:
        return _moveImpl(srcFile, destFile, overwrite=overwrite, warnBetweenDrives=warnBetweenDrives,
                        doTrace=doTrace, allowDirs=allowDirs, createParent=createParent, traceOnly=traceOnly)
    except Exception:
        print(f"Failed to move {srcFile} to {destFile}", file=_sys.stderr)
        raise

def _moveImpl(
    srcFile,
    destFile,
    overwrite,
    warnBetweenDrives=False,
    doTrace=False,
    allowDirs=False,
    createParent=False,
    traceOnly=False,
):
    """If overwrite is True, always overwrites if destination already exists.
    if overwrite is False, always raises exception if destination already exists."""
    if doTrace:
        _trace('move()', srcFile, destFile)
    if not exists(srcFile):
        raise OSFileRelatedError('source path does not exist')
    if not allowDirs and not isFile(srcFile):
        raise OSFileRelatedError('allowDirs is False but given a dir')

    if traceOnly:
        # can be useful for temporary debugging
        return

    if createParent and not exists(getParent(destFile)):
        makeDirs(getParent(destFile))

    if arePathsSame(srcFile, destFile):
        _trace('Paths equal, skipping.')
    elif _sys.platform.startswith('win'):
        _moveFileWin(srcFile, destFile, overwrite, warnBetweenDrives)
    else:
        _moveFilePosixNoOverwrite(srcFile, destFile, overwrite)

    _assertTrue(exists(destFile))

confirmedMvOpts = None
def _moveFilePosixNoOverwrite(srcFile, destFile, overwrite):
    from . import m2_files_higher
    global confirmedMvOpts
    if overwrite:
        _shutil.move(srcFile, destFile)
        return

    # why not use copy-with-exclusive lock, like we do for copy()?
    # because the implementation of move that way would look like this:
    # 1) copy src to dest 2) delete src
    # so if for some reason src and dest pointed to the same data, this could
    # lead to data loss. we do a check for this in arePathsSame() but there could be
    # some type of scenario like hardlinks where we'd still be in trouble.
    # could potentially build a solution by copying to temp file, but that's complex
    # so let's shell out to mv just to be safe.

    if confirmedMvOpts is None:
        confirmedMvOpts = _confirmMvOpts()

    if confirmedMvOpts is not True:
        raise OSFileRelatedError("Could not move, " + confirmedMvOpts)
    else:
        m2_files_higher.run(['mv', '--no-clobber', srcFile, destFile], shell=True)
    
def _confirmMvOpts():
    "Check that --no-clobber both 1) doesn't error and 2) actually doesn't clobber"
    from . import m2_files_higher
    import tempfile as _tmpfile
    err = None
    f1 = _tmpfile.gettempdir() + '/f1.txt'
    f2 = _tmpfile.gettempdir() + '/f2.txt'
    writeAll(f1, 'f1')
    writeAll(f2, 'f2')
    didClobber = False
    try:
        # coreutils that support this include: gnu, toybox, rust uutils
        # coreutils that don't support this include: busybox, heirloom, sbase
        # coreutils where I didn't see mv: 9base, ubase
        m2_files_higher.run(['mv', '--no-clobber', f1, f2], shell=True)
        didClobber = readAll(f2) == 'f1'
    except Exception as err:
        return f'failed to run no-clobber test, please use gnu coreutils or rust uutils {err}'
    finally:
        delete(f1)
        delete(f2)
    
    if didClobber:
        return 'mv still overwrote even with --no-clobber, please use gnu coreutils or rust uutils'
    else:
        return True
        

_winErrs = {
    3: 'Path not found',
    5: 'Access denied',
    17: 'Different drives',
    80: 'Destination already exists',
}

def _copyFileWin(srcFile, destFile, overwrite):
    from ctypes import windll, c_wchar_p, c_int, GetLastError

    _assertTrue(_sys.platform.startswith('win'))
    failIfExists = c_int(0) if overwrite else c_int(1)
    res = windll.kernel32.CopyFileW(c_wchar_p(srcFile), c_wchar_p(destFile), failIfExists)
    if not res:
        err = GetLastError()
        raise OSFileRelatedError(
            f'CopyFileW failed ({_winErrs.get(err, "unknown")}) err={err}'
        )

def _moveFileWin(srcFile, destFile, overwrite, warnBetweenDrives):
    from ctypes import windll, c_wchar_p, c_int, GetLastError

    flags = 0
    flags |= 1 if overwrite else 0
    flags |= 0 if warnBetweenDrives else 2
    res = windll.kernel32.MoveFileExW(c_wchar_p(srcFile), c_wchar_p(destFile), c_int(flags))

    if not res:
        err = GetLastError()
        if _winErrs.get(err) == 'Different drives' and warnBetweenDrives:
            _alert(
                'Note: moving file from one drive to another. ' +
                srss.getPrintable(srcFile + '->' + destFile)
            )
            return _moveFileWin(srcFile, destFile, overwrite, warnBetweenDrives=False)

        raise OSFileRelatedError(
            f'MoveFileExW failed ({_winErrs.get(err, "unknown")}) err={err} '
        )
    
    return None

def _copyFilePosixByContentsNoOverwrite(srcFile, destFile):
    "This is an opt-in type of lock, but works in all scenarios tested."
    # fails if destination already exists. O_EXCL prevents other files from writing to location.
    # raises OSError on failure.
    flags = _os.O_CREAT | _os.O_EXCL | _os.O_WRONLY
    fileHandle = _os.open(destFile, flags)
    with _os.fdopen(fileHandle, 'wb') as fDest:
        # confirmed that the context manager will automatically close the handle
        with open(srcFile, 'rb') as fSrc:
            while True:
                buffer = fSrc.read(64 * 1024)
                if not buffer:
                    break
                fDest.write(buffer)

def _copyFilePosix(srcFile, destFile, overwrite):
    _assertTrue(not _sys.platform.startswith('win'))
    if overwrite:
        _shutil.copy(srcFile, destFile)
    else:
        _copyFilePosixByContentsNoOverwrite(srcFile, destFile)

def _getStatTime(path, key_ns, key_s, units):
    st = _os.stat(path)
    if key_ns in dir(st):
        timeNs = getattr(st, key_ns)
    else:
        # fall back to seconds in case it is not available (like some py2)
        timeNs = getattr(st, key_s) * 1.0e9

    if units == TimeUnits.Nanoseconds:
        return int(timeNs)
    elif units == TimeUnits.Milliseconds:
        return int(timeNs / 1.0e6)
    elif units == TimeUnits.Seconds:
        return int(timeNs / 1.0e9)
    else:
        raise ValueError('unknown unit')

def getLastModTime(path, units=TimeUnits.Seconds):
    "Last-modified time"
    return _getStatTime(path, 'st_mtime_ns', 'st_mtime', units)

def _getATime(path, units=TimeUnits.Seconds):
    """The 'atime' of a file. In modern systems this isn't usually the last-accessed time.
    Currently unexposed because it's only useful internaly"""
    return _getStatTime(path, 'st_atime_ns', 'st_atime', units)

def setLastModTime(path, newVal, units=TimeUnits.Seconds):
    "Set the last-modified time of a file"
    if units == TimeUnits.Nanoseconds:
        newVal = int(newVal)
    elif units == TimeUnits.Milliseconds:
        newVal = int(newVal * 1.0e6)
    elif units == TimeUnits.Seconds:
        newVal = int(newVal * 1.0e9)
    else:
        raise ValueError('unknown unit')

    atimeNs = _getATime(path, units=TimeUnits.Nanoseconds)
    _os.utime(path, ns=(atimeNs, newVal))

def readAll(path, mode='r', encoding=None):
    """Read entire file into string (mode=='r') or bytes (mode=='rb')
    
    When reading as text, defaults to utf-8. Not python2 compatible."""
    if 'b' not in mode and encoding is None:
        encoding = 'utf-8'

    with open(path, mode, encoding=encoding) as f:
        return f.read()

def writeAll(
    path, content, mode='w', encoding=None, skipIfSameContent=False, updateTimeIfSameContent=True
):
    """Write entire file. 
    
    Common modes are 'w' for writing text and 'wb' for writing bytes.
    
    When writing text, defaults to utf-8. Not python2 compatible."""
    if 'b' not in mode and encoding is None:
        encoding = 'utf-8'

    if skipIfSameContent and isFile(path):
        _assertTrue(mode in ('w', 'wb'))
        currentContent = readAll(path, mode=mode.replace('w', 'r'), encoding=encoding)
        if currentContent == content:
            if updateTimeIfSameContent:
                setLastModTime(path, srss.getNowAsMillisTime(), units=TimeUnits.Milliseconds)
            return False

    with open(path, mode, encoding=encoding) as f:
        f.write(content)
        return True

def isEmptyDir(dirPath):
    "Is a directory empty"
    return len(_os.listdir(dirPath)) == 0

def fileContentsEqual(f1, f2):
    "Efficiently tests if the content of two files is the same"
    import filecmp

    filecmp.clear_cache()
    return filecmp.cmp(f1, f2, shallow=False)

class OSFileRelatedError(OSError):
    "Indicates a file-related exception"

