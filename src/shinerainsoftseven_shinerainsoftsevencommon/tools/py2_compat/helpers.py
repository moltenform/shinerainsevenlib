

def getTk():
    try:
        from tkinter import Tk
    except ImportError:
        from Tkinter import Tk
    
    if isPy3OrNewer:
        import tkinter as Tkinter
        from tkinter import simpledialog as tkSimpleDialog
    else:
        import Tkinter
        import tkSimpleDialog
    
    if isPy3OrNewer:
        import tkinter.filedialog as tkFileDialog
    else:
        import tkFileDialog

