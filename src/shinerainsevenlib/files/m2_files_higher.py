
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import sys as _sys
import os as _os
import subprocess as _subprocess
import shutil as _shutil
from ..core import assertEq as _assertEq

from .m1_files_listing import *
from ..core import (
    alert as _alert,
    trace as _trace,
    assertTrue as _assertTrue,
)

def openDirectoryInExplorer(path):
    "Open directory in operating system, like finder or windows explorer."
    assert isDir(path), 'not a path? ' + path
    if _sys.platform.startswith('win'):
        assert '^' not in path and '"' not in path, 'path cannot contain ^ or "'
        args = ['cmd', '/c', 'start', 'explorer.exe', path]
        return run(args, shell=True, captureOutput=False, throwOnFailure=False, wait=False)
    else:
        # on mac_os, there's usually 'open'.
        for candidate in ['xdg-open', 'nautilus', 'open']:
            pathBin = findBinaryOnPath(candidate)
            if pathBin:
                args = [pathBin, path]
                return run(
                    args,
                    shell=False,
                    createNoWindow=False,
                    throwOnFailure=False,
                    captureOutput=False,
                    wait=False,
                )
                
        raise RuntimeError('unable to open directory.')

def openUrl(url, filterChars=True):
    "Open a url in the default browser"
    import webbrowser

    prefix = None
    if url.startswith('http://'):
        prefix = 'http://'
    elif url.startswith('https://'):
        prefix = 'https://'
    else:
        # block potentially risky file:// links
        _assertTrue(False, 'url did not start with http')

    if filterChars:
        url = url[len(prefix) :]
        url = url.replace('%', '%25')
        url = url.replace('&', '%26')
        url = url.replace('|', '%7C')
        url = url.replace('\\', '%5C')
        url = url.replace('^', '%5E')
        url = url.replace('"', '%22')
        url = url.replace("'", '%27')
        url = url.replace('>', '%3E')
        url = url.replace('<', '%3C')
        url = url.replace(' ', '%20')
        url = prefix + url

    webbrowser.open(url, new=2)

def findBinaryOnPath(name):
    """Works like 'which' on linux; finds the path to a binary executable.
    
    For example, notepad.exe -> c:\\windows\\system32\\notepad.exe.

    This even knows about .bat and .exe on windows platforms"""
    if _os.path.isabs(name) and _os.path.isfile(name):
        return name
    
    return _shutil.which(name)

def hasherFromString(s):
    """Get a hash function from a string. If you've
    installed xxhash, you can use 'xxhash_32' and 'xxhash_64' here."""
    import hashlib

    if s == 'sha1':
        return hashlib.sha1()
    elif s == 'sha224':
        return hashlib.sha224()
    elif s == 'sha256':
        return hashlib.sha256()
    elif s == 'sha384':
        return hashlib.sha384()
    elif s == 'sha512':
        return hashlib.sha512()
    elif s == 'blake2b':
        return hashlib.blake2b()
    elif s == 'blake2s':
        return hashlib.blake2s()
    elif s == 'md5':
        return hashlib.md5()
    elif s == 'sha3_224':
        return hashlib.sha3_224()
    elif s == 'sha3_256':
        return hashlib.sha3_256()
    elif s == 'sha3_384':
        return hashlib.sha3_384()
    elif s == 'sha3_512':
        return hashlib.sha3_512()
    elif s == 'shake_128':
        return hashlib.shake_128()
    elif s == 'shake_256':
        return hashlib.shake_256()
    elif s == 'xxhash_32':
        import xxhash

        return xxhash.xxh32()
    elif s == 'xxhash_64':
        import xxhash

        return xxhash.xxh64()
    else:
        raise ValueError('Unknown hash type ' + s)

defaultBufSize = 0x40000  # 256kb
"Buffer size, in bytes. :meta private:"

def computeHashBytes(b, hasher='sha1', buffersize=defaultBufSize):
    "Get hash of a bytes object, or a crc32"
    import io

    with io.BytesIO(b) as f:
        return _computeHashImpl(f, hasher, buffersize)

def computeHash(path, hasher='sha1', buffersize=defaultBufSize):
    "Get hash of file, or a crc32"
    with open(path, 'rb') as f:
        return _computeHashImpl(f, hasher, buffersize)

def _computeHashImpl(f, hasher, buffersize=defaultBufSize):
    if hasher == 'crc32':
        import zlib

        crc = zlib.crc32(b'', 0)
        while True:
            # update the hash with the contents of the file
            buffer = f.read(buffersize)
            if not buffer:
                break
            crc = zlib.crc32(buffer, crc)

        crc = crc & 0xFFFFFFFF
        return '%08x' % crc
    elif hasher == 'crc64':
        # at first this used crc64iso.crc64iso, but the values it gave
        # didn't line up with any other standard I could find. currently using
        # the crc package which has results that line up with other websites.
        # This crc seems to be called "CRC-64/ECMA-182".
        
        try:
            from crc import Crc64, Register
        except ImportError:
            _assertTrue(False, 'To use this feature, you must install "crc" from pip.')
        
        register = Register(Crc64.CRC64)
        register.init()
        while True:
            # update the hash with the contents of the file
            buffer = f.read(buffersize)
            if not buffer:
                break
            register.update(buffer)
        
        result = register.digest()
        result = result & 0xFFFFFFFFFFFFFFFF
        return f"{result:016x}"
    else:
        if isinstance(hasher, str):
            hasher = hasherFromString(hasher)

        while True:
            # update the hash with the contents of the file
            buffer = f.read(buffersize)
            if not buffer:
                break
            hasher.update(buffer)
        return hasher.hexdigest()

def windowsUrlFileGet(path):
    "Extract the url from a windows .url file"
    _assertEq('.url', splitExt(path)[1].lower())
    s = readAll(path, mode='r')
    lines = s.split('\n')
    for line in lines:
        if line.startswith('URL='):
            return line[len('URL=') :]
    
    raise RuntimeError('no url seen in ' + path)

def windowsUrlFileWrite(path, url):
    "Create a windows .url file"
    _assertTrue(len(url) > 0)
    _assertTrue(not exists(path), 'file already exists at', path)
    s = '[InternetShortcut]\n'
    s += 'URL=%s\n' % url
    writeAll(path, s)

def runWithoutWait(listArgs):
    "Run process without waiting for completion"
    p = _subprocess.Popen(listArgs, shell=False)
    return p.pid

def runWithTimeout(
    args,
    *,
    shell=False,
    createNoWindow=True,
    throwOnFailure=True,
    captureOutput=True,
    timeoutSeconds=None,
    stripText=True,
    addArgs=None,
):
    """Run a process, with a timeout.
    on some windows IDEs, starting a process visually shows a black window appearing,
    so can pass createNoWindow to prevent this.
    returns tuple (returncode, stdout, stderr)"""
    addArgs = addArgs if addArgs else {}

    _assertTrue(
        throwOnFailure is True or throwOnFailure is False or throwOnFailure is None,
        "we don't yet support custom exception types set here, you can use CalledProcessError",
    )

    retcode = -1
    stdout = None
    stderr = None
    if _sys.platform.startswith('win') and createNoWindow:
        addArgs['creationflags'] = 0x08000000

    ret = _subprocess.run(
        args,
        capture_output=captureOutput,
        shell=shell,
        timeout=timeoutSeconds,
        check=throwOnFailure,
        **addArgs,
    )

    retcode = ret.returncode
    if captureOutput:
        stdout = ret.stdout
        stderr = ret.stderr
        if stripText:
            stdout = stdout.rstrip()
            stderr = stderr.rstrip()

    return retcode, stdout, stderr

def run(
    listArgs,
    *,
    shell=False,
    createNoWindow=True,
    throwOnFailure=RuntimeError,
    stripText=True,
    captureOutput=True,
    silenceOutput=False,
    wait=True,
    confirmExists=False,
):
    """Run a process.
    on some windows IDEs, starting a process visually shows a black window appearing,
    so can pass createNoWindow to prevent this.

    By default throws if the process fails (return code is nonzero).
    
    returns tuple (returncode, stdout, stderr)"""

    if confirmExists:
        _assertTrue(
            isFile(listArgs[0]) or
            'which' not in dir(_shutil) or
            _shutil.which(listArgs[0]) or
            shell,
            'executable file not found?',
            listArgs[0],
        )

    kwargs = {}

    if _sys.platform.startswith('win') and createNoWindow:
        kwargs['creationflags'] = 0x08000000

    if captureOutput and not wait:
        raise ValueError('captureOutput implies wait')

    if throwOnFailure and not wait:
        raise ValueError('throwing on failure implies wait')

    retcode = -1
    stdout = None
    stderr = None

    if captureOutput:
        sp = _subprocess.Popen(
            listArgs, shell=shell, stdout=_subprocess.PIPE, stderr=_subprocess.PIPE, **kwargs
        )

        comm = sp.communicate()
        stdout = comm[0]
        stderr = comm[1]
        retcode = sp.returncode
        if stripText:
            stdout = stdout.rstrip()
            stderr = stderr.rstrip()

    else:
        stdoutArg = None
        stderrArg = None
        try:
            if silenceOutput:
                stdoutArg = open(_os.devnull, 'wb')  # noqa
                stderrArg = open(_os.devnull, 'wb')  # noqa

            if wait:
                retcode = _subprocess.call(
                    listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs
                )
            else:
                _subprocess.Popen(
                    listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs
                )
        finally:
            if stdoutArg is not None:
                stdoutArg.close()
            if stderrArg is not None:
                stderrArg.close()

    if throwOnFailure and retcode != 0:
        if throwOnFailure is True:
            throwOnFailure = RuntimeError

        exceptionText = (
            'retcode is not 0 for process ' +
            str(listArgs) +
            '\nretcode was ' +
            str(retcode) +
            '\nstdout was ' +
            str(stdout) +
            '\nstderr was ' +
            str(stderr)
        )
        raise throwOnFailure(srss.getPrintable(exceptionText))

    return retcode, stdout, stderr

def runPskill(processName, pathToPskill='pskill'):
    """Use pskill to terminate a process. processName like notepad.exe."""
    # use constants instead of importing winerror
    winerror_OK = 0
    winerror_ERROR_ACCESS_DENIED = 5
    winerror_ERROR_NOT_FOUND = 1168
    args = [pathToPskill, '-accepteula', processName]
    retcode, stderr, _stdout = run(args, throwOnFailure=None)
    if retcode == 0:
        return winerror_OK
    else:
        stderr = stderr.decode('utf-8')
        if '\nAccess is denied.' in stderr:
            return winerror_ERROR_ACCESS_DENIED
        elif '\nProcess does not exist.' in stderr:
            return winerror_ERROR_NOT_FOUND
        else:
            raise RuntimeError('pskill failed ' + stderr)

def makeShortcut(sourcePath, targetPath):
    "Create a symlink (or .lnk shortcut on Windows)"
    if _sys.platform.startswith('win'):
        import winshell
        winshell.CreateShortcut(sourcePath, targetPath)
    else:
        _os.symlink(sourcePath, targetPath)

def isSymlink(path):
    """Is the path a symlink.
    
    Confirmed works on Windows (where symlinks are rare but
    can be created with tools like ``mklink``)"""
    return _os.path.islink(path)

def _checkIfFileCanBeMovedInelegant(f):
    "locked by other process writing? robocopy doesn't handle this case well."
    tmpName = f + '~srsstemporyrename~'
    _assertTrue(not exists(tmpName), 'file already exists', tmpName)
    canMove = False
    try:
        move(f, tmpName, False)
    except OSError:
        # this is usually winerr 32, "held by other process"
        pass
    finally:
        if exists(tmpName):
            # undo our temporary name
            canMove = True
            move(tmpName, f, False)
    
    return canMove

def _checkIfSafeForRobocopy(srcRoot, destRoot):
    "Do two checks 1) can be moved 2) no type mismatches 3) are symlinks"
    if not exists(destRoot):
        return

    for f, _short in recurseFiles(destRoot, includeDirs=True, includeFiles=True):
        if isSymlink(f):
            raise RuntimeError('not-safe-for-robocopy: symlink in destination', f)
        
        versionInSrc = acrossDir(f, destRoot, srcRoot)
        if exists(versionInSrc):
            isDirInSrc = isDir(versionInSrc)
            isDirInDest = isDir(f)
            if isDirInSrc != isDirInDest:
                raise RuntimeError('not-safe-for-robocopy: type mismatch', f,)
            
            if not isDirInDest:
                if not _checkIfFileCanBeMovedInelegant(f):
                    raise RuntimeError('not-safe-for-robocopy: file handle prob locked', f,)

def runRsync(srcDir, destDir, deleteExisting, useRobocopy=False,
    robocopyExcludeFiles=None, robocopyExcludeDirs=None,
    excludeRelative=None, excludeWithName=None,
    throwOnFailure=True, checkExist=True, binPath=None):
    """Use rsync to copy files between directories.
    
    On Windows, if you do not have rsync, you can use the flag useRobocopy.
    
    Robocopy has separate robocopyExcludeFiles and robocopyExcludeDirs
    parameters because the semantics are different than rsync, e.g.
    in how they handle glob patterns and relative paths.
    
    robocopy does many retries on failure, which can appear as hangs,
    we work around this by proactively checking for problems like locked files
    in the destination. Setting retries to 0 could mask other problems."""
    # Specifying exclusions is complicated.
    # There's absolute paths, relative paths, glob patterns,
    # and "by name" (should "/XF foo.txt" also exclude "dir/subdir/foo.txt"?)
    # Best to separate based on platform because semantics differ.
    if checkExist:
        _assertTrue(isDir(srcDir), "not a dir", srcDir)
        _assertTrue(isDir(destDir), "not a dir", destDir)
    
    if useRobocopy:
        _assertTrue(not excludeRelative and not excludeWithName, 
            "Use robocopy-specific params")
        
        retcode, stdout, stderr = _runRobocopy(srcDir, destDir, 
            deleteExisting=deleteExisting, binPath=binPath,
            robocopyExcludeFiles=robocopyExcludeFiles, 
            robocopyExcludeDirs=robocopyExcludeDirs)
        
        isOk, status = interpretRobocopyErr(retcode)
    else:
        _assertTrue(not robocopyExcludeFiles and not robocopyExcludeDirs, 
            "Don't use robocopy-specific params")
        
        retcode, stdout, stderr = _runRsync(srcDir, destDir,
            deleteExisting=deleteExisting, binPath=binPath,
            excludeRelative=excludeRelative, excludeWithName=excludeWithName)
        
        isOk, status = interpretRsyncErr(retcode)
    
    if throwOnFailure and not isOk:
        raise OSFileRelatedError("Could not copy. " + str(retcode) +
            str(stdout) + str(stderr) + str(status))
    return retcode, stdout, stderr, status

def _runRobocopy(srcDir, destDir, deleteExisting,
    robocopyExcludeFiles=None, robocopyExcludeDirs=None, binPath=None):
    defaultToEmptyList = lambda lst: list(lst) if lst else []
    # we could use /r:0 to eliminate retries, but an
    # apparent bug in robocopy gives a success exit code,
    # so it's better to leave the current repeat-million-times
    # because at least it doesn't silently fail
    # (we use _checkIfSafeForRobocopy to work around known problems)
    args = []
    args.append(binPath or 'robocopy')
    args.append(srcDir)
    args.append(destDir)
    if deleteExisting:
        args.append('/MIR')
    
    args.append('/E')  # means 'copy all including empty dirs'
    for ex in defaultToEmptyList(robocopyExcludeFiles):
        args.append('/XF')
        args.append(ex)
    for ex in defaultToEmptyList(robocopyExcludeDirs):
        args.append('/XD')
        args.append(ex)
    
    # hack: robocopy has weird bugs where it overrides locked files -
    # it writes data there anyways. it also badly handles cases where a path represents
    # a directory on one side and a file on the other side.
    _checkIfSafeForRobocopy(srcDir, destDir)
    return run(args, throwOnFailure=False, confirmExists=True)

def _runRsync(srcDir, destDir, deleteExisting,
        excludeRelative=None, excludeWithName=None, binPath=None):

    defaultToEmptyList = lambda lst: list(lst) if lst else []
    args = []
    args.append(binPath or 'rsync')
    args.append('-az')
    if not srcDir.endswith('/'):
        # important: otherwise rsync might put files into a subdir
        srcDir += '/'

    if deleteExisting:
        args.append('--delete-after')
    for ex in defaultToEmptyList(excludeRelative):
        _assertTrue(not _os.path.isabs(ex), ex)
        args.append('--exclude=/' + ex)
    for ex in defaultToEmptyList(excludeWithName):
        _assertTrue(not _os.path.isabs(ex), ex)
        args.append('--exclude=' + ex)

    args.append(srcDir)
    args.append(destDir)
    return run(args, throwOnFailure=False, confirmExists=True)

def interpretRobocopyErr(code):
    ":meta private:"
    status = ''
    if code & 0x1:
        status += "One or more files were copied successfully (that is, new files have arrived).\n"
        code = code & ~0x1
    if code & 0x2:
        status += "Extra files or directories were detected.\n"
        code = code & ~0x2
    if code & 0x4:
        status += "Mismatched files or directories were detected.\n"
        code = code & ~0x4
    if code & 0x8:
        status += "Some files or directories could not be copied.\n"
    if code & 0x10:
        status += "Serious error.\n"
    isOk = code == 0
    return (isOk, status)

def interpretRsyncErr(code):
    ":meta private:"
    mapCode = {}
    mapCode[0] = (True, '')
    mapCode[1] = (False, "Syntax or usage error")
    mapCode[2] = (False, "Protocol incompatibility")
    mapCode[3] = (False, "Errors selecting input/output files, dirs")
    mapCode[4] = (False, "Action not supported, maybe by the client and not server")
    mapCode[5] = (False, "Error starting client-server protocol")
    mapCode[6] = (False, "Daemon unable to append to log-file")
    mapCode[10] = (False, "Error in socket I/O")
    mapCode[11] = (False, "Error in file I/O")
    mapCode[12] = (False, "Error in rsync protocol data stream")
    mapCode[13] = (False, "Errors with program diagnostics")
    mapCode[14] = (False, "Error in IPC code")
    mapCode[20] = (False, "Received SIGUSR1 or SIGINT")
    mapCode[21] = (False, "Some error returned by waitpid()")
    mapCode[22] = (False, "Error allocating core memory buffers")
    mapCode[23] = (False, "Partial transfer due to error")
    mapCode[24] = (False, "Partial transfer due to vanished source files")
    mapCode[25] = (False, "The --max-delete limit stopped deletions")
    mapCode[30] = (False, "Timeout in data send/receive")
    mapCode[35] = (False, "Timeout waiting for daemon connection")
    return mapCode.get(code, (False, "Unknown"))

