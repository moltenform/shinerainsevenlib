
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import enum as _enum
import zipfile as _zipfile
import os as _os
import sys as _sys

from . import plugin_compression_7z as _plugin_compression_7z
from . import plugin_compression_rar as _plugin_compression_rar
from .. import files as _files
from .. import core as _srss
from ..core import assertTrue, getRandomString
from . import plugin_fileexts

class ZipMethods(_enum.IntEnum):
    store = _zipfile.ZIP_STORED
    deflate = _zipfile.ZIP_DEFLATED
    lzma = _zipfile.ZIP_LZMA

class Strength(_enum.StrEnum):
    max = _enum.auto()
    strong = _enum.auto()
    default = _enum.auto()
    store = _enum.auto()

paramsZip = {}

# max compression (slow)
paramsZip[Strength.max] = '-tzip,-mx=9,-mm=Deflate,-mfb=258,-mpass=15'
# strong compression
paramsZip[Strength.strong] = '-tzip,-mx=9'
# 7z's default compression
paramsZip[Strength.default] = '-tzip'
# store
paramsZip[Strength.store] = '-tzip,-mx=0'

params7z = {}

# max compression (slow)
# for a 2gb file this takes 14gb ram to compress, for machines with 16gb ram this is about the max.
# confirmed will only need 2gb ram to decompress, though. (used sysinternals to see peak private bytes)
# for 7z (unlike rar), it's fine to use a very large dict size for small input because
# when decompressing, the full 1.5gb is not allocated in ram unless there are actually big files.
params7z[Strength.max] = (
    '-t7z,-mx=9,-mfb=273,-myx=9,-mmt,-mmtf,-md=1536m,-mmf=bt3,-mqs=on,-mmc=10000'
)
# strong compression
# an alternative is '-t7z,-md=31,-mmf=bt3,-mmc=10000,-mpb=0,-mlc=0'
# in rare cases this can be better, usually though it is just slower and worse
params7z[Strength.strong] = '-t7z,-m0=lzma,-mx=9,-mfb=64,-md=256m,-ms=on'
# 7z's default compression
params7z[Strength.default] = '-t7z'
# store
params7z[Strength.store] = '-t7z,-mx=0'

# Documentation on additional switches, and my notes
# -m0=lzma2 (default)   method=lzma2
# -mx=9        sets strength to max
# -myx=9      sets file analysis to max to set filtes
#     (e.g. detects exe files and gives them a filter to convert addresses for better compression,
#     delta filter can be better for wav)
# -ms=on       use solid mode (use default block size)
# -mqs=on      sort files by extension when adding in solid mode
# -mf=on (default) use filters
# -mmt=2   use 2 threads (can also be off,on) (in mx=9 seems not to have effect)
# -mtf=on   use multithread for filters
# -ma=1 (default) don't use fast mode
# -md=31 set dictionary size to 2gb
# -md=1536m set dictionary to 1.5Gb
# -mmf=bt3 select which match finder
#     (default bt4 is a bit better but slower which means -mmc needs to be lower)
# -mmc=10000 number of cycles for match finder
# -mfb=273 set fast bytes to max
# -mlc=0 literal context bits (high bits of previous literal). 0 to 8. Default=3. Sometimes lc=4 gives gain for big files.
# -mlp=0 (default) literal lowbits. for 32-bit periodical data you can lp=2 in which case it'd be better to set lc=0.
# -mpb=0 Sets the number of pos bits (low bits of current position). 0 to 4. Default=2.
#     Usually, text files benefit from lower pb and higher lc (lc+lp must not exceed 4 for LZMA2)
#     best lp value is almost always zero. for COFF files try pb1; for Windows Installer try pb3 and nonzero lp.
#     We use the default solid block size, which for mx=9 is around 4gb
# note that 7z cannot write a 7z or zip to stdout, only formats like gz.
# 7z e extracts to current directory (ignoring path info in archive)
# 7z x extracts with full paths

def addAllToZip(
    inPath,
    zipPath,
    method=ZipMethods.deflate,
    alreadyCompressedAsStore=False,
    creatingNewArchive=True,
    pathPrefix=None,
    recurse=True,
    **kwargs,
):
    if creatingNewArchive:
        assertTrue(not _files.exists(zipPath), 'already exists')

    def getCompressionMethod(path):
        if (
            alreadyCompressedAsStore and
            _files.getExt(path, removeDot=False) in plugin_fileexts.alreadyCompressedExt
        ):
            return _zipfile.ZIP_STORED
        else:
            assertTrue(
                method is not None, 'invalid method (note that ZIP_LZMA is not always available)'
            )
            assertTrue(
                isinstance(method, int), 'please specify ZipMethods.deflate instead of "deflate"'
            )
            return method

    assertTrue(not inPath.endswith('/') and not inPath.endswith('\\'))
    with _zipfile.ZipFile(zipPath, 'a') as zip:
        if _files.isFile(inPath):
            compressionMethod = getCompressionMethod(inPath)
            zip.write(
                inPath, (pathPrefix or '') + _files.getName(inPath), compress_type=compressionMethod
            )
        elif _files.isDir(inPath):
            itr = (
                _files.recurseFiles(inPath, **kwargs)
                if recurse
                else _files.listfiles(inPath, **kwargs)
            )
            for f, _short in itr:
                assertTrue(f.startswith(inPath))
                shortname = f[len(inPath) + 1 :]
                compressionMethod = getCompressionMethod(f)
                assertTrue(shortname, 'needs shortname')
                if pathPrefix is None:
                    innerPath = _files.getName(inPath) + '/' + shortname
                else:
                    innerPath = pathPrefix + shortname
                zip.write(f, innerPath, compress_type=compressionMethod)
        else:
            raise RuntimeError('not found: ' + inPath)

def getContents(
    archive, verbose=True, silenceWarnings=False, pword=None, okToFallbackTo7zForRar=False
):
    results = None
    if archive.lower().endswith('.rar'):
        if _files.exists(_plugin_compression_rar.getRarPath()):
            results = _plugin_compression_rar.getContentsViaRar(
                archive, verbose, silenceWarnings, pword=pword
            )
        else:
            assertTrue(okToFallbackTo7zForRar, 'rar not found for a rar file')

    if not results:
        results = _plugin_compression_7z._getContentsVia7z(
            archive, verbose, silenceWarnings, pword=pword
        )

    for item in results:
        assertTrue(item.get('Path'), 'all items must have a path', item)

        # 7z doesn't include a crc for empty _files, so add one.
        if _srss.parseIntOrFallback(item.get('Size')) == 0 and (
            not item.get('CRC') or item.get('CRC') == '--no crc found'
        ):
            item['CRC'] = '00000000'

    return results

def _getRunCommandCommonTempFile(path, preferEphemeral=False, prefix='runCommandCommon'):
    outExtension = _files.getExt(path, removeDot=False)
    tempOutFilename = rf'{prefix}{_os.getpid()}_{getRandomString()}{outExtension}'
    dirPath = _srss.getSoftTempDir(path, preferEphemeral=preferEphemeral)
    return _files.join(dirPath, tempOutFilename)

def runProcessThatCreatesOutput(
    listArgs,
    outPath,
    *,
    inPath=None,
    sizeMustBeGreaterThan=0,
    copyLastModTimeFromInput=False,
    handleUnicodeInputs=False,
):
    """
    Writes to a temp location first,
    1) no risk of getting a half-made file (like if user hits ctrl-c halfway through).
    2) handles unicode output names even if the external tool doesn't.
    Example:
    runProcessThatCreatesOutput(['magick', 'convert', '%input%', '%output%'], inPath='a.bmp', outPath='b.png')
    """
    with _srss.CleanupTempFilesOnException() as cleanup:
        assertTrue(not _files.exists(outPath), 'output already there')
        tmpOutPath = _getRunCommandCommonTempFile(outPath)
        assertTrue(not _files.exists(tmpOutPath), 'tmpOutPath already there')
        cleanup.registerTempFile(tmpOutPath)

        inPathToUse = inPath
        if (
            handleUnicodeInputs and
            _sys.platform.startswith('win') and
            _srss.containsNonAscii(inPath)
        ):
            inPathToUse = _getRunCommandCommonTempFile(inPath, 'runCommandCommonInput')
            assertTrue(not _files.exists(inPathToUse), 'inPathToUse already there')
            cleanup.registerTempFile(inPathToUse)
            _files.copy(inPath, inPathToUse, True)

        transformedArgs = list(listArgs)
        for i in range(len(transformedArgs)):
            transformedArgs[i] = (
                transformedArgs[i].replace('%input%', inPathToUse).replace('%output%', tmpOutPath)
            )

        _files.run(transformedArgs)
        assertTrue(_files.isFile(tmpOutPath), 'output not created', transformedArgs)
        assertTrue(
            _files.getSize(tmpOutPath) > sizeMustBeGreaterThan, 'output too small', transformedArgs
        )
        if copyLastModTimeFromInput:
            lmt = _files.getLastModTime(inPath)
            _files.setLastModTime(tmpOutPath, lmt)

        _files.move(tmpOutPath, outPath, False)
