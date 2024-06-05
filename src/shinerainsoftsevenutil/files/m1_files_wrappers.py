# shinerainsoftsevencommon
# Released under the LGPLv3 License

import sys
import os
import shutil

from ..core import *

rename = os.rename
exists = os.path.exists
join = os.path.join
split = os.path.split
splitExt = os.path.splitext
isDir = os.path.isdir
isFile = os.path.isfile
getSize = os.path.getsize
rmDir = os.rmdir
chDir = os.chdir
sep = os.path.sep
lineSep = os.linesep
absPath = os.path.abspath
rmTree = shutil.rmtree

TimeUnits = SimpleEnum(('Milliseconds', 'Seconds', 'Nanoseconds'))

def getParent(path):
    return os.path.split(path)[0]

def getName(path):
    return os.path.split(path)[1]

def createdTime(path):
    return os.stat(path).st_ctime

def getExt(s, removeDot=True):
    a, b = splitExt(s)
    if removeDot and len(b) > 0 and b[0] == '.':
        return b[1:].lower()
    else:
        return b.lower()

def getWithDifferentExt(s, ext_with_dot):
    parent, short = os.path.split(s)
    short_before_ext, short_ext = os.path.splitExt(short)
    assertTrue(short_ext, s)
    if parent:
        with_trailing_slash = s[0:len(parent)+1]
        assertTrue(with_trailing_slash == parent+'/' or with_trailing_slash == parent+'\\')
        return with_trailing_slash + short_before_ext + ext_with_dot
    else:
        return short_before_ext + ext_with_dot

def delete(s, doTrace=False):
    if doTrace:
        trace('delete()', s)

    os.unlink(s)

def deleteSure(s, doTrace=False):
    if exists(s):
        delete(s, doTrace)

    assertTrue(not exists(s))

def makeDirs(s):
    "ok if dir already exists. also, creates parent directory(s) if needed."
    try:
        os.makedirs(s)
    except OSError:
        if isDir(s):
            return
        else:
            raise

def ensureEmptyDirectory(d):
    "delete all contents, or raise exception if that fails"
    if isFile(d):
        raise IOError('file exists at this location ' + d)

    if isDir(d):
        # delete all existing files in the directory
        for s in os.listdir(d):
            if os.path.isDir(join(d, s)):
                shutil.rmtree(join(d, s))
            else:
                os.unlink(join(d, s))

        assertTrue(isEmptyDir(d))
    else:
        os.makedirs(d)

def copy(srcFile, destFile, overwrite, doTrace=False,
        keepSameModifiedTime=False, allowDirs=False, createParent=False, traceOnly=False):
    """if overwrite is True, always overwrites if destination already exists.
    if overwrite is False, always raises exception if destination already exists."""
    if not isFile(srcFile):
        raise IOError('source path does not exist or is not a file')
    if not allowDirs and isDir(srcFile):
        raise IOError('allowDirs is False but given a dir')

    toSetModTime = None
    if keepSameModifiedTime and exists(destFile):
        assertTrue(isFile(destFile), 'not supported for directories')
        toSetModTime = getLastModifiedTime(destFile, units=TimeUnits.Nanoseconds)

    if doTrace:
        trace('copy()', srcFile, destFile)
    
    if traceOnly:
        # can be useful for temporary debugging
        return

    if createParent and not exists(getParent(destFile)):
        makeDirs(getParent(destFile))

    if srcFile == destFile:
        pass
    elif sys.platform.startswith('win'):
        _copyFileWin(srcFile, destFile, overwrite)
    else:
        _copyFilePosix(srcFile, destFile, overwrite)

    assertTrue(exists(destFile))
    if toSetModTime:
        setLastModifiedTime(destFile, toSetModTime, units=TimeUnits.Nanoseconds)

def move(srcFile, destFile, overwrite, warnBetweenDrives=False,
        doTrace=False, allowDirs=False, createParent=False, traceOnly=False):
    """if overwrite is True, always overwrites if destination already exists.
    if overwrite is False, always raises exception if destination already exists."""
    if not exists(srcFile):
        raise IOError('source path does not exist')
    if not allowDirs and not isFile(srcFile):
        raise IOError('allowDirs is False but given a dir')

    if doTrace:
        trace('move()', srcFile, destFile)
    
    if traceOnly:
        # can be useful for temporary debugging
        return

    if createParent and not exists(getParent(destFile)):
        makeDirs(getParent(destFile))

    if srcFile == destFile:
        pass
    elif sys.platform.startswith('win'):
        _moveFileWin(srcFile, destFile, overwrite, warnBetweenDrives)
    elif sys.platform.startswith('linux') and overwrite:
        os.rename(srcFile, destFile)
    else:
        copy(srcFile, destFile, overwrite)
        assertTrue(exists(destFile))
        os.unlink(srcFile)

    assertTrue(exists(destFile))

_winErrs = {3: 'Path not found', 5: 'Access denied',
            17: 'Different drives',
             80: 'Destination already exists' }

def _copyFileWin(srcFile, destFile, overwrite):
    from ctypes import windll, c_wchar_p, c_int, GetLastError
    failIfExists = c_int(0) if overwrite else c_int(1)
    res = windll.kernel32.CopyFileW(c_wchar_p(srcFile), c_wchar_p(destFile), failIfExists)
    if not res:
        err = GetLastError()
        raise IOError(f'CopyFileW failed ({_winErrs.get(err, "unknown")}) err={err} ' +
            getPrintable(srcFile + '->' + destFile))

def _moveFileWin(srcFile, destFile, overwrite, warnBetweenDrives):
    from ctypes import windll, c_wchar_p, c_int, GetLastError
    flags = 0
    flags |= 1 if overwrite else 0
    flags |= 0 if warnBetweenDrives else 2
    res = windll.kernel32.MoveFileExW(c_wchar_p(srcFile), c_wchar_p(destFile), c_int(flags))
    
    if not res:
        err = GetLastError()
        if _winErrs.get(err) == 'Different drives' and warnBetweenDrives:
            alert('Note: moving file from one drive to another. ' +
                getPrintable(srcFile + '->' + destFile))
            return _moveFileWin(srcFile, destFile, overwrite, warnBetweenDrives=False)

        raise IOError(f'MoveFileExW failed ({_winErrs.get(err, "unknown")}) err={err} ' +
            getPrintable(srcFile + '->' + destFile))

def _copyFilePosix(srcFile, destFile, overwrite):
    if overwrite:
        shutil.copy(srcFile, destFile)
        return

    # fails if destination already exists. O_EXCL prevents other files from writing to location.
    # raises OSError on failure.
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fileHandle = os.open(destFile, flags)
    with os.fdopen(fileHandle, 'wb') as fDest:
        # confirmed that the context manager will automatically close the handle
        with open(srcFile, 'rb') as fSrc:
            while True:
                buffer = fSrc.read(64 * 1024)
                if not buffer:
                    break
                fDest.write(buffer)


def _getStatTime(path, key_ns, key_s, units):
    st = os.stat(path)
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


def getLastModifiedTime(path, units=TimeUnits.Seconds):
    return _getStatTime(path, 'st_mtime_ns', 'st_mtime', units)

def getCTime(path, units=TimeUnits.Seconds):
    return _getStatTime(path, 'st_ctime_ns', 'st_ctime', units)
    
def getATime(path, units=TimeUnits.Seconds):
    return _getStatTime(path, 'st_atime_ns', 'st_atime', units)


def setLastModifiedTime(path, newVal, units=TimeUnits.Seconds):
    if units == TimeUnits.Nanoseconds:
        newVal = int(newVal)
    elif units == TimeUnits.Milliseconds:
        newVal = int(newVal * 1.0e6)
    elif units == TimeUnits.Seconds:
        newVal = int(newVal * 1.0e9)
    else:
        raise ValueError('unknown unit')
        
    atimeNs = getATime(path, units=TimeUnits.Nanoseconds)
    os.utime(path, ns=(atimeNs, newVal))

def readAll(path, mode='r', encoding=None):
    """Read entire file into string (mode=='r') or bytes (mode=='rb')
    When reading as text, defaults to utf-8."""
    if 'b' not in mode and encoding==None:
        encoding = 'utf-8'
    with open(path, mode, encoding=encoding) as f:
        return f.read()

def writeAll(path, txt, mode='w', encoding=None,
             skipIfSameContent=False, updateTimeIfSameContent=True):
    """Write entire file. Defaults to utf-8."""
    if 'b' not in mode and encoding==None:
        encoding = 'utf-8'
    
    if skipIfSameContent and isFile(path):
        assertTrue(mode == 'w' or mode == 'wb')
        currentContent = readAll(path, mode=mode.replace('w', 'r'), encoding=encoding)
        if currentContent == txt:
            if updateTimeIfSameContent:
                setLastModifiedTime(path, getNowAsMillisTime(), units=TimeUnits.Milliseconds)
            return False

    with open(path, mode, encoding=encoding) as f:
        f.write(txt)
        return True

def isEmptyDir(dir):
    return len(os.listdir(dir)) == 0
    
def getDirectorySizeRecurse(dir, followSymlinks=False, fnFilterDirs=None, fnDirectExceptionsTo=None):
    from .m2_files_listing import recurseFileInfo
    total = 0
    for obj in recurseFileInfo(dir, followSymlinks=followSymlinks,
            fnFilterDirs=fnFilterDirs, fnDirectExceptionsTo=fnDirectExceptionsTo):
        total += obj.size()
    return total

def fileContentsEqual(f1, f2):
    import filecmp
    return filecmp.cmp(f1, f2, shallow=False)

