
# shinerainsoftsevencommon
# Released under the LGPLv3 License
from .common_util_classes import *

import pprint
import re

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

def getSoftTempDir(startingPath=None):
    return shinerainsoftsevencommon_preferences.getTempDirectoryForPath(startingPath=None)

def getSoftDeleteDir(path):
    return shinerainsoftsevencommon_preferences.getSoftDeleteDirectoryForPath(path)

softDeleteFileRng = IndependentRNG()
def getSoftDeleteFullPath(path):
    from . import files
    
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


# why the asciiOnlyIfOnWindows option?
#     old windows tools might be compiled without unicode support, or without long-path support.
#     one way to get them to work would be to use win32api.GetShortPathName() but this needs the
#     win32api package, and also can fail on some filesystems.
#     temporarily moving the file risks leaving it there if there is a crash.
#     let's instead copy the file to a temp directory and run the tool on the copy there.
#     (if you have an ssd and want to limit writes you can create a ram drive with a tool like ImDisk,
#     then edit the .shinerainsoftsevencommon file on your machine to point there.)
def getSoftTempFullPath(extension, startingPath=None, asciiOnlyIfOnWindows=False):
    from . import files
    dir = getSoftTempDir(startingPath=startingPath)
    with softDeleteFileRng:
        randomString = getRandomString()
    
    fullPath = dir + files.dirSep + 'file' + randomString + '.' + extension
    if asciiOnlyIfOnWindows and sys.platform.startswith('win'):
        # check for the case where the user profile dir has an ascii character
        if containsNonAscii(fullPath):
            trace(f'''
            The temporary path has a unicode character... Please edit the file
            {getShineRainSoftSevenCommonPrefsFilePath()}
            and specify the path to another temporary directory that does not have a
            unicode character.''')
            raise Exception('Temporary path contains unicode character')
    
    return fullPath

    
class DeleteFileWhenCompleted:
    def __init__(self, path, softDelete=True, skipDelete=False):
        self.path = path
        self.softDelete = softDelete
        self.skipDelete = skipDelete
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.skipDelete:
            if files.exists(self.path):
                if self.softDelete:
                    softDeleteFile(self.path)
                else:
                    os.path.unlink(self.path)


    
    
