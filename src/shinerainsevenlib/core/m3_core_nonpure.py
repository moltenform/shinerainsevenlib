

# shinerainsevenlib (Ben Fisher, moltenform.com)
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
