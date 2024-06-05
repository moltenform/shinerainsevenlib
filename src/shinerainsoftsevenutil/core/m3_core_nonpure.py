
# shinerainsoftsevencommon
# Released under the LGPLv3 License

import pprint as _pprint
import random as _random
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
    except BaseException as e:
        if 'selection doesn\'t exist' in str(e):
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
    "dump values of local variables"
    import inspect
    
    if obj is None:
        fback = inspect.currentframe().f_back
        framelocals = fback.f_locals
        newDict = {}
        for key in framelocals:
            if not callable(framelocals[key]) and not \
                    inspect.isclass(framelocals[key]) and not \
                    inspect.ismodule(framelocals[key]):
                newDict[key] = framelocals[key]
        _pprint._pprint(newDict)
    else:
        _pprint._pprint(obj)

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

def getRandomString(max=1000 * 1000, hex=False):
    if hex:
        return genUuid().split('-')[0]
    else:
        return '%s' % _random.randrange(max)

def genUuid(asBase64=False):
    import uuid
    import base64
    
    u = uuid.uuid4()
    if asBase64:
        b = base64.urlsafe_b64encode(u.bytes_le)
        return b.decode('utf8')
    else:
        return str(u)

class IndependentRNG:
    "keep a separate _random stream that won't get affected by someone else calling seed()"
    def __init__(self, seed=None):
        if seed is not None:
            _random.seed(seed)
            
        self.state = _random.getstate()
        self.keep_outside_state = None
        self.entered = False
    
    def __enter__(self):
        if self.entered:
            return
        
        self.entered = True
        self.keep_outside_state = _random.getstate()
        _random.setstate(self.state)
    
    def __exit__(self, type, value, traceback):
        if not self.entered:
            return
                
        self.entered = False
        _random.setstate(self.keep_outside_state)

# endregion
# region temp file helpers
def getSoftTempDir(path=''):
    from .. import utility
    prefs = utility.m1_config.getSsrsInternalPrefs()
    return prefs.parsed.tempDirectory

cUseOSTrash = UniqueSentinelForMissingParameter()
def getSoftDeleteDir(path):
    from .. import files
    from .. import utility
    prefs = utility.m1_config.getSsrsInternalPrefs()
    k, v = prefs.findKeyForPath(path, 'softDeleteDirectory_')
    if not v:
        v = prefs.parsed.main.softDeleteDirectory
        if not v:
            return cUseOSTrash
    assertTrue(files.isDir(v), 'not a directory', v)
    return v

            #~ if prefs.parsed.main.warnSoftDeleteBetweenDrives:

_softDeleteFileRng = IndependentRNG()
def getSoftDeleteFullPath(path):
    from .. import files
    assertTrue(files.exists(path), 'file not found', path)
    
    dirPath = getSoftDeleteDir(path)
    if not dirPath or dirPath is cUseOSTrash:
        return cUseOSTrash
    
    with _softDeleteFileRng:
        randomString = getRandomString()
    
    # as a prefix, the first 2 chars of the parent directory
    prefix = files.getName(files.getParent(path))[0:2] + '_'
    newPath = dirPath + files.sep + prefix + files.getName(path) + randomString
    assertTrue(not files.exists(newPath), 'already exists', newPath)
    
    return newPath
    
def softDeleteFile(path, allowDirs=False, doTrace=False):
    "Delete a file in a recoverable way, either OS Trash or a designated folder"
    from .. import files
    from .. import utility
    from .m4_core_ui import warn
    prefs = utility.m1_config.getSsrsInternalPrefs()
    assertTrue(files.exists(path), 'file not found', path)
    assertTrue(allowDirs or not files.isDir(path), 'you cannot softDelete a dir', path)
    newPath = getSoftDeleteFullPath(path)
    warnIfBetweenDrives = prefs.parsed.main.warnSoftDeleteBetweenDrives

    if warnIfBetweenDrives:
        if not newPath or newPath is cUseOSTrash:
            warn('about to send file to OS trash. you may want to put a softDeleteDirectory '
                 'into shinerainsoftsevenutil.cfg')
    
    if not newPath or newPath is cUseOSTrash:
        try:
            from send2trash import send2trash
        except ImportError:
            assertTrue(False, 'Either put a softDeleteDirectory into shinerainsoftsevenutil.cfg',
                       ', or install the package send2trash')
        if doTrace:
            trace(f'softDeleteFile |on| {path}')
        
        send2trash(path)
    else:
        if doTrace:
            trace(f'softDeleteFile |on| {path} |to| {newPath}')
        
        files.move(path, newPath, overwrite=False, warnBetweenDrives=warnIfBetweenDrives,
                   allowDirs=allowDirs)
        return newPath

# endregion
# region other helpers    

def downloadUrl(url, toFile=None, timeout=30, asText=False):
    import requests
    resp = requests.get(url, timeout=timeout)
    if toFile:
        with open(toFile, 'wb') as fout:
            fout.write(resp.content)
    
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
    
