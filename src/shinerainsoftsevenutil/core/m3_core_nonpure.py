
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pprint as _pprint
import random as _random
import os as _os
import sys as _sys

from .m2_core_data_structures import *

# region clipboard state

def getClipboardText():
    try:
        return _getClipboardTextPyperclip()
    except ImportError:
        return _getClipboardTextTk()

def setClipboardText(s):
    try:
        _setClipboardTextPyperclip(s)
    except ImportError:
        _setClipboardTextTk(s)

def _getClipboardTextTk():
    from tkinter import Tk

    try:
        r = Tk()
        r.withdraw()
        s = r.clipboard_get()
    except Exception as e:
        if "selection doesn't exist" in str(e):
            s = ''
        else:
            raise
    finally:
        r.destroy()
    return s

def _setClipboardTextTk(s):
    from tkinter import Tk

    assertTrue(isPy3OrNewer, 'Python 3 required')
    try:
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(s)
    finally:
        r.destroy()

def _getClipboardTextPyperclip():
    import pyperclip

    return pyperclip.paste()

def _setClipboardTextPyperclip(s):
    import pyperclip

    pyperclip.copy(s)

# endregion
# region debugging

def DBG(obj=None):
    "Dump values of local variables"
    import inspect

    if obj is None:
        fback = inspect.currentframe().f_back
        framelocals = fback.f_locals
        newDict = {}
        for key in framelocals:
            if (
                not callable(framelocals[key]) and
                not inspect.isclass(framelocals[key]) and
                not inspect.ismodule(framelocals[key])
            ):
                newDict[key] = framelocals[key]
        _pprint.pprint(newDict)
    else:
        _pprint.pprint(obj)

def _dbgHookCallback(exctype, value, traceback):
    DBG()
    from .m4_core_ui import alert

    alert('unhandled exception ' + value)
    _sys.__excepthook__(exctype, value, traceback)

def registerDebughook(b=True):
    if b:
        _sys.excepthook = _dbgHookCallback
    else:
        _sys.excepthook = _sys.__excepthook__

# endregion
# region rng helpers

def getRandomString(maxVal=1000 * 1000, asHex=False, rng=_random):
    if asHex:
        return genUuid().split('-')[0]
    else:
        return '%s' % rng.randrange(maxVal)

def genUuid(asBase64=False):
    import base64
    import uuid

    u = uuid.uuid4()
    if asBase64:
        b = base64.urlsafe_b64encode(u.bytes_le)
        return b.decode('utf8')
    else:
        return str(u)

class IndependentRNG:
    """Keep a separate random stream that won't get affected by someone else.
    sometimes you want to set rng state to get a repeatable sequence of numbers back,
    which would get thrown off by other parts of the program also getting rng values."""

    def __init__(self, seed=None):
        self.rng = _random.Random(seed)

# endregion
# region temp file helpers

def softDeleteFile(path, allowDirs=False, doTrace=False):
    "Delete a file in a recoverable way, either OS Trash or a designated folder"
    from .. import files
    from ..plugins.plugin_configreader import getSsrsInternalPrefs
    from .m4_core_ui import warn

    prefs = getSsrsInternalPrefs()
    assertTrue(files.exists(path), 'file not found', path)
    assertTrue(allowDirs or not files.isDir(path), 'you cannot softDelete a dir', path)
    newPath = getSoftDeleteFullPath(path)
    warnIfBetweenDrives = prefs.parsed.main.warnSoftDeleteBetweenDrives

    if warnIfBetweenDrives:
        if not newPath or newPath is cUseOSTrash:
            warn(
                'about to send file to OS trash. you may want to put a softDeleteDirectory '
                'into shinerainsoftsevenutil.cfg'
            )

    if not newPath or newPath is cUseOSTrash:
        try:
            from send2trash import send2trash
        except ImportError:
            assertTrue(
                False,
                'Either put a softDeleteDirectory into shinerainsoftsevenutil.cfg',
                ', or install the package send2trash',
            )
        if doTrace:
            trace(f'softDeleteFile |on| {path}')

        send2trash(path)
        return '<sent-to-trash>'
    else:
        if doTrace:
            trace(f'softDeleteFile |on| {path} |to| {newPath}')

        files.move(
            path,
            newPath,
            overwrite=False,
            warnBetweenDrives=warnIfBetweenDrives,
            allowDirs=allowDirs,
        )
        return newPath

cUseOSTrash = UniqueSentinelForMissingParameter()

def getSoftDeleteDir(path):
    r"""You can set up shinerainsoftsevenutil.cfg so that soft-deleted files go to a specified dir.
    set `softDeleteDirectory=path` or
    to be even more precise you can set different softDeletePaths based on the path,
    which can reduce number of disk writes. edit shinerainsoftsevenutil.cfg with paths like
    softDeleteDirectory_SlashhomeSlashuserSlasha=path1
    softDeleteDirectory_SlashhomeSlashuserSlashb=path2
    (which maps /home/a to path1 and /home/2 to path2) or

    softDeleteDirectory_cColonBackslash=path1
    softDeleteDirectory_dColonBackslash=path2
    (which maps C:\ to path1 and D:\ to path2)
    (all lowercase except the special keywords Slash, Backslash, and Colon)
    """
    from .. import files
    from ..plugins.plugin_configreader import getSsrsInternalPrefs

    prefs = getSsrsInternalPrefs()
    _k, v = prefs.findKeyForPath(path, 'softDeleteDirectory_')
    if not v:
        v = prefs.parsed.main.softDeleteDirectory
        if not v:
            return cUseOSTrash

    assertTrue(files.isDir(v), 'not a directory', v)
    return v

def _getSoftTempDirImpl(path='', preferEphemeral=False):
    from .. import files
    from ..plugins.plugin_configreader import getSsrsInternalPrefs

    prefs = getSsrsInternalPrefs()

    if preferEphemeral and prefs.parsed.get('tempEphemeralDirectory'):
        return prefs.parsed.get('tempEphemeralDirectory')

    dirPath = getSoftDeleteDir(path)
    if not dirPath or dirPath is cUseOSTrash:
        if prefs.parsed.tempDirectory:
            return prefs.parsed.tempDirectory
        else:
            import tempfile

            dirPath = tempfile.gettempdir()
            dirPath += '/srss'
            files.makeDirs(dirPath)
            return dirPath

    return dirPath

def getSoftTempDir(path='', preferEphemeral=False):
    dirPath = _getSoftTempDirImpl(path=path, preferEphemeral=preferEphemeral)

    # place in the temp subfolder
    assertTrue(_os.path.isdir(dirPath), 'temp dir not a directory', dirPath)
    dirPath += '/temp'
    if not _os.path.exists(dirPath):
        _os.makedirs(dirPath)
    return dirPath

_rngForSoftDeleteFile = IndependentRNG()

def getSoftDeleteFullPath(path):
    from .. import files

    assertTrue(files.exists(path), 'file not found', path)
    dirPath = getSoftDeleteDir(path)
    if not dirPath or dirPath is cUseOSTrash:
        return cUseOSTrash

    # place in the trash subfolder
    dirPath += '/trash'
    files.makeDirs(dirPath)

    # use an independent rng, so that other random sequences aren't disrupted
    randomString = getRandomString(rng=_rngForSoftDeleteFile.rng)

    # as a prefix, the first 2 chars of the parent directory
    prefix = files.getName(files.getParent(path))[0:2] + '_'
    newPath = dirPath + files.sep + prefix + files.getName(path) + randomString
    assertTrue(not files.exists(newPath), 'already exists', newPath)

    return newPath

# endregion
# region other helpers

def downloadUrl(url, toFile=None, timeout=30, asText=False):
    import requests

    resp = requests.get(url, timeout=timeout)
    if toFile:
        with open(toFile, 'wb') as fOut:
            fOut.write(resp.content)

    if asText:
        return resp.text
    else:
        return resp.content

def startThread(fn, args=None):
    import threading

    if args is None:
        args = tuple()

    t = threading.Thread(target=fn, args=args)
    t.start()

# endregion
