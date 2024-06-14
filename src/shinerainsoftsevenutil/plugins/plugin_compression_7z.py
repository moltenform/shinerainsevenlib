
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

from .plugin_fileexts import *
from .. import files
from .. import core as srss
from ..core import assertTrue, trace

def addAllTo7z(inPath, outPath, effort=None, multiThread='off', solid=True):
    from .plugin_compression import Strength, params7z, paramsZip, runProcessThatCreatesOutput

    if not effort:
        effort = Strength.Default

    assertTrue(not isinstance(inPath, list), "we don't yet support multiple items")
    assertTrue(outPath.endswith(('7z', 'zip')))
    if outPath.lower().endswith('.zip'):
        # zip format does not support solid
        assertTrue(not solid, 'not solid')
        opts = paramsZip[effort].split(',')
    else:
        opts = params7z[effort].split(',')

    args = [get7zExecutablePath(), 'a', '%output%']
    args.extend(['-mmt=' + multiThread])
    if opts:
        args.extend(opts)

    if not solid and not outPath.lower().endswith('.zip'):
        args.extend(['-ms=off'])

    args.extend(['%input%'])
    runProcessThatCreatesOutput(args, inPath=inPath, outPath=outPath)

def checkArchivePasswordVia7z(inPath, pword=None):
    args = [get7zExecutablePath(), 'l', getPlaceholderPword(pword), inPath]
    retcode, stdout, stderr = files.run(args, throwOnFailure=None)
    results = srss.Bucket(success=False, failedWrongPword=False, failedOtherReason=False, stdout=stdout, stderr=stderr)
    if retcode == 0:
        results.success = True
    elif b'Wrong password?' in stderr:
        results.failedWrongPword = True
    else:
        results.failedOtherReason = True
    return results

def checkArchiveIntegrityVia7z(inPath, pword=None):
    args = [get7zExecutablePath(), 't', getPlaceholderPword(pword), inPath]
    retcode, _stdout, stderr = files.run(args, throwOnFailure=None)
    if retcode == 0:
        return True
    elif b'Cannot open the file as archive' in stderr:
        return False
    elif b'Cannot open the file as [7z] archive' in stderr:
        return False
    elif b'Cannot open the file as [zip] archive' in stderr:
        return False
    elif b'ERROR: CRC Failed' in stderr:
        return False
    elif b'ERROR: Data Error' in stderr:
        return False
    else:
        assertTrue(False, 'failed to test archive', inPath, stderr)
        return None

def getPlaceholderPword(pword):
    # we send in a placeholder password to intentionally get an error
    # -- otherwise it will block on stdin!
    pword = pword or '(placeholder-password)'
    return '-p' + pword

def _processAttributes7z(item):
    isDir = 'D' in item.get('Attributes', '') or item.get('Folder', '').strip() == '+'
    return dict(
        Path=item.get('Path', ''),  # uses \ as dirsep
        Type='Directory' if isDir else 'File',  # .tar.gz does not have Attributes
        Modified=item.get('Modified', '--no modified found'),  # 2023-01-27 18:17:19.7498290
        CRC=item.get('CRC', '--no crc found'),
        Size=item.get('Size', '--no size found'),
        PackedSize=item.get('Packed Size', '--no packedsize found'),
        Raw=item,
    )

def getContentsVia7z(archive, verbose, silenceWarnings, pword=None):
    assertTrue(files.isFile(archive))
    assertTrue(verbose, 'we only support verbose listing')
    args = [get7zExecutablePath(), '-slt', 'l', getPlaceholderPword(pword), archive]
    _retcode, stdout, stderr = files.run(args)
    results = _getContentsVia7zImpl(stdout, stderr, archive, verbose, silenceWarnings)

    if len(results) == 1 and (
        isCompressedTarExtension(archive) or results[0]['Path'].endswith('.tar')
    ):
        assertTrue(files.isFile(archive))
        # detect a .tar.gz file and list the tar contents instead. use pipe so there's no disk used.
        # 7z does not seem to be able to list .tar.bz2 directly (unlike winrar), 
        # but it can list the inner tar after extracting, so it all still works.
        args = [
            get7zExecutablePath(),
            'x',
            archive,
            getPlaceholderPword(pword),
            '-so',
            '|',
            get7zExecutablePath(),
            'l',
            '-slt',
            '-ttar',
            '-si',
        ]
        _retcode, stdout, stderr = files.run(args, shell=True)
        results = _getContentsVia7zImpl(
            stdout, stderr, archive, verbose, silenceWarnings,
        )
    elif len(results) == 1 and (isSingleFileCompressionExtension(archive)):
        results = _handleSingleFileCase(archive, pword)

    return results

def _handleSingleFileCase(archive, pword):
    "Handle cases like example.gz"
    
    # get crc32 checksum of contents
    args = [
        get7zExecutablePath(),
        'x',
        archive,
        getPlaceholderPword(pword),
        '-so',
        '|',
        getCksumExecutablePath(),
    ]
    _retcode, stdout, _stderr = files.run(args, shell=True)
    stdout = stdout.decode('utf-8').strip()
    assertTrue(' ' in stdout)
    pts = stdout.replace('  ', ' ').split(' ')
    _unusableCrc32 = int(pts[0])
    countBytes = int(pts[1])

    # by convention, the 'filename' is just the input name minus extension
    innerFilename = files.splitExt(files.getName(archive))[0]
    _unusableRenderedCrc = ('%08x'%_unusableCrc32).upper()

    # Note: the crc given by cksum is not the same crc32 as used by zip.
    # solution: either have users install the unix tool named 'crc32'
    # or shell out to gzip in a clever way to retrieve its crc
    # from @robert on stackoverflow,
    # echo "abc" | gzip -1 -c | tail -c8 | hexdump -n4 -e '"%u"'
    # for now though I'll just leave without a checksum.
    mockItem = dict(Path=innerFilename, Size=countBytes)

    # to ensure consistency with code from when we really read a 7z,
    # call into the same processing function.
    return [_processAttributes7z(mockItem)]


def _getContentsVia7zImpl(stdout, _stderr, archive, _verbose, silenceWarnings):
    stdoutFull = stdout.decode('latin-1').replace('\r\n', '\n')
    marker = '\n----------\n'
    if marker not in stdoutFull:
        if files.getSize(archive) < 1024:
            trace('apparently an empty archive', archive)
            return []
        else:
            raise ValueError('output from 7z did not include', marker, archive)

    _header, stdout = stdoutFull.split('\n----------\n')
    results = []
    parts = stdout.split('\n\n')
    for part in parts:
        lines = part.split('\n')
        lines = [line for line in lines if line.strip()]
        if len(lines) == 1 and lines[0].strip().startswith('Warnings:'):
            if not silenceWarnings and not _isIgnorableWarning(stdoutFull):
                trace(lines[0], archive)
            continue

        result = {}
        results.append(result)
        for line in lines:
            if line.endswith(' ='):
                continue
            if not ' = ' in line:
                assertTrue(False, 'could not parse line', line, stdout)
            title, contents = line.split(' = ', 1)
            result[title.strip()] = contents.strip()
    return [_processAttributes7z(result) for result in results]

def _isIgnorableWarning(stdout):
    # having a file with .7z extension but is actually a .rar is confusing, but ok.
    if (
        '\nOpen WARNING: Cannot open the file as [7z] archive' in stdout and
        '\nType = Rar' in stdout and
        '\nWarnings: 1' in stdout
    ):
        return True
    else:
        return False

def get7zExecutablePath():
    from .plugin_configreader import getExecutablePathFromPrefs
    fallbackGuesses = [r"C:\Program Files (x86)\7-Zip\7z.exe",
                       r"C:\Program Files\7-Zip\7z.exe"]
    return getExecutablePathFromPrefs('7z', throwIfNotFound=True,fallbacksToTry=fallbackGuesses)

def getCksumExecutablePath():
    from .plugin_configreader import getExecutablePathFromPrefs
    return getExecutablePathFromPrefs('cksum', throwIfNotFound=True)
