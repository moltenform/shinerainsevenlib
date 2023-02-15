
from .. import files
from ..common_util import *
from .file_extensions import alreadyCompressedExt
import zipfile
import shutil

zipMethods = Bucket(
    deflate=zipfile.ZIP_DEFLATED,
    store=zipfile.ZIP_STORED,
    lzma=zipfile.ZIP_LZMA if 'ZIP_LZMA' in dir(zipfile) else None
)

optsCompression = Bucket(
    optsMax='optsMax',
    optsStrong='optsStrong',
    optsDefault='optsDefault',
    optsStore='optsStore',
)

internalOptsZip = dict(
    # max compression (slow)
    optsMax = '-tzip|-mx=9|-mm=Deflate|-mfb=258|-mpass=15',

    # strong compression
    optsStrong = '-tzip|-mx=9',
    
    # 7z's default compression
    optsDefault = '-tzip',
    
     # store
    optsStore = '-tzip|-mx=0',
)

internalOpts7z = dict(
    # max compression (slow)
    # for a 2gb file this takes around 14gb ram to compress, for machines with 16gb ram this is about the max.
    # confirmed will only need 2gb ram to decompress, though. (used sysinternals to see peak private bytes)
    # for 7z (unlike rar), it's fine to use a very large dict size for small input becuse 
    # when decompressing, the full 1.5gb is not allocated in ram unless there are actually big files.
    optsMax = '-t7z|-mx=9|-mfb=273|-myx=9|-mmt|-mmtf|-md=1536m|-mmf=bt3|-mqs=on|-mmc=10000',
    
    # in rare cases this can be better, usually though it is just slower and worse
    optsTweakLzma = '-t7z|-md=31|-mmf=bt3|-mmc=10000|-mpb=0|-mlc=0',

    # strong compression
    optsStrong = '-t7z|-m0=lzma|-mx=9|-mfb=64|-md=256m|-ms=on',
    
    # 7z's default compression
    optsDefault = '-t7z',
    
    # store
    optsStore = '-t7z|-mx=0',
)

# https://sevenzip.osdn.jp/chm/cmdline/switches/method.htm
# -m0=lzma2 (default)   method=lzma2
# -mx=9        sets strength to max
# -myx=9      sets file analysis to max to set filtes
#     (e.g. detects exe files and gives them a filter to convert addresses for better compression,
#     delta filter can be better for wav)
# -ms=on       use solid mode (use default block size)
# -mqs=on      sort files by extension when adding in solid mode
# -mf=on (default) use filters
# -mmt=2   use 2 threads (can also be off,on) (in mx=9 seems not to have much effect)
# -mtf=on   use multithread for filters
# -ma=1 (default) don't use fast mode
# -md=31 set dictionary size to 2gb
# -md=1536m set dictionary to 1.5Gb
# -mmf=bt3 which match finder
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


def addAllToZip(inPath, zipPath, method=zipMethods.deflate, alreadyCompressedAsStore=False,
        creatingNewArchive=True, pathPrefix='', recurse=True, **kwargs):
    
    assertTrue(method, 'invalid method (note that ZIP_LZMA is not always available)')
    if creatingNewArchive:
        assertTrue(not files.exists(zipPath))

    def getCompressionMethod(path):
        if alreadyCompressedAsStore and files.getext(path, False) in alreadyCompressedExt:
            return zipfile.ZIP_STORED
        else:
            assertTrue(isinstance(method, int), 'please specify zipMethods.deflate instead of "deflate"')
            return method

    assertTrue(not inPath.endswith('/') and not inPath.endswith('\\'))
    with zipfile.ZipFile(zipPath, 'a') as zip:
        if files.isfile(inPath):
            thisMethod = getCompressionMethod(inPath)
            zip.write(inPath, pathPrefix + files.getname(inPath), compress_type=thisMethod)
        elif files.isdir(inPath):
            itr = files.recursefiles(inPath, **kwargs) if recurse else files.listfiles(inPath, **kwargs)
            for f, short in itr:
                assertTrue(f.startswith(inPath))
                shortname = f[len(inPath) + 1:]
                thisMethod = getCompressionMethod(f)
                assertTrue(shortname)
                zip.write(f, pathPrefix + shortname, compress_type=thisMethod)
        else:
            raise RuntimeError("not found: " + inPath)


def addAllTo7z(inPathStrOrList, outPath, effort=optsCompression.optsDefault, multiThread='off', solid=True):
    assertTrue(outPath.endswith('7z') or outPath.endswith('zip'))
    if outPath.lower().endswith('.zip'):
        # zip format does not support solid
        assertTrue(not solid)
        opts = internalOptsZip[effort].split('|')
    else:
        opts = internalOpts7z[effort].split('|')
    
    args = ['7z', 'a']
    args.extend(['-mmt=' + multiThread])
    if opts:
        args.extend(opts)
        
    if not solid and not outPath.lower().endswith('.zip'):
        args.extend(['-ms=off'])
        
    args.extend([outPath])
    args.extend(['%input%'])
    sendToShellCommon(args, inPathStrOrList, outPath)


def addAllToRar(inPathStrOrList, outPath, formatVersion='4', dictSize='8192', solid=True):
    args = [getRarPath().binRar, 'a']
    if solid:
        args.extend(['-s'])
    args.extend(['-m', '5']) # effort=max 
    args.extend(['-ma', formatVersion])
    args.extend(['-md', dictSize])
    assertTrue(outPath.lower().endswith('.rar'))
    args.extend([outPath])
    args.extend(['%input%'])
    sendToShellCommon(args, inPathStrOrList, outPath)
    
def addAllToRarSimple(inPathStrOrList, outPath):
    args = [getRarPath().binWinRar, 'a', outPath, '%input%']
    sendToShellCommon(args, inPathStrOrList, outPath)


def checkArchivePasswordVia7z(inPath, pword=None):
    # we send in a placeholder password to intentionally get an error, and not block on stdin
    pword = pword or '(placeholderPassword)'
    args = ['7z', 'l', '-p' + pword, inPath]
    retcode, stdout, stderr = files.run(args, throwOnFailure=None)
    if retcode == 0:
        return {'output': stdout, 'couldNotOpenDueToIncorrectPassword': False}
    elif b'Wrong password?' in stderr:
        return {'couldNotOpenDueToIncorrectPassword': True}
    else:
        assertTrue(False, 'failed to load archive', inPath)

def checkArchiveIntegrityVia7z(inPath, pword=None):
    args = ['7z', 't', inPath]
    retcode, stdout, stderr = files.run(args, throwOnFailure=None)
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
    else:
        assertTrue(False, 'failed to test archive', inPath, stderr)
    
    
    



def getContents(archive, verbose):
    if archive.lower().endswith('.rar') and files.exists(getRarPath().binRar):
        return getContentsViaRar(archive, verbose)
    else:
        return getContentsVia7z(archive, verbose)
        
def processAttributesRar(item):
    return dict(
        Path=item['Path'], # uses \ as dirsep
        Type=item.get('Type'), # File or Directory
        Modified=item.get('Modified', '').split(',')[0], # 2023-02-02 12:56:05,673617400
        CRC=item.get('CRC32'),
        Size=item.get('Size'),
        PackedSize=item.get('Packed size'),
        Raw=item
    )
    
def processAttributes7z(item):
    return dict(
        Path=item['Path'], # uses \ as dirsep
        Type='Directory' if 'D' in item['Attributes'] else 'File',
        Modified=item['Modified'], #2023-01-27 18:17:19.7498290
        CRC=item['CRC'],
        Size=item.get('Size'),
        PackedSize=item.get('Packed Size'),
        Raw=item
    )



def getContentsViaRar(archive, verbose):
    assertTrue(files.isfile(archive))
    assertTrue(verbose, 'we only support verbose listing')
    args = [rarExe, 'lt', archive]
    retcode, stdout, stderr = files.run(args)
    stdout = stdout.decode('latin-1').replace('\r\n', '\n')
    results = []
    parts = stdout.split(' Name: ')
    parts.pop(0) # just the header
    for part in parts:
        lines = part.split('\n')
        result = {}
        results.append(result)
        result['Path'] = lines[0].strip()
        for line in lines[1:]:
            if not line.strip():
                continue
            
            title, contents = line.split(': ', 1)
            result[title.strip()] = contents.strip()
    return [processAttributesRar(result) for result in results]
    
def getContentsVia7z(archive, verbose):
    assertTrue(files.isfile(archive))
    assertTrue(verbose, 'we only support verbose listing')
    args = ['7z', '-slt', 'l', archive]
    retcode, stdout, stderr = files.run(args)
    stdout = stdout.decode('latin-1').replace('\r\n', '\n')
    header, stdout = stdout.split('\n----------\n')
    results = []
    parts = stdout.split('\n\n')
    for part in parts:
        lines = part.split('\n')
        result = {}
        results.append(result)
        for line in lines:
            if not line.strip():
                continue
            
            title, contents = line.split(' = ', 1)
            result[title.strip()] = contents.strip()
    return [processAttributes7z(result) for result in results]

def getRarPath():
    binRar = 'rar' if shutil.which('rar') else r"C:\Program Files\WinRAR\Rar.exe"
    binWinRar = 'winrar' if shutil.which('winrar') else r"C:\Program Files\WinRAR\WinRar.exe"
    return Bucket(
        binRar = binRar,
        binWinRar = binWinRar
    )

def sendToShellCommon(args, inPathStrOrList, outPath, inputInArgs=True):
    assertTrue(not files.exists(outPath), 'output already there')
    if isinstance(inPathStrOrList, str):
        inPathList = [inPathStrOrList]
    elif isinstance(inPathStrOrList, list):
        inPathList = inPathStrOrList
    else:
        assertTrue(False, 'input should be a list or string')
    
    if inputInArgs:
        inputIndex = args.index('%input%')
        newargs = args[0:inputIndex]
        newargs.extend(inPathList)
        newargs.extend(args[inputIndex+1:])
    else:
        newargs = args
    
    files.run(newargs)
    assertTrue(files.getsize(outPath) > 0, 'output must be more than 0 bytes')
    if files.getsize(outPath) < 128:
        trace('warning: small outsize', outPath)
        