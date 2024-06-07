
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import shutil
from .plugin_fileexts import *
from .. import files
from ..core import assertTrue, getRandomString, trace

def addAllToRar(
    inPath, outPath, effort=None, formatVersion='4', dictSize=None, solid=True, pword=None
):
    from .plugin_compression import Strength, params7z, runProcessThatCreatesOutput

    if not effort:
        effort = Strength.optsDefault

    assertTrue(not isinstance(inPath, list), "we don't yet support multiple items")
    if not dictSize:
        dictSize = '256m' if formatVersion == '5' else '4096k'

    assertTrue(outPath.lower().endswith('.rar') or outPath.lower().endswith('.zip'))
    args = [getRarPath(), 'a']
    if solid:
        args.extend(['-s'])

    # 5 ("max") is still quite fast
    strEffort = '0' if effort == Strength.optsStore else '5'
    if outPath.lower().endswith('.rar'):
        args.extend(['-m' + strEffort])
        args.extend(['-ma' + formatVersion])
        args.extend(['-md' + dictSize])

    if pword:
        # hp encrypts both headers and files
        args.extend(['-hp' + pword])

    args.extend(['%output%'])
    args.extend(['%input%'])
    runProcessThatCreatesOutput(args, inPath=inPath, outPath=outPath)

def getContentsViaRar(archive, verbose, _silenceWarnings, pword=None):
    from . import plugin_compression_7z

    assertTrue(files.isFile(archive))
    assertTrue(verbose, 'we only support verbose listing')
    args = [getRarPath(), 'lt', plugin_compression_7z.getPlaceholderPword(pword), archive]
    _retcode, stdout, _stderr = files.run(args)
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

def getRarPath():
    return 'rar' if shutil.which('rar') else r'C:\Program Files\WinRAR\Rar.exe'
