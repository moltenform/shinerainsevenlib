# shinerainsoftsevencommon
# Released under the LGPLv3 License
from .files_listing import *
import subprocess

def openDirectoryInExplorer(path):
    assert isdir(path), 'not a path? ' + path
    if sys.platform.startswith('win'):
        assert '^' not in path and '"' not in path, 'path cannot contain ^ or "'
        runWithoutWaitUnicode([u'cmd', u'/c', u'start', u'explorer.exe', path])
    else:
        for candidate in ['xdg-open', 'nautilus']:
            pathBin = findBinaryOnPath(candidate)
            if pathBin:
                args = [pathBin, path]
                run(args, shell=False, createNoWindow=False, throwOnFailure=False, captureOutput=False, wait=False)
                return
        raise RuntimeError('unable to open directory.')

def openUrl(url, filter=True):
    import webbrowser
    if url.startswith('http://'):
        prefix = 'http://'
    elif url.startswith('https://'):
        prefix = 'https://'
    else:
        assertTrue(False, 'url did not start with http')

    if filter:
        url = url[len(prefix):]
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
    # like `which`
    def existsAsExe(dir, name):
        f = join(dir, name)
        if os.path.isfile(f):
            return f
        if sys.platform.startswith('win'):
            if os.path.isfile(f + '.exe'):
                return f + '.exe'
            if os.path.isfile(f + '.cmd'):
                return f + '.cmd'
            if os.path.isfile(f + '.com'):
                return f + '.com'
            if os.path.isfile(f + '.bat'):
                return f + '.bat'
        return None

    # handle "./binaryname"
    if os.sep in name:
        return existsAsExe('.', name) if existsAsExe('.', name) else None

    # handle "binaryname"
    for path in os.environ["PATH"].split(os.pathsep):
        if path and existsAsExe(path, name):
            return existsAsExe(path, name)

    return None

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

# default to 256kb buffer.
def computeHashBytes(b, hasher='sha1', buffersize=0x40000):
    import io
    with io.BytesIO(b) as f:
        return _computeHashImpl(f, hasher, buffersize)

def computeHash(path, hasher='sha1', buffersize=0x40000):
    with open(path, 'rb') as f:
        return _computeHashImpl(f, hasher, buffersize)

def _computeHashImpl(f, hasher, buffersize=0x40000):
    if hasher == 'crc32':
        import zlib
        crc = zlib.crc32(bytes(), 0)
        while True:
            # update the hash with the contents of the file
            buffer = f.read(buffersize)
            if not buffer:
                break
            crc = zlib.crc32(buffer, crc)
        crc = crc & 0xffffffff
        return '%08x' % crc
    elif hasher == 'crc64':
        from crc64iso.crc64iso import crc64_pair, format_crc64_pair
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
    assertEq('.url', os.path.splitExt(path)[1].lower())
    s = readAll(path, mode='r')
    lines = s.split('\n')
    for line in lines:
        if line.startswith('URL='):
            return line[len('URL='):]
    raise RuntimeError('no url seen in ' + path)

def windowsUrlFileWrite(path, url):
    assertTrue(len(url) > 0)
    assertTrue(not exists(path), 'file already exists at', path)
    try:
        url.encode('ascii')
    except e:
        if isinstance(e, UnicodeEncodeError):
            raise RuntimeError('can\'t support a non-ascii url' + url + ' ' + path)
        else:
            raise

    s = '[InternetShortcut]\n'
    s += 'URL=%s\n' % url
    writeAll(path, s)

def runWithoutWait(listArgs):
    p = subprocess.Popen(listArgs, shell=False)
    return p.pid

# returns tuple (returncode, stdout, stderr)
def runWithTimeout(args, *, shell=False, createNoWindow=True,
                  throwOnFailure=True, captureOutput=True, timeoutSeconds=None, addArgs=None):
    addArgs = addArgs if addArgs else {}
    
    assertTrue(throwOnFailure is True or throwOnFailure is False or throwOnFailure is None,
        "we don't yet support custom exception types set here, you can use CalledProcessError")

    retcode = -1
    stdout = None
    stderr = None
    if sys.platform.startswith('win') and createNoWindow:
        addArgs['creationflags'] = 0x08000000

    ret = subprocess.run(args, capture_output=captureOutput, shell=shell, timeout=timeoutSeconds,
        check=throwOnFailure, **addArgs)

    retcode = ret.returncode
    if captureOutput:
        stdout = ret.stdout
        stderr = ret.stderr
    
    return retcode, stdout, stderr

# returns tuple (returncode, stdout, stderr)
def run(listArgs, *, shell=False, createNoWindow=True,
        throwOnFailure=RuntimeError, stripText=True, captureOutput=True, silenceOutput=False,
        wait=True):
    
    assertTrue(isFile(listArgs[0]) or 'which' not in dir(shutil) or shutil.which(listArgs[0]) or shell, 'file not found?', listArgs[0])
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
        sp = subprocess.Popen(listArgs, shell=shell,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

        comm = sp.communicate()
        stdout = comm[0]
        stderr = comm[1]
        retcode = sp.returncode
        if stripText:
            stdout = stdout.rstrip()
            stderr = stderr.rstrip()

    else:
        if silenceOutput:
            stdoutArg = open(os.devnull, 'wb')
            stderrArg = open(os.devnull, 'wb')
        else:
            stdoutArg = None
            stderrArg = None

        if wait:
            retcode = subprocess.call(listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs)
        else:
            subprocess.Popen(listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs)

    if throwOnFailure and retcode != 0:
        if throwOnFailure is True:
            throwOnFailure = RuntimeError

        exceptionText = 'retcode is not 0 for process ' + \
            str(listArgs) + '\nretcode was ' + str(retcode) + \
            '\nstdout was ' + str(stdout) + \
            '\nstderr was ' + str(stderr)
        raise throwOnFailure(getPrintable(exceptionText))

    return retcode, stdout, stderr


