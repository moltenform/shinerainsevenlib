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
isDir = os.path.isDir
isFile = os.path.isFile
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
    try:
        os.makedirs(s)
    except OSError:
        if isDir(s):
            return
        else:
            raise

def ensureEmptyDirectory(d):
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

def copy(srcfile, destfile, overwrite, doTrace=False,
        useDestModifiedTime=False, createParent=False):
    if not isFile(srcfile):
        raise IOError('source path does not exist or is not a file')

    toSetModTime = None
    if useDestModifiedTime and exists(destfile):
        assertTrue(isFile(destfile), 'not supported for directories')
        toSetModTime = getLastModifiedTime(destfile, units=TimeUnits.Nanoseconds)

    if doTrace:
        trace('copy()', srcfile, destfile)

    if createParent and not exists(getParent(destfile)):
        makeDirs(getParent(destfile))

    if srcfile == destfile:
        pass
    elif sys.platform.startswith('win'):
        from ctypes import windll, c_wchar_p, c_int, GetLastError
        failIfExists = c_int(0) if overwrite else c_int(1)
        res = windll.kernel32.CopyFileW(c_wchar_p(srcfile), c_wchar_p(destfile), failIfExists)
        if not res:
            err = GetLastError()
            raise IOError('CopyFileW failed (maybe dest already exists?) err=%d' % err +
                getPrintable(srcfile + '->' + destfile))
    else:
        if overwrite:
            shutil.copy(srcfile, destfile)
        else:
            _copyFilePosixWithoutOverwrite(srcfile, destfile)

    assertTrue(exists(destfile))
    if toSetModTime:
        setLastModifiedTime(destfile, toSetModTime, units=TimeUnits.Nanoseconds)

def move(srcfile, destfile, overwrite, warnBetweenDrives=False,
        doTrace=False, allowDirs=False, useDestModifiedTime=False, createParent=False):
    if not exists(srcfile):
        raise IOError('source path does not exist')
    if not allowDirs and not isFile(srcfile):
        raise IOError('source path does not exist or is not a file')

    if doTrace:
        trace('move()', srcfile, destfile)

    if createParent and not exists(getParent(destfile)):
        makeDirs(getParent(destfile))

    if srcfile == destfile:
        pass
    elif sys.platform.startswith('win'):
        _moveFileWin(srcfile, destfile)

    elif sys.platform.startswith('linux') and overwrite:
        os.rename(srcfile, destfile)
    else:
        copy(srcfile, destfile, overwrite)
        os.unlink(srcfile)

    assertTrue(exists(destfile))

def _moveFileWin():
    from ctypes import windll, c_wchar_p, c_int, GetLastError
    ERROR_NOT_SAME_DEVICE = 17
    flags = 0
    flags |= 1 if overwrite else 0
    flags |= 0 if warnBetweenDrives else 2
    res = windll.kernel32.MoveFileExW(c_wchar_p(srcfile), c_wchar_p(destfile), c_int(flags))
    
    if not res:
        err = GetLastError()
        if err == ERROR_NOT_SAME_DEVICE and warnBetweenDrives:
            rinput('Note: moving file from one drive to another. ' +
                '%s %s Press Enter to continue.\r\n'%(srcfile, destfile))
            return move(srcfile, destfile, overwrite, warnBetweenDrives=False)

        raise IOError('MoveFileExW failed (maybe dest already exists?) err=%d' % err +
            getPrintable(srcfile + '->' + destfile))

def _copyFilePosixWithoutOverwrite(srcfile, destfile):
    # fails if destination already exist. O_EXCL prevents other files from writing to location.
    # raises OSError on failure.
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    file_handle = os.open(destfile, flags)
    with os.fdopen(file_handle, 'wb') as fdest:
        with open(srcfile, 'rb') as fsrc:
            while True:
                buffer = fsrc.read(64 * 1024)
                if not buffer:
                    break
                fdest.write(buffer)

# "millistime" is number of milliseconds past epoch (unix time * 1000)
# I recomend using this as a a way to store times.

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
    return _getStatTime(path, 'st_mtime_ns', 'st_mtime')

def getCTime(path, units=TimeUnits.Seconds):
    return _getStatTime(path, 'st_ctime_ns', 'st_ctime')
    
def getATime(path, units=TimeUnits.Seconds):
    return _getStatTime(path, 'st_atime_ns', 'st_atime')


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

# unicodetype can be utf-8, utf-8-sig, etc.
def readAll(path, mode='r', encoding=None):
    if 'b' not in mode and encoding==None:
        encoding = 'utf-8'
    with open(path, mode, encoding=encoding) as f:
        return f.read()

# unicodetype can be utf-8, utf-8-sig, etc.
def writeAll(path, txt, mode='w', unicodetype=None, encoding=None, skipIfSameContent=False, updateTimeIfSameContent=True):
    if 'b' not in mode and encoding==None:
        encoding = 'utf-8'
    
    if skipIfSameContent and isFile(path):
        assertTrue(mode == 'w' or mode == 'wb')
        currentContent = readAll(path, mode.replace('w', 'r'), unicodetype, encoding)
        if currentContent == txt:
            if updateTimeIfSameContent:
                setLastModifiedTime(path, getNowAsMillisTime(), units=TimeUnits.Milliseconds)
            return False

    with open(path, mode, encoding=encoding) as f:
        f.write(txt)
        return True

def isEmptyDir(dir):
    return len(os.listdir(dir)) == 0
    
def getSizeRecurse(dir, followSymlinks=False, fnFilterDirs=None, fnDirectExceptionsTo=None):
    total = 0
    for obj in recurseFileInfo(dir, followSymlinks=followSymlinks,
            fnFilterDirs=fnFilterDirs, fnDirectExceptionsTo=fnDirectExceptionsTo):
        total += obj.size()
    return total

def fileContentsEqual(f1, f2):
    import filecmp
    return filecmp.cmp(f1, f2, shallow=False)



