exeExt = {'.action': 1, '.apk': 1, '.app': 1, '.bat': 1, '.bin': 1, '.cmd': 1, '.com': 1,
    '.command': 1, '.cpl': 1, '.csh': 1, '.exe': 1, '.gadget': 1, '.inf1': 1, '.ins': 1, '.inx': 1,
    '.ipa': 1, '.isu': 1, '.job': 1, '.jse': 1, '.ksh': 1, '.lnk': 1, '.msc': 1, '.msi': 1,
    '.msp': 1, '.mst': 1, '.osx': 1, '.out': 1, '.paf': 1, '.pif': 1, '.prg': 1, '.ps1': 1,
    '.reg': 1, '.rgs': 1, '.run': 1, '.scr': 1, '.sct': 1, '.shb': 1, '.shs': 1, '.u3p': 1,
    '.vb': 1, '.vbe': 1, '.vbs': 1, '.vbscript': 1, '.workflow': 1, '.ws': 1, '.wsf': 1, '.wsh': 1}

warnExt = {'.0xe': 1, '.73k': 1, '.89k': 1, '.a6p': 1, '.ac': 1, '.acc': 1, '.acr': 1, '.actm': 1,
    '.ahk': 1, '.air': 1, '.app': 1, '.arscript': 1, '.as': 1, '.asb': 1, '.awk': 1, '.azw2': 1,
    '.beam': 1, '.btm': 1, '.cel': 1, '.celx': 1, '.chm': 1, '.cof': 1, '.crt': 1, '.dek': 1,
    '.dld': 1, '.dmc': 1, '.docm': 1, '.dotm': 1, '.dxl': 1, '.ear': 1, '.ebm': 1, '.ebs': 1,
    '.ebs2': 1, '.ecf': 1, '.eham': 1, '.elf': 1, '.es': 1, '.ex4': 1, '.exopc': 1, '.ezs': 1,
    '.fas': 1, '.fky': 1, '.fpi': 1, '.frs': 1, '.fxp': 1, '.gs': 1, '.ham': 1, '.hms': 1,
    '.hpf': 1, '.hta': 1, '.iim': 1, '.ipf': 1, '.isp': 1, '.jar': 1, '.js': 1, '.jsx': 1,
    '.kix': 1, '.lo': 1, '.ls': 1, '.mam': 1, '.mcr': 1, '.mel': 1, '.mpx': 1, '.mrc': 1,
    '.ms': 1, '.ms': 1, '.mxe': 1, '.nexe': 1, '.obs': 1, '.ore': 1, '.otm': 1, '.pex': 1,
    '.plx': 1, '.potm': 1, '.ppam': 1, '.ppsm': 1, '.pptm': 1, '.prc': 1, '.pvd': 1, '.pwc': 1,
    '.pyc': 1, '.pyo': 1, '.qpx': 1, '.rbx': 1, '.rox': 1, '.rpj': 1, '.s2a': 1, '.sbs': 1,
    '.sca': 1, '.scar': 1, '.scb': 1, '.script': 1, '.smm': 1, '.spr': 1, '.tcp': 1, '.thm': 1,
    '.tlb': 1, '.tms': 1, '.udf': 1, '.upx': 1, '.url': 1, '.vlx': 1, '.vpm': 1, '.wcm': 1,
    '.widget': 1, '.wiz': 1, '.wpk': 1, '.wpm': 1, '.xap': 1, '.xbap': 1, '.xlam': 1, '.xlm': 1,
    '.xlsm': 1, '.xltm': 1, '.xqt': 1, '.xys': 1, '.zl9': 1}

mostCommonImageExt = {'.gif': 1, '.jpg': 1, '.jpeg': 1, '.png': 1, '.bmp': 1, '.tif': 1,
    '.webp': 1}

def extensionPossiblyExecutable(s):
    '''Returns 'exe' if it looks executable,
    Returns 'warn' if it is a document type that can include embedded scripts,
    Returns False otherwise'''
    ext = getExt(s, False)
    if ext in exeExt:
        return 'exe'
    elif ext in warnExt:
        return 'warn'
    else:
        return False
