
import os

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
    try:
        from tkinter import Tk
    except ImportError:
        from Tkinter import Tk
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
    try:
        from tkinter import Tk
    except ImportError:
        from Tkinter import Tk
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
    import pprint
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


