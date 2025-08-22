

# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import pprint as _pprint
import random as _random
import os as _os
import sys as _sys
import re as _re

from .m2_core_data_structures import *

# region clipboard state

def getClipboardText():
    "Get clipboard text"
    try:
        return _getClipboardTextPyperclip()
    except ImportError:
        return _getClipboardTextTk()

def setClipboardText(s):
    "Set clipboard text"
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
    "Print values of local variables"
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
    "Register callback for printing values of local variables"
    if b:
        _sys.excepthook = _dbgHookCallback
    else:
        _sys.excepthook = _sys.__excepthook__

# endregion
# region rng helpers

def getRandomString(maxVal=1000 * 1000, asHex=False, rng=_random):
    "Generate a random string of digits"
    if asHex:
        assertTrue(rng == _random, "Can't provide a custom random for this one")
        return genUuid().split('-')[0]
    else:
        return '%s' % rng.randrange(maxVal)

def genUuid(asBase64=False):
    "Generate a UUID"
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
# region other helpers

def downloadUrl(url, toFile=None, timeout=30, asText=False):
    "Download a URL, if toFile is not specified returns the results as a string."
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
    "Start a thread"
    import threading

    if args is None:
        args = tuple()

    t = threading.Thread(target=fn, args=args)
    t.start()

# endregion

# region temp file helpers

def _getTrashDirPath(originalFile):
    from ..plugins.plugin_configreader import getSsrsInternalPrefs

    prefs = getSsrsInternalPrefs()
    trashDir = prefs.parsed.main.get('trashDir') or 'default'
    
    if trashDir == 'default':
        # likely to be writable, which is good
        return _os.path.expanduser('~/trash')
    elif trashDir == 'recycleBin':
        return 'recycleBin'
    elif trashDir == 'currentDriveDataLocalTrash':
        if _sys.platform.startswith('win'):
            originalFileFull = _os.path.abspath(originalFile)
            assertTrue(_re.match(r'^[a-zA-Z]:', originalFileFull), 'originalFileFull should be absolute path', originalFileFull)
            driveLetter = originalFileFull[0]
            return driveLetter + ':/data/local/trash'
        else:
            return _os.path.expanduser('~/data/local/trash')
    else:
        if _os.path.isabs(trashDir):
            # it looks like an absolute path
            return trashDir
        else:
            # it's a relative path or misspelling of a known option
            raise ShineRainSevenLibError(longStr('''invalid trashDir, please fix shinerainsevenlib.cfg.
                expected "default" or "recycleBin" or an absolute path'''), trashDir)

def _getTrashDirAndCreateIfNeeded(originalFile):
    from .. import files

    trashDir = _getTrashDirPath(originalFile)
    if trashDir != 'recycleBin':
        try:
            files.makeDirs(trashDir)
        except Exception as e:
            raise ShineRainSevenLibError('failed to create trash dir', trashDir) from e
    
    return trashDir

# use an independent rng, so that other random sequences aren't disrupted
_rngForSoftDeleteFile = IndependentRNG()
def _getTrashFullDest(path, trashDir):
    from .. import files
    randomString = getRandomString(rng=_rngForSoftDeleteFile.rng)
    
    # as a prefix, the first 2 chars of the parent directory
    prefix = files.getName(files.getParent(path))[0:2] + '_'
    newPath = trashDir + files.sep + prefix + files.getName(path) + randomString
    assertTrue(not files.exists(newPath), 'already exists', newPath)
    return newPath


def softDeleteFile(path, allowDirs=False, doTrace=False):
    """Delete a file in a recoverable way, either OS Trash or a designated folder.
    
    Defaults to ~/trash
    
    Configure behavior by editing shinerainsevenlib.cfg, 
    
    trashDir='recycleBin' or 'currentDriveDataLocalTrash' or a path"""
    from .. import files
    from .m4_core_ui import warn

    assertTrue(files.exists(path), 'file not found', path)
    assertTrue(allowDirs or not files.isDir(path), 'you cannot softDelete a dir', path)
    trashDir = _getTrashDirAndCreateIfNeeded(path)
    if trashDir == 'recycleBin':
        try:
            from send2trash import send2trash
        except ImportError as e:
            raise ShineRainSevenLibError('shinerainsevenlib.cfg says recycleBin, but send2trash not installed') from e
        
        if doTrace:
            trace(f'softDeleteFile |on| {path} to recycleBin')
        
        send2trash(path)
        return '<sent-to-recycle-bin>'
    else:
        destPath = _getTrashFullDest(path, trashDir)
        if doTrace:
            trace(f'softDeleteFile |on| {path} to {destPath}')
        
        files.move(path, destPath, False)
        return destPath

def _getSoftTempDir(_originalPath, preferEphemeral):
    import tempfile
    from ..plugins.plugin_configreader import getSsrsInternalPrefs

    prefs = getSsrsInternalPrefs()
    tempDir = prefs.parsed.main.get('tempDir') or 'default'
    tempEphemeralDir = prefs.parsed.main.get('tempEphemeralDir') or 'default'
    
    if preferEphemeral:
        if tempEphemeralDir == 'default':
            return tempfile.gettempdir() + '/srsstemp-ephemeral'
        else:
            assertTrue(_os.path.isabs(tempEphemeralDir), 'shinerainsevenlib.cfg, tempEphemeralDir should be absolute path')
            return tempEphemeralDir
    else:
        if tempDir == 'default':
            return tempfile.gettempdir() + '/srsstemp'
        else:
            assertTrue(_os.path.isabs(tempDir), 'shinerainsevenlib.cfg, tempDir should be absolute path')
            return tempDir

def _getTempDirAndCreateIfNeeded(originalPath, preferEphemeral):
    from .. import files

    tempDir = _getSoftTempDir(originalPath, preferEphemeral)
    try:
        files.makeDirs(tempDir)
    except Exception as e:
        raise ShineRainSevenLibError('failed to create trash dir', tempDir) from e

    return tempDir

def getSoftTempDir(path='', preferEphemeral=False):
    """
    Get a temporary directory. 
    Defaults to default OS temp directory, can be configured in shinerainsevenlib.cfg

    tempDir = (path to dir)
    
    tempEphemeralDir = (path to dir)
    
    An ephemeral dir is one where data isn't kept long term. I often configure this
    to be a RAM drive, which are useful for heavy read/write scenarios.
    """
    ret = _getTempDirAndCreateIfNeeded(path, preferEphemeral)
    assertTrue(_os.path.isdir(ret), 'temp dir not a directory', ret)
    return _os.path.join(ret, path) if path else ret
    

# endregion


