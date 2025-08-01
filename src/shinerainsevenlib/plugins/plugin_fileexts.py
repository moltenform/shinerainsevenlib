
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

from .. import files as _files

imageExtensions = {
    '.jpg': 1,  # section
    '.jpeg': 1,
    '.jfif': 1,
    '.gif': 1,
    '.png': 1,
    '.webp': 1,
    '.heic': 1,
    '.jxl': 1,  # section
    '.ico': 1,
    '.cur': 1,
    '.jp2': 1,  # section
    '.av1f': 1,
    '.avif': 1,
    '.bpg': 1,
    '.flif': 1,
    '.fuif': 1,
    '.tga': 1,
    '.pict': 1,
    '.tif': 1,  # section
    '.tiff': 1,
    '.ppm': 1,
    '.pgm': 1,
    '.pbm': 1,
    '.pnm': 1,
    '.pdn': 1,
    '.psd': 1,
    '.bmp': 1,
}

vidExtensions = {
    '.webm': 1,  # section
    '.mkv': 1,
    '.vob': 1,
    '.mp4': 1,
    '.m4p': 1,
    '.m4v': 1,
    '.mpg': 1,
    '.mpeg': 1,
    '.m2v': 1,
    '.flv': 1,  # section
    '.oggv': 1,
    '.drc': 1,
    '.gifv': 1,
    '.mng': 1,
    '.avi': 1,
    '.mov': 1,
    '.qt': 1,
    '.wmv': 1,
    '.yuv': 1,
    '.rm': 1,
    '.rmvb': 1,
    '.viv': 1,
    '.asf': 1,
    '.amv': 1,
    '.svi': 1,
    '.mxf': 1,
    '.roq': 1,
    '.nsv': 1,
    '.f4v': 1,
    '.f4p': 1,
    '.f4a': 1,
    '.f4b': 1,
    '.3gp': 1,
    '.3g2': 1,
}

audExtensions = {
    '.flac': 1,  # section
    '.ogg': 1,
    '.mp3': 1,
    '.m4a': 1,
    '.wav': 1,
    '.aif': 1,  # section
    '.aiff': 1,
    '.au': 1,
    '.pcm': 1,
    '.opus': 1,  # section
    '.oga': 1,
    '.mogg': 1,
    '.wma': 1,  # section
    '.ape': 1,
    '.wv': 1,
    '.tta': 1,
    '.atrac': 1,
    '.alac': 1,
    '.shn': 1,
    '.mpc': 1,
    '.mpcs': 1,
    '.mpp': 1,
    '.aac': 1,
    '.aa3': 1,
    '.at3': 1,
    '.at9': 1,
    '.atp': 1,
    '.hma': 1,
    '.oma': 1,
    '.omg': 1,
    '.bwf': 1,
    '.aa': 1,  # section
    '.aax': 1,
    '.act': 1,
    '.amr': 1,
    '.awb': 1,
    '.dss': 1,
    '.dvf': 1,
    '.gsm': 1,
    '.iklax': 1,
    '.ivs': 1,
    '.m4b': 1,
    '.m4p': 1,
    '.mmf': 1,
    '.msv': 1,
    '.nmf': 1,
    '.ra': 1,
    '.rm': 1,
    '.raw': 1,
    '.fr64': 1,
    '.voc': 1,  # section
    '.vox': 1,
    '.cda': 1,
    '.8svx': 1,
}

archiveExtensions = {
    '.ar': 1,  # section
    '.cpio': 1,
    '.shar': 1,
    '.lbr': 1,
    '.iso': 1,
    '.mar': 1,
    '.sbx': 1,
    '.tar': 1,
    '.br': 1,  # section
    '.bz2': 1,
    '.f': 1,
    '.gz': 1,
    '.lz': 1,
    '.lz4': 1,
    '.lzma': 1,
    '.lzo': 1,
    '.rz': 1,
    '.sfark': 1,
    '.sz': 1,
    '.xz': 1,
    '.z': 1,
    '.zst': 1,
    '.7z': 1,  # section
    '.zip': 1,
    '.rar': 1,
    '.s7z': 1,  # section
    '.ace': 1,
    '.afa': 1,
    '.alz': 1,
    '.apk': 1,
    '.arc': 1,
    '.ark': 1,
    '.cdx': 1,
    '.arj': 1,
    '.b1': 1,
    '.b6z': 1,
    '.ba': 1,
    '.bh': 1,
    '.cab': 1,
    '.car': 1,
    '.cfs': 1,
    '.cpt': 1,
    '.dar': 1,
    '.dd': 1,
    '.dgc': 1,
    '.dmg': 1,
    '.ear': 1,
    '.gca': 1,
    '.genozip': 1,
    '.ha': 1,
    '.hki': 1,
    '.ice': 1,
    '.jar': 1,
    '.kgb': 1,
    '.lzh': 1,
    '.lha': 1,
    '.lzx': 1,
    '.pak': 1,
    '.partimg': 1,
    '.paq6': 1,
    '.paq7': 1,
    '.paq8': 1,
    '.pea': 1,
    '.phar': 1,
    '.pim': 1,
    '.pit': 1,
    '.qda': 1,
    '.rk': 1,
    '.sda': 1,
    '.sea': 1,
    '.sen': 1,
    '.sfx': 1,
    '.shk': 1,
    '.sit': 1,
    '.sitx': 1,
    '.sqx': 1,
    '.tgz': 1,
    '.tbz': 1,
    '.tbz2': 1,
    '.tlz': 1,
    '.txz': 1,
    '.uc': 1,
    '.uc0': 1,
    '.uc2': 1,
    '.ucn': 1,
    '.ur2': 1,
    '.ue2': 1,
    '.uca': 1,
    '.uha': 1,
    '.war': 1,
    '.wim': 1,
    '.xar': 1,
    '.xp3': 1,
    '.yz1': 1,
    '.zipx': 1,
    '.zoo': 1,
    '.zpaq': 1,
    '.zz': 1,
}

# based on  default_compressed_extensions.txt in Duplicati source code
alreadyCompressedExt = {
    '.7z': 1,
    '.alz': 1,
    '.bz': 1,
    '.bz2': 1,
    '.cab': 1,
    '.cbr': 1,
    '.cbz': 1,
    '.deb': 1,
    '.dl_': 1,
    '.dsft': 1,
    '.ex_': 1,
    '.gz': 1,
    '.jar': 1,
    '.lzma': 1,
    '.mpkg': 1,
    '.msi': 1,
    '.msp': 1,
    '.msu': 1,
    '.pet': 1,
    '.rar': 1,
    '.rpm': 1,
    '.sft': 1,
    '.sfx': 1,
    '.sit': 1,
    '.sitx': 1,
    '.sy_': 1,
    '.tgz': 1,
    '.war': 1,
    '.wim': 1,
    '.xar': 1,
    '.xz': 1,
    '.zip': 1,
    '.zipx': 1,
    '.3gp': 1,
    '.aa3': 1,
    '.aac': 1,
    '.aif': 1,
    '.ape': 1,
    '.file': 1,
    '.flac': 1,
    '.gsm': 1,
    '.iff': 1,
    '.m4a': 1,
    '.mp3': 1,
    '.mpa': 1,
    '.mpc': 1,
    '.ra': 1,
    '.ogg': 1,
    '.wma': 1,
    '.wv': 1,
    '.sfark': 1,
    '.sfpack': 1,
    '.3g2': 1,
    '.asf': 1,
    '.asx': 1,
    '.avi': 1,
    '.bsf': 1,
    '.divx': 1,
    '.dv': 1,
    '.f4v': 1,
    '.flv': 1,
    '.hdmov': 1,
    '.m2p': 1,
    '.m4v': 1,
    '.mkv': 1,
    '.mov': 1,
    '.mp4': 1,
    '.mpg': 1,
    '.mts': 1,
    '.ogv': 1,
    '.rm': 1,
    '.swf': 1,
    '.trp': 1,
    '.ts': 1,
    '.vob': 1,
    '.webm': 1,
    '.wmv': 1,
    '.wtv': 1,
    '.m2ts': 1,
    '.emz': 1,
    '.gif': 1,
    '.j2c': 1,
    '.jpeg': 1,
    '.jpg': 1,
    '.pamp': 1,
    '.pdn': 1,
    '.png': 1,
    '.pspimage': 1,
    '.tif': 1,
    '.dng': 1,
    '.cr2': 1,
    '.webp': 1,
    '.nef': 1,
    '.arw': 1,
    '.heic': 1,
    '.eot': 1,
    '.woff': 1,
    '.bik': 1,
    '.mpq': 1,
    '.chm': 1,
    '.docx': 1,
    '.docm': 1,
    '.dotm': 1,
    '.dotx': 1,
    '.epub': 1,
    '.graffle': 1,
    '.hxs': 1,
    '.max': 1,
    '.mobi': 1,
    '.mshc': 1,
    '.odp': 1,
    '.ods': 1,
    '.odt': 1,
    '.otp': 1,
    '.ots': 1,
    '.ott': 1,
    '.pages': 1,
    '.pptx': 1,
    '.pptm': 1,
    '.stw': 1,
    '.trf': 1,
    '.webarchive': 1,
    '.xlsx': 1,
    '.xlsm': 1,
    '.xlsb': 1,
    '.xps': 1,
    '.d': 1,
    '.dess': 1,
    '.i': 1,
    '.idx': 1,
    '.nupkg': 1,
    '.pack': 1,
    '.swz': 1,
    '.aes': 1,
    '.axx': 1,
    '.gpg': 1,
    '.hc': 1,
    '.kdbx': 1,
    '.tc': 1,
    '.tpm': 1,
    '.fve': 1,
    '.apk': 1,
    '.eftx': 1,
    '.sdg': 1,
    '.thmx': 1,
    '.vsix': 1,
    '.vsv': 1,
    '.wmz': 1,
    '.xpi': 1,
    '.pea': 1,
    '.jxl': 1,
    '.avif': 1,
    '.mpo': 1,
}

moreNonTextual = {
    '.com': 1,
    '.exe': 1,
    '.msi': 1,
    '.pdb': 1,
    '.dll': 1,
    '.pyc': 1,
    '.pch': 1,
    '.pyd': 1,
    '.lnk': 1,  #
    '.scssc': 1,
    '.mid': 1,
    '.db': 1,
    '.db-wal': 1,
    '.dat': 1,
    '.wasm': 1,
}

documentExtensions = {
    '.docx': 1,
    '.doc': 1,
    '.xlsx': 1,
    '.xls': 1,
    '.ppt': 1,
    '.pptx': 1,
    '.pdf': 1,
    '.ttf': 1,
}

exeExt = {
    '.action': 1,
    '.apk': 1,
    '.app': 1,
    '.bat': 1,
    '.bin': 1,
    '.cmd': 1,
    '.com': 1,
    '.command': 1,
    '.cpl': 1,
    '.csh': 1,
    '.exe': 1,
    '.gadget': 1,
    '.inf1': 1,
    '.ins': 1,
    '.inx': 1,
    '.ipa': 1,
    '.isu': 1,
    '.job': 1,
    '.jse': 1,
    '.ksh': 1,
    '.lnk': 1,
    '.msc': 1,
    '.msi': 1,
    '.msp': 1,
    '.mst': 1,
    '.osx': 1,
    '.out': 1,
    '.paf': 1,
    '.pif': 1,
    '.prg': 1,
    '.ps1': 1,
    '.reg': 1,
    '.rgs': 1,
    '.run': 1,
    '.scr': 1,
    '.sct': 1,
    '.shb': 1,
    '.shs': 1,
    '.sh': 1,
    '.u3p': 1,
    '.vb': 1,
    '.vbe': 1,
    '.vbs': 1,
    '.vbscript': 1,
    '.workflow': 1,
    '.ws': 1,
    '.wsf': 1,
    '.wsh': 1,
}

warnExt = {
    '.0xe': 1,
    '.73k': 1,
    '.89k': 1,
    '.a6p': 1,
    '.ac': 1,
    '.acc': 1,
    '.acr': 1,
    '.actm': 1,
    '.ahk': 1,
    '.air': 1,
    '.app': 1,
    '.arscript': 1,
    '.as': 1,
    '.asb': 1,
    '.awk': 1,
    '.azw2': 1,
    '.beam': 1,
    '.btm': 1,
    '.cel': 1,
    '.celx': 1,
    '.chm': 1,
    '.cof': 1,
    '.crt': 1,
    '.dek': 1,
    '.dld': 1,
    '.dmc': 1,
    '.docm': 1,
    '.dotm': 1,
    '.dxl': 1,
    '.ear': 1,
    '.ebm': 1,
    '.ebs': 1,
    '.ebs2': 1,
    '.ecf': 1,
    '.eham': 1,
    '.elf': 1,
    '.es': 1,
    '.ex4': 1,
    '.exopc': 1,
    '.ezs': 1,
    '.fas': 1,
    '.fky': 1,
    '.fpi': 1,
    '.frs': 1,
    '.fxp': 1,
    '.gs': 1,
    '.ham': 1,
    '.hms': 1,
    '.hpf': 1,
    '.hta': 1,
    '.iim': 1,
    '.ipf': 1,
    '.isp': 1,
    '.jar': 1,
    '.js': 1,
    '.jsx': 1,
    '.kix': 1,
    '.lo': 1,
    '.ls': 1,
    '.mam': 1,
    '.mcr': 1,
    '.mel': 1,
    '.mpx': 1,
    '.mrc': 1,
    '.ms': 1,
    '.mxe': 1,
    '.nexe': 1,
    '.obs': 1,
    '.ore': 1,
    '.otm': 1,
    '.pex': 1,
    '.plx': 1,
    '.potm': 1,
    '.ppam': 1,
    '.ppsm': 1,
    '.pptm': 1,
    '.prc': 1,
    '.pvd': 1,
    '.pwc': 1,
    '.pyc': 1,
    '.pyo': 1,
    '.qpx': 1,
    '.rbx': 1,
    '.rox': 1,
    '.rpj': 1,
    '.s2a': 1,
    '.sbs': 1,
    '.sca': 1,
    '.scar': 1,
    '.scb': 1,
    '.script': 1,
    '.smm': 1,
    '.spr': 1,
    '.tcp': 1,
    '.thm': 1,
    '.tlb': 1,
    '.tms': 1,
    '.udf': 1,
    '.upx': 1,
    '.url': 1,
    '.vlx': 1,
    '.vpm': 1,
    '.wcm': 1,
    '.widget': 1,
    '.wiz': 1,
    '.wpk': 1,
    '.wpm': 1,
    '.xap': 1,
    '.xbap': 1,
    '.xlam': 1,
    '.xlm': 1,
    '.xlsm': 1,
    '.xltm': 1,
    '.xqt': 1,
    '.xys': 1,
    '.zl9': 1,
}

def extensionPossiblyExecutable(s):
    """Returns 'exe' if it looks executable,
    Returns 'warn' if it is a document type that can include embedded scripts,
    Returns False otherwise"""

    ext = _files.getExt(s, removeDot=False)
    if ext in exeExt:
        return 'exe'
    elif ext in warnExt:
        return 'warn'
    else:
        return False

def isCompressedTarExtension(archive):
    """Is this a compressed tar archive, like example.tar.gz or example.tgz'
    Not example.gz which should fall under isSingleFileCompressionExtension() instead"""
    archive = archive.lower()
    return archive.endswith((
        '.tar.z',
        '.tar.br',
        '.tar.zst',
        '.tar.gz',
        '.tar.bz2',
        '.tar.xz',
        '.tgz',
        '.tbz',
        '.tbz2',
        '.txz'))

def isSingleFileCompressionExtension(archive):
    """Is this a plain single-file-archive, like example.gz'
    Not example.tar.gz which should fall under isCompressedTarExtension() instead"""
    archive = archive.lower()
    a, _b = _files.splitExt(archive)
    if a.endswith('.tar'):
        return False
    else:
        return archive.endswith((
        '.z',
        '.br',
        '.zst',
        '.gz',
        '.bz2',
        '.xz',
        ))

mostCommonImageExt = {
    '.gif': 1,
    '.jpg': 1,
    '.jpeg': 1,
    '.png': 1,
    '.bmp': 1,
    '.tif': 1,
    '.webp': 1,
    '.jxl': 1,
    '.heic': 1,
    '.avif': 1,
}

mostCommonImageExtAlternatives = {
    '.jpeg_large': '.jpg',
    '.jpg_large': '.jpg',
    '.jpeg': '.jpg',
    '.jfif': '.jpg',
    '.tiff': '.tif',
    '.png_large': '.png',
}

def removeDotsFromExts(obj):
    "Get a version of the dictionary without leading ."
    return set(k[1:] if k.startswith('.') else k for k in obj)
