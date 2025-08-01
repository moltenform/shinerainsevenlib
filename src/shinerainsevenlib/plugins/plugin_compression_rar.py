
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import shutil
from .plugin_fileexts import *
from .. import files
from ..core import assertTrue

def addAllToRar(
    inPath, outPath, effort=None, formatVersion='4', dictSize=None, solid=True, pword=None
):
    "Create a rar or zip archive. inPath should be the path to a directory or file."
    from .plugin_compression import Strength, runProcessThatCreatesOutput

    if not effort:
        effort = Strength.Default

    assertTrue(formatVersion in ('4', '5'), 'formatVersion must be 4 or 5')
    assertTrue(not isinstance(inPath, list), "we don't yet support multiple items")
    if not dictSize:
        dictSize = '256m' if formatVersion == '5' else '4096k'

    assertTrue(outPath.lower().endswith('.rar') or outPath.lower().endswith('.zip'))
    args = [getRarExecutablePath(), 'a', '%output%']
    if solid:
        args.extend(['-s'])

    # 5 ("max") is still quite fast
    strEffort = '0' if effort == Strength.Store else '5'
    if outPath.lower().endswith('.rar'):
        args.extend(['-m' + strEffort])
        args.extend(['-ma' + formatVersion])
        args.extend(['-md' + dictSize])

    if pword:
        # hp encrypts both headers and files
        args.extend(['-hp' + pword])

    args.extend(['%input%'])
    runProcessThatCreatesOutput(args, inPath=inPath, outPath=outPath)

def getContentsViaRar(archive, verbose, _silenceWarnings, pword=None):
    """List contents of the zip, 7z, rar, or other type of archive.
    Details are provided about each item: ``Path, Type, Modified,
    CRC, Size, PackedSize, and Raw (raw data about the item)``"""
    from . import plugin_compression_7z

    assertTrue(files.isFile(archive))
    assertTrue(verbose, 'we only support verbose listing')
    args = [getRarExecutablePath(), 'lt', plugin_compression_7z.getPlaceholderPword(pword), archive]
    retcode, stdout, stderr = files.run(args, throwOnFailure=None)
    if retcode != 0 and b'Incorrect password for ' in stderr:
        # use an error message more similar to 7z
        raise RuntimeError(f'Wrong password? getContentsViaRar {args}')
    elif retcode != 0:
        raise RuntimeError(f'return code is not 0 when running getContentsViaRar {args}')

    stdout = stdout.decode('latin-1').replace('\r\n', '\n')
    results = []
    parts = stdout.split(' Name: ')
    parts.pop(0)  # just the header
    for part in parts:
        lines = part.split('\n')
        result = {}
        results.append(result)
        result['Path'] = lines[0].strip()
        for line in lines[1:]:
            if not line.strip():
                continue

            if not ': ' in line:
                assertTrue(False, 'could not parse line', line, stdout)
            title, contents = line.split(': ', 1)
            result[title.strip()] = contents.strip()
    return [processAttributesRar(result) for result in results]

def processAttributesRar(item):
    "Standardize the data coming in from rar"
    return dict(
        Path=item.get('Path', ''),  # uses \ as dirsep
        Type=item.get('Type', '--no type found'),  # File or Directory
        Modified=item.get('Modified', '--no modified found').split(',')[
            0
        ],  # 2023-02-02 12:56:05,673617400
        CRC=item.get('CRC32', '--no crc found'),
        Size=item.get('Size', '--no size found'),
        PackedSize=item.get('Packed size', '--no packedsize found'),
        Raw=item,
    )

def getRarExecutablePath(throwIfNotFound=True):
    ""
    from .plugin_configreader import getExecutablePathFromPrefs
    fallbackGuesses = [r"C:\Program Files\WinRAR\RAR.exe"]
    return getExecutablePathFromPrefs('rar', throwIfNotFound=throwIfNotFound,fallbacksToTry=fallbackGuesses)
