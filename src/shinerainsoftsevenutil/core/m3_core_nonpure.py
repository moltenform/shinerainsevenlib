
# shinerainsoftsevencommon
# Released under the LGPLv3 License

import pprint
import re

from m2_core_data_structures import *

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
    if not isPy3OrNewer:
        s = unicode(s)
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
        pprint.pprint(newDict)
    else:
        pprint.pprint(obj)

def _dbgHookCallback(exctype, value, traceback):
    DBG()
    alert('unhandled exception ' + value)
    sys.__excepthook__(exctype, value, traceback)

def registerDebughook(b=True):
    if b:
        sys.excepthook = _dbgHookCallback
    else:
        sys.excepthook = sys.__excepthook__

# endregion
# region rng helpers

def getRandomString(max=1000 * 1000, hex=False):
    import random
    
    if hex:
        return genUuid().split('-')[0]
    else:
        return '%s' % random.randrange(max)

def genUuid(asBase64=False):
    import uuid
    import base64
    
    u = uuid.uuid4()
    if asBase64:
        b = base64.urlsafe_b64encode(u.bytes_le)
        return b.decode('utf8')
    else:
        return str(u)

# endregion
# region temp file helpers

def getSoftTempDir(startingPath=None):
    return shinerainsoftsevencommon_preferences.getTempDirectoryForPath(startingPath=None)

def getSoftDeleteDir(path):
    return shinerainsoftsevencommon_preferences.getSoftDeleteDirectoryForPath(path)

softDeleteFileRng = IndependentRNG()
def getSoftDeleteFullPath(path):
    from . import files
    assertTrue(files.exists(path), 'file not found', path)
    
    dirPath = getSoftDeleteDir(path)
    if not dirPath:
        return None
    
    with softDeleteFileRng:
        randomString = getRandomString()
    
    # as a prefix, the first 2 chars of the parent directory
    prefix = files.getName(files.getParent(path))[0:2] + '_'
    newPath = dirPath + files.sep + prefix + files.getName(path) + randomString
    assertTrue(not files.exists(newPath), 'already exists', newPath)
    
    return newPath
    
def softDeleteFile(path, allowDirs=False, doTrace=False):
    from . import files
    assertTrue(files.exists(path), 'file not found', path)
    assertTrue(allowDirs or not files.isDir(path), 'typically you cannot softDelete a dir', path)
    newPath = getSoftDeleteFullPath(path)
    diagnostics = shinerainsoftsevencommon_preferences.diagnosticsEnabled()
    
    if not newPath:
        from send2trash import send2trash
        if diagnostics:
            trace(f'when deleting {path}, softDeleteDir not set, so falling back to send-to-os-recycle-bin')
        
        if doTrace:
            trace(f'softDeleteFile |on| {path}')
        
        send2trash(path)
    else:
        if doTrace:
            trace(f'softDeleteFile |on| {path} |to| {newPath}')
        
        files.move(path, newPath, overwrite=False, warnBetweenDrives=diagnostics, allowDirs=allowDirs)
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
    
