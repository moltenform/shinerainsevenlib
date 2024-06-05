
# shinerainsoftsevencommon
# Released under the LGPLv3 License

import sys as _sys
import os as _os
import types as _types
from .m3_core_nonpure import *

# region user prompts

def getInputBool(prompt, flushOutput=True):
    prompt += ' '
    while True:
        s = getRawInput(prompt, flushOutput).strip()
        if s == 'y':
            return True
        if s == 'n':
            return False
        if s == 'Y':
            return 1
        if s == 'N':
            return 0
        if s == 'BRK':
            raise KeyboardInterrupt()

def getInputYesNoCancel(prompt, flushOutput=True):
    prompt += ' y/n/cancel '
    while True:
        s = getRawInput(prompt, flushOutput).strip()
        if s == 'y':
            return 'Yes'
        if s == 'n':
            return 'No'
        if s == 'cancel':
            return 'Cancel'
        if s == 'BRK':
            raise KeyboardInterrupt()

def getInputInt(prompt, min=0, max=0xffffffff, flushOutput=True):
    prompt += ' between %d and %d ' % (min, max)
    while True:
        s = getRawInput(prompt, flushOutput).strip()
        if s.isdigit() and min <= int(s) <= max:
            return int(s)
        if s == 'BRK':
            raise KeyboardInterrupt()

def getInputString(prompt, bConfirm=True, flushOutput=True):
    prompt += ' '
    while True:
        s = getRawInput(prompt, flushOutput).strip()
        if s == 'BRK':
            raise KeyboardInterrupt()
        if s:
            if not bConfirm or getInputBool('you intended to write: ' + s):
                return ustr(s)

def getInputFromChoices(prompt, arrChoices, fnOtherCommands=None,
        otherCommandsContext=None, flushOutput=True, cancelString='0) cancel', zeroBased=False):
    """allows user to choose from a numbered list.
    return value is the tuple (index, text)
    if user cancels, return value is the tuple (-1, 'Cancel')"""
    if cancelString:
        trace(cancelString)
    for i, choice in enumerate(arrChoices):
        num = i if zeroBased else i+1
        trace('%d) %s'%(num, choice))
    while True:
        # use a loop, since we'll re-ask on invalid inputs
        s = getRawInput(prompt, flushOutput).strip()
        if s == '0' and cancelString:
            return -1, 'Cancel'
        elif s == 'BRK':
            raise KeyboardInterrupt()
        elif s.isdigit():
            n = int(s) if zeroBased else (int(s) - 1)
            if n >= 0 and n < len(arrChoices):
                return n, arrChoices[n]
            else:
                trace('out of range')
                continue
        elif fnOtherCommands:
            breakLoop = fnOtherCommands(s, arrChoices, otherCommandsContext)
            if breakLoop:
                return (-1, breakLoop)

def getRawInput(prompt, flushOutput=True):
    print(getPrintable(prompt))
    if flushOutput:
        _sys.stdout.flush()
    assertTrue(_sys.version_info[0] >= 3)
    return input(getPrintable(''))

# endregion
# region user messages

def err(*args):
    s = ' '.join(map(getPrintable, args))
    raise RuntimeError('fatal error\n' + getPrintable(s))

gRedirectAlertCalls = _types.SimpleNamespace()
gRedirectAlertCalls.fnHook = None
def alert(*args, flushOutput=True, always=False):
    """show an alert to the user (they can press Enter to continue).
    can be suppressed for automated tests via gRedirectAlertCalls"""
    s = ' '.join(map(getPrintable, args))
    if gRedirectAlertCalls.fnHook and not always:
        gRedirectAlertCalls.fnHook(s)
    else:
        trace(s)
        getRawInput('press Enter to continue', flushOutput)

def warn(*args, flushOutput=True, always=False):
    """show an alert to the user (they can choose if they want to continue).
    can be suppressed for automated tests via gRedirectAlertCalls"""
    s  = ' '.join(map(getPrintable, args))
    if gRedirectAlertCalls.fnHook and not always:
        gRedirectAlertCalls.fnHook(s)
    else:
        trace('warning\n' + getPrintable(s))
        if not getInputBool('continue?', flushOutput):
            raise RuntimeError('user chose not to continue after warning')

# endregion
# region using tk gui

def getInputBoolGui(prompt):
    "Ask yes or no. Returns True on yes and False on no."
    from tkinter import messagebox as tkMessageBox
    return tkMessageBox.askyesno(title=' ', message=prompt)

def getInputYesNoCancelGui(prompt):
    "Ask yes, no, or cancel. Returns the string chosen."
    choice, choiceText = getInputFromChoicesGui(prompt, ['Yes', 'No', 'Cancel'])
    if choice == -1:
        return 'Cancel'
    elif choice == 0:
        return 'Yes'
    elif choice == 1:
        return 'No'
    else:
        return 'Cancel'

def _createTkSimpleDialog():
    "helper for opening tkSimpleDialogs"
    import tkinter as Tkinter
    from tkinter import simpledialog as tkSimpleDialog
    # need to create a root window or we'll fail because parent is none.
    root = Tkinter.Tk()
    root.withdraw()
    return Tkinter, tkSimpleDialog, root

def getInputFloatGui(prompt, default=None, min=0.0, max=100.0, title=''):
    "validated to be an float (decimal number). Returns None on cancel."
    Tkinter, tkSimpleDialog, root = _createTkSimpleDialog()
    options = dict(initialvalue=default) if default is not None else dict()
    return tkSimpleDialog.askfloat(' ', prompt, minvalue=min, maxvalue=max, **options)

def getInputStringGui(prompt, initialvalue=None, title=' '):
    "returns '' on cancel"
    Tkinter, tkSimpleDialog, root = _createTkSimpleDialog()
    options = dict(initialvalue=initialvalue) if initialvalue else dict()
    s = tkSimpleDialog.askstring(title, prompt, **options)
    return '' if s is None else s

def getInputFromChoicesGui(prompt, arOptions):
    """allows user to choose from a list.
    return value is the tuple (index, text)
    if user cancels, return value is the tuple (-1, 'Cancel')"""
    import tkinter as Tkinter
    assert len(arOptions) > 0
    retval = [None]

    def setResult(v):
        retval[0] = v
        
    def findUnusedLetter(dictUsed, newWord):
        for i, c in enumerate(newWord):
            if c.isalnum() and c.lower() not in dictUsed:
                dictUsed[c] = True
                return i
                
        return None

    # http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
    class ChoiceDialog:
        def __init__(self, parent):
            top = self.top = Tkinter.Toplevel(parent)
            Tkinter.Label(top, text=prompt).pack()
            top.title('Choice')

            lettersUsed = dict()
            box = Tkinter.Frame(top)
            for i, text in enumerate(arOptions):
                opts = dict()
                opts['text'] = text
                opts['width'] = 10
                opts['command'] = lambda which=i: self.onBtn(which)

                whichToUnderline = findUnusedLetter(lettersUsed, text)
                if whichToUnderline is not None:
                    opts['underline'] = whichToUnderline

                    # if the label is has t underlined, t is keyboard shortcut
                    top.bind(text[whichToUnderline].lower(), lambda _, which=i: self.onBtn(which))

                if i == 0:
                    opts['default'] = Tkinter.ACTIVE

                w = Tkinter.Button(box, **opts)
                w.pack(side=Tkinter.LEFT, padx=5, pady=5)

            top.bind("<Return>", lambda unused: self.onBtn(0))
            top.bind("<Escape>", lambda unused: self.cancel())
            box.pack(pady=5)
            parent.update()

        def cancel(self):
            self.top.destroy()

        def onBtn(self, nWhich):
            setResult(nWhich)
            self.top.destroy()

    root = Tkinter.Tk()
    root.withdraw()
    d = ChoiceDialog(root)
    root.wait_window(d.top)
    result = retval[0]
    if result is None:
        return -1, 'Cancel'
    else:
        return result, arOptions[result]

def errGui(*args):
    s = ' '.join(map(getPrintable, args))
    from tkinter import messagebox as tkMessageBox
    tkMessageBox.showerror(title='Error', message=getPrintable(s))
    raise RuntimeError('fatal error\n' + getPrintable(s))

def alertGui(*args):
    s = ' '.join(map(getPrintable, args))
    from tkinter import messagebox as tkMessageBox
    tkMessageBox.showinfo(title=' ', message=getPrintable(s))

def warnGui(*args):
    s = ' '.join(map(getPrintable, args))
    from tkinter import messagebox as tkMessageBox
    if not tkMessageBox.askyesno(title='Warning', message=getPrintable(s) + '\nContinue?', icon='warning'):
        raise RuntimeError('user chose not to continue after warning')

def getOpenFileGui(initialdir=None, types=None, title='Open'):
    "Specify types in the format ['.png|Png image','.gif|Gif image'] and so on."
    import tkinter.filedialog as tkFileDialog
    return _getFileDialogGui(tkFileDialog.askopenfilename, initialdir, types, title)

def getSaveFileGui(initialdir=None, types=None, title='Save As'):
    "Specify types in the format ['.png|Png image','.gif|Gif image'] and so on."
    import tkinter.filedialog as tkFileDialog
    return _getFileDialogGui(tkFileDialog.asksaveasfilename, initialdir, types, title)

_gDirectoryHistory = {}
def _getFileDialogGui(fn, initialdir, types, title, directoryHistory=None):
    "Helper that keeps a list of recently used directories"
    if initialdir is None:
        if directoryHistory:
            initialdir = _gDirectoryHistory.get(repr(types), '.')

    kwargs = dict()
    if types is not None:
        aTypes = [(type.split('|')[1], type.split('|')[0]) for type in types]
        defaultExtension = aTypes[0][1]
        kwargs['defaultextension'] = defaultExtension
        kwargs['filetypes'] = aTypes

    result = fn(initialdir=initialdir, title=title, **kwargs)
    if result:
        if directoryHistory:
            directoryHistory[repr(types)] = _os.path.split(result)[0]

    return result

# endregion

# get better arrowkey history in macos
try:
    import gnureadline
except:
    try:
        import readline
    except:
        pass
