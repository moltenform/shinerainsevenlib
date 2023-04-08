# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import sys
import os as _os
import shutil as _shutil
from .common_higher import *
from .common_util import *

rename = _os.rename
exists = _os.path.exists
join = _os.path.join
split = _os.path.split
splitext = _os.path.splitext
isdir = _os.path.isdir
isfile = _os.path.isfile
getsize = _os.path.getsize
rmdir = _os.rmdir
chdir = _os.chdir
sep = _os.path.sep
linesep = _os.linesep
abspath = _os.path.abspath
rmtree = _shutil.rmtree

def getparent(s):
    return _os.path.split(s)[0]

def getname(s):
    return _os.path.split(s)[1]

def createdtime(s):
    return _os.stat(s).st_ctime

def getext(s, removeDot=True):
    a, b = splitext(s)
    if removeDot and len(b) > 0 and b[0] == '.':
        return b[1:].lower()
    else:
        return b.lower()

def getwithdifferentext(s, ext_with_dot):
    parent, short = os.path.split(s)
    short_before_ext, short_ext = os.path.splitext(short)
    assertTrue(short_ext, s)
    if parent:
        with_trailing_slash = s[0:len(parent)+1]
        assertTrue(with_trailing_slash == parent+'/' or with_trailing_slash == parent+'\\')
        return with_trailing_slash + short_before_ext + ext_with_dot
    else:
        return short_before_ext + ext_with_dot

def delete(s, traceToStdout=False):
    if traceToStdout:
        trace('delete()', s)

    _os.unlink(s)

def deletesure(s, traceToStdout=False):
    if exists(s):
        delete(s, traceToStdout)

    assertTrue(not exists(s))

def makedirs(s):
    try:
        _os.makedirs(s)
    except OSError:
        if isdir(s):
            return
        else:
            raise

def ensureEmptyDirectory(d):
    if isfile(d):
        raise IOError('file exists at this location ' + d)

    if isdir(d):
        # delete all existing files in the directory
        for s in _os.listdir(d):
            if _os.path.isdir(join(d, s)):
                _shutil.rmtree(join(d, s))
            else:
                _os.unlink(join(d, s))

        assertTrue(isemptydir(d))
    else:
        _os.makedirs(d)

def copy(srcfile, destfile, overwrite, traceToStdout=False,
        useDestModifiedTime=False, createParent=False):
    if not isfile(srcfile):
        raise IOError('source path does not exist or is not a file')

    toSetModTime = None
    if useDestModifiedTime and exists(destfile):
        assertTrue(isfile(destfile), 'not supported for directories')
        toSetModTime = getModTimeNs(destfile)

    if traceToStdout:
        trace('copy()', srcfile, destfile)

    if createParent and not exists(getparent(destfile)):
        makedirs(getparent(destfile))

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
            _shutil.copy(srcfile, destfile)
        else:
            _copyFilePosixWithoutOverwrite(srcfile, destfile)

    assertTrue(exists(destfile))
    if toSetModTime:
        setModTimeNs(destfile, toSetModTime)

def move(srcfile, destfile, overwrite, warnBetweenDrives=False,
        traceToStdout=False, allowDirs=False, useDestModifiedTime=False, createParent=False):
    if not exists(srcfile):
        raise IOError('source path does not exist')
    if not allowDirs and not isfile(srcfile):
        raise IOError('source path does not exist or is not a file')

    toSetModTime = None
    if useDestModifiedTime and exists(destfile):
        assertTrue(isfile(destfile), 'not supported for directories')
        toSetModTime = getModTimeNs(destfile)

    if traceToStdout:
        trace('move()', srcfile, destfile)

    if createParent and not exists(getparent(destfile)):
        makedirs(getparent(destfile))

    if srcfile == destfile:
        pass
    elif sys.platform.startswith('win'):
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

    elif sys.platform.startswith('linux') and overwrite:
        _os.rename(srcfile, destfile)
    else:
        copy(srcfile, destfile, overwrite)
        _os.unlink(srcfile)

    assertTrue(exists(destfile))
    if toSetModTime:
        setModTimeNs(destfile, toSetModTime)

def _copyFilePosixWithoutOverwrite(srcfile, destfile):
    # fails if destination already exist. O_EXCL prevents other files from writing to location.
    # raises OSError on failure.
    flags = _os.O_CREAT | _os.O_EXCL | _os.O_WRONLY
    file_handle = _os.open(destfile, flags)
    with _os.fdopen(file_handle, 'wb') as fdest:
        with open(srcfile, 'rb') as fsrc:
            while True:
                buffer = fsrc.read(64 * 1024)
                if not buffer:
                    break
                fdest.write(buffer)

# "millistime" is number of milliseconds past epoch (unix time * 1000)

def getModTimeNs(path, asMillisTime=False):
    t = _os.stat(path).st_mtime_ns
    if asMillisTime:
        t = int(t / 1.0e6)
    return t

def getCTimeNs(path, asMillisTime=False):
    t = _os.stat(path).st_ctime_ns
    if asMillisTime:
        t = int(t / 1.0e6)
    return t

def getATimeNs(path, asMillisTime=False):
    t = _os.stat(path).st_atime_ns
    if asMillisTime:
        t = int(t / 1.0e6)
    return t

def setModTimeNs(path, mtime, asMillisTime=False):
    if asMillisTime:
        mtime *= 1e6
    atime = getATimeNs(path)
    _os.utime(path, ns=(atime, mtime))

def setATimeNs(path, atime, asMillisTime=False):
    if asMillisTime:
        atime *= 1e6
    mtime = getModTimeNs(path)
    _os.utime(path, ns=(atime, mtime))

def getFileLastModifiedTime(filepath):
    return _os.path.getmtime(filepath)

def setFileLastModifiedTime(filepath, lmt):
    curtimes = _os.stat(filepath)
    newtimes = (curtimes.st_atime, lmt)
    with open(filepath, 'ab'):
        _os.utime(filepath, newtimes)

def _openSupportingUnicode(s, mode, encoding):
    if encoding:
        # python 3-style
        return lambda: open(s, mode, encoding=encoding)
    else:
        return lambda: open(s, mode)

# unicodetype can be utf-8, utf-8-sig, etc.
def readall(s, mode='r', encoding=None):
    with _openSupportingUnicode(s, mode, encoding)() as f:
        return f.read()

# unicodetype can be utf-8, utf-8-sig, etc.
def writeall(s, txt, mode='w', unicodetype=None, encoding=None, skipIfSameContent=False, updateTimeIfSameContent=True):
    if skipIfSameContent and isfile(s):
        assertTrue(mode == 'w' or mode == 'wb')
        currentContent = readall(s, mode.replace('w', 'r'), unicodetype, encoding)
        if currentContent == txt:
            if updateTimeIfSameContent:
                setFileLastModifiedTime(s, getNowAsMillisTime() / 1000.0)
            return False

    with _openSupportingUnicode(s, mode, unicodetype, encoding)() as f:
        f.write(txt)
        return True

def isemptydir(dir):
    return len(_os.listdir(dir)) == 0
    
def getSizeRecurse(dir, followSymlinks=False, fnFilterDirs=None, fnDirectExceptionsTo=None):
    total = 0
    for obj in recursefileinfo(dir, followSymlinks=followSymlinks,
            fnFilterDirs=fnFilterDirs, fnDirectExceptionsTo=fnDirectExceptionsTo):
        total += obj.size()
    return total

def fileContentsEqual(f1, f2):
    import filecmp
    return filecmp.cmp(f1, f2, shallow=False)


