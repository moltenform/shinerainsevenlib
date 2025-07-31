
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import sys as _sys
import os as _os
import shutil as _shutil
import enum as _enum
from enum import StrEnum as _StrEnum

from .. import core as srss
from ..core import (
    alert,
    trace,
    assertTrue,
    assertEq
)

rename = _os.rename
exists = _os.path.exists
join = _os.path.join
split = _os.path.split
isDir = _os.path.isdir
isFile = _os.path.isfile
getSize = _os.path.getsize
rmDir = _os.rmdir
chDir = _os.chdir
sep = _os.path.sep
lineSep = _os.linesep
absPath = _os.path.abspath
rmTree = _shutil.rmtree

class TimeUnits(_StrEnum):
    Milliseconds = _enum.auto()
    Seconds = _enum.auto()
    Nanoseconds = _enum.auto()

def getParent(path):
    return _os.path.split(path)[0]

def getName(path):
    return _os.path.split(path)[1]

def createdTime(path):
    return _os.stat(path).st_ctime

def getExt(s, removeDot=True):
    "Get extension. removeDot determines whether result is '.jpg' or 'jpg'"
    _before, after = splitExt(s)
    if removeDot and len(after) > 0 and after[0] == '.':
        return after[1:].lower()
    else:
        return after.lower()

def getWithDifferentExt(s, extWithDot, onesToPreserve=None):
    """From /a/b/c.ext1 to /a/b/c.ext1
    
    onesToPreserve is a list like ['.l.jxl', '.j.jxl']
    """
    for attempt in (onesToPreserve or []):
        if s.endswith(attempt):
            name = s[0:-len(attempt)]
            return name + extWithDot

    name, ext = splitExt(s)
    assertTrue(ext, s)
    return name + extWithDot

def splitExt(path, onesToPreserve=None):
    """
    onesToPreserve is a list like ['.l.jxl', '.j.jxl']
    """
    if onesToPreserve:
        withNoExt = getWithDifferentExt(path, '', onesToPreserve)
        first = path[0:len(withNoExt)]
        second = path[len(withNoExt):]
        return first, second
    else:
        return _os.path.splitext(path)


def delete(s, doTrace=False):
    "Delete a file"
    if doTrace:
        trace('delete()', s)

    if exists(s):
        _os.unlink(s)

def deleteSure(s, doTrace=False):
    "Delete a file and confirm it is no longer there"
    delete(s, doTrace)
    assertTrue(not exists(s))

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

        assertTrue(isEmptyDir(d))
    else:
        _os.makedirs(d)

def copy(
    srcFile,
    destFile,
    overwrite,
    doTrace=False,
    keepSameModifiedTime=False,
    allowDirs=False,
    createParent=False,
    traceOnly=False,
):
    """If overwrite is True, always overwrites if destination already exists.
    if overwrite is False, always raises exception if destination already exists."""
    if doTrace:
        trace('copy()', srcFile, destFile)
    if not isFile(srcFile):
        raise OSFileRelatedError('source path does not exist or is not a file')
    if not allowDirs and isDir(srcFile):
        raise OSFileRelatedError('allowDirs is False but given a dir')

    toSetModTime = None
    if keepSameModifiedTime and exists(destFile):
        assertTrue(isFile(destFile), 'not supported for directories')
        toSetModTime = getLastModTime(destFile, units=TimeUnits.Nanoseconds)

    if traceOnly:
        # can be useful for temporary debugging
        return

    if createParent and not exists(getParent(destFile)):
        makeDirs(getParent(destFile))

    if srcFile == destFile:
        pass
    elif _sys.platform.startswith('win'):
        _copyFileWin(srcFile, destFile, overwrite)
    else:
        _copyFilePosix(srcFile, destFile, overwrite)

    assertTrue(exists(destFile))
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
    traceOnly=False,
):
    """If overwrite is True, always overwrites if destination already exists.
    if overwrite is False, always raises exception if destination already exists."""
    if doTrace:
        trace('move()', srcFile, destFile)
    if not exists(srcFile):
        raise OSFileRelatedError('source path does not exist ' + srcFile)
    if not allowDirs and not isFile(srcFile):
        raise OSFileRelatedError('allowDirs is False but given a dir ' + srcFile)

    if traceOnly:
        # can be useful for temporary debugging
        return

    if createParent and not exists(getParent(destFile)):
        makeDirs(getParent(destFile))

    if srcFile == destFile:
        pass
    elif _sys.platform.startswith('win'):
        _moveFileWin(srcFile, destFile, overwrite, warnBetweenDrives)
    elif _sys.platform.startswith('linux') and overwrite:
        _os.rename(srcFile, destFile)
    else:
        copy(srcFile, destFile, overwrite)
        assertTrue(exists(destFile))
        _os.unlink(srcFile)

    assertTrue(exists(destFile))

_winErrs = {
    3: 'Path not found',
    5: 'Access denied',
    17: 'Different drives',
    80: 'Destination already exists',
}

def _copyFileWin(srcFile, destFile, overwrite):
    from ctypes import windll, c_wchar_p, c_int, GetLastError

    failIfExists = c_int(0) if overwrite else c_int(1)
    res = windll.kernel32.CopyFileW(c_wchar_p(srcFile), c_wchar_p(destFile), failIfExists)
    if not res:
        err = GetLastError()
        raise OSFileRelatedError(
            f'CopyFileW failed ({_winErrs.get(err, "unknown")}) err={err} ' +
            srss.getPrintable(srcFile + '->' + destFile)
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
            alert(
                'Note: moving file from one drive to another. ' +
                srss.getPrintable(srcFile + '->' + destFile)
            )
            return _moveFileWin(srcFile, destFile, overwrite, warnBetweenDrives=False)

        raise OSFileRelatedError(
            f'MoveFileExW failed ({_winErrs.get(err, "unknown")}) err={err} ' +
            srss.getPrintable(srcFile + '->' + destFile)
        )
    return None

def _copyFilePosix(srcFile, destFile, overwrite):
    if overwrite:
        _shutil.copy(srcFile, destFile)
        return

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

def _getStatTime(path, key_ns, key_s, units):
    st = _os.stat(path)
    if key_ns in dir(st):
        timeNs = getattr(st, key_ns)
    else:
        # fall back to seconds in case it is not available (like some py2)
        timeNs = getattr(st, key_s) * 1000 * 1000

    if units == TimeUnits.Nanoseconds:
        return int(timeNs)
    elif units == TimeUnits.Milliseconds:
        return int(timeNs / 1.0e6)
    elif units == TimeUnits.Seconds:
        return int(timeNs / 1.0e9)
    else:
        raise ValueError('unknown unit')

def getLastModTime(path, units=TimeUnits.Seconds):
    return _getStatTime(path, 'st_mtime_ns', 'st_mtime', units)

def getCTime(path, units=TimeUnits.Seconds):
    return _getStatTime(path, 'st_ctime_ns', 'st_ctime', units)

def getATime(path, units=TimeUnits.Seconds):
    return _getStatTime(path, 'st_atime_ns', 'st_atime', units)

def setLastModTime(path, newVal, units=TimeUnits.Seconds):
    if units == TimeUnits.Nanoseconds:
        newVal = int(newVal)
    elif units == TimeUnits.Milliseconds:
        newVal = int(newVal * 1.0e6)
    elif units == TimeUnits.Seconds:
        newVal = int(newVal * 1.0e9)
    else:
        raise ValueError('unknown unit')

    atimeNs = getATime(path, units=TimeUnits.Nanoseconds)
    _os.utime(path, ns=(atimeNs, newVal))

def readAll(path, mode='r', encoding=None):
    """Read entire file into string (mode=='r') or bytes (mode=='rb')
    When reading as text, defaults to utf-8."""
    if 'b' not in mode and encoding is None:
        encoding = 'utf-8'
    with open(path, mode, encoding=encoding) as f:
        return f.read()

def writeAll(
    path, content, mode='w', encoding=None, skipIfSameContent=False, updateTimeIfSameContent=True
):
    """Write entire file. Defaults to utf-8."""
    if 'b' not in mode and encoding is None:
        encoding = 'utf-8'

    if skipIfSameContent and isFile(path):
        assertTrue(mode in ('w', 'wb'))
        currentContent = readAll(path, mode=mode.replace('w', 'r'), encoding=encoding)
        if currentContent == content:
            if updateTimeIfSameContent:
                setLastModTime(path, srss.getNowAsMillisTime(), units=TimeUnits.Milliseconds)
            return False

    with open(path, mode, encoding=encoding) as f:
        f.write(content)
        return True

def isEmptyDir(dirPath):
    return len(_os.listdir(dirPath)) == 0

def fileContentsEqual(f1, f2):
    import filecmp

    return filecmp.cmp(f1, f2, shallow=False)

def acrossDir(path, directoryFrom, directoryTo):
    assertTrue(not directoryTo.endswith(('/', '\\')))
    assertTrue(not directoryFrom.endswith(('/', '\\')))
    assertTrue(path.startswith(directoryFrom))
    remainder = path[len(directoryFrom):]
    assertTrue(remainder == '' or remainder.startswith('/') or remainder.startswith('\\'))
    return directoryTo + remainder

class OSFileRelatedError(OSError):
    pass
