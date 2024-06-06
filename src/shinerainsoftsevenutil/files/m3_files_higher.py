

import subprocess
import shutil as _shutil
from contextlib import ExitStack as _ExitStack

from .m2_files_listing import *

def openDirectoryInExplorer(path):
    "Open directory in operating system, like finder or windows explorer."
    assert isDir(path), 'not a path? ' + path
    if sys.platform.startswith('win'):
        assert '^' not in path and '"' not in path, 'path cannot contain ^ or "'
        args = ['cmd', '/c', 'start', 'explorer.exe', path]
        run(args, shell=True, captureOutput=False, wait=False)
    else:
        # on macos, open should work.
        for candidate in ['xdg-open', 'nautilus', 'open']:
            pathBin = findBinaryOnPath(candidate)
            if pathBin:
                args = [pathBin, path]
                run(
                    args,
                    shell=False,
                    createNoWindow=False,
                    throwOnFailure=False,
                    captureOutput=False,
                    wait=False,
                )
                return
        raise RuntimeError('unable to open directory.')

def openUrl(url, filterChars=True):
    import webbrowser

    prefix = None
    if url.startswith('http://'):
        prefix = 'http://'
    elif url.startswith('https://'):
        prefix = 'https://'
    else:
        # block potentially risky file:// links
        assertTrue(False, 'url did not start with http')

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
    "this even adds a .exe on windows platforms"
    return _shutil.which(name)

def hasherFromString(s):
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
        try:
            from crc64iso.crc64iso import crc64_pair, format_crc64_pair
        except ImportError:
            assertTrue(False, 'To use this feature, you must install the crc64iso module.')

        cur = None
        while True:
            # update the hash with the contents of the file
            buffer = f.read(buffersize)
            if not buffer:
                break
            cur = crc64_pair(buffer, cur)
        return format_crc64_pair(cur)
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
    "extract the url from a windows .url file"
    assertEq('.url', splitExt(path)[1].lower())
    s = readAll(path, mode='r')
    lines = s.split('\n')
    for line in lines:
        if line.startswith('URL='):
            return line[len('URL=') :]
    raise RuntimeError('no url seen in ' + path)

def windowsUrlFileWrite(path, url):
    "create a windows .url file"
    assertTrue(len(url) > 0)
    assertTrue(not exists(path), 'file already exists at', path)
    s = '[InternetShortcut]\n'
    s += 'URL=%s\n' % url
    writeAll(path, s)

def runWithoutWait(listArgs):
    "run process without waiting for completion"
    p = subprocess.Popen(listArgs, shell=False)
    return p.pid

def runWithTimeout(
    args,
    *,
    shell=False,
    createNoWindow=True,
    throwOnFailure=True,
    captureOutput=True,
    timeoutSeconds=None,
    addArgs=None,
):
    """Run a process, with a timeout.
    on some windows IDEs, starting a process visually shows a black window appearing,
    so can pass createNoWindow to prevent this.
    returns tuple (returncode, stdout, stderr)"""
    addArgs = addArgs if addArgs else {}

    assertTrue(
        throwOnFailure is True or throwOnFailure is False or throwOnFailure is None,
        "we don't yet support custom exception types set here, you can use CalledProcessError",
    )

    retcode = -1
    stdout = None
    stderr = None
    if sys.platform.startswith('win') and createNoWindow:
        addArgs['creationflags'] = 0x08000000

    ret = subprocess.run(
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
    by default throws if the process fails (return code is nonzero).
    returns tuple (returncode, stdout, stderr)"""

    if confirmExists:
        assertTrue(
            isFile(listArgs[0]) or
            'which' not in dir(_shutil) or
            _shutil.which(listArgs[0]) or
            shell,
            'file not found?',
            listArgs[0],
        )

    kwargs = {}

    if sys.platform.startswith('win') and createNoWindow:
        kwargs['creationflags'] = 0x08000000

    if captureOutput and not wait:
        raise ValueError('captureOutput implies wait')

    if throwOnFailure and not wait:
        raise ValueError('throwing on failure implies wait')

    retcode = -1
    stdout = None
    stderr = None

    if captureOutput:
        sp = subprocess.Popen(
            listArgs, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs
        )

        comm = sp.communicate()
        stdout = comm[0]
        stderr = comm[1]
        retcode = sp.returncode
        if stripText:
            stdout = stdout.rstrip()
            stderr = stderr.rstrip()

    else:
        with _ExitStack() as cleanupTasks:
            if silenceOutput:
                stdoutArg = open(os.devnull, 'wb')  # noqa
                stderrArg = open(os.devnull, 'wb')  # noqa
                cleanupTasks.push(stdoutArg)
                cleanupTasks.push(stderrArg)
            else:
                stdoutArg = None
                stderrArg = None

                if wait:
                    retcode = subprocess.call(
                        listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs
                    )
                else:
                    subprocess.Popen(
                        listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs
                    )

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

