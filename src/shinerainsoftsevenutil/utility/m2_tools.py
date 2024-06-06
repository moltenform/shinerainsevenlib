import os as _os
from ..core import *

def removeEmptyFolders(path, removeRootIfEmpty=True, isRecurse=False, verbose=False):
    if not _os.path.isdir(path):
        return

    # remove empty subfolders
    files = _os.listdir(path)
    if len(files):
        for f in files:
            fullpath = _os.path.join(path, f)
            if _os.path.isdir(fullpath):
                removeEmptyFolders(fullpath, removeRootIfEmpty=removeRootIfEmpty, isRecurse=True)

    # if folder empty, delete it
    files = _os.listdir(path)
    if len(files) == 0:
        if not isRecurse and not removeRootIfEmpty:
            pass
        else:
            if verbose:
                trace('Deleting empty dir', path)

            _os.rmdir(path)
