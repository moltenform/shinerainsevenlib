
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import time as _time
import os as _os
import re as _re
import shutil as _shutil
import contextlib as _contextlib
from collections.abc import Iterable

from .m4_core_ui import *

class SrssLooper:
    """Helpful for batch processing, when you want to add pauses every n iterations
    
    >>> loop = SrssLooper(list(range(10)))
    >>> loop.showPercentageEstimates()
    >>> loop.addPauses(2, seconds=2)
    >>> loop.waitUntilValueSeen(3)
    >>> for number in loop:
    >>>     if number % 2 == 0:
    >>>         print('skipping even number', number)
    >>>         loop.flagDidNoMeaningfulWork()
    >>>     else:
    >>>         print('found an odd number', number)

    input can be a
        list 
        iterable
        lambda that returns an iterable
            useful if you need to compute the length without producing the list
    waitUntilValueSeen can be a
        value
        lambda that returns boolean- the first time it returns True,
            we'll start the loop
    """

    def __init__(self, listOrLambda):
        self._showPercentages = False
        self._pauseEveryNTimes = None
        self._pauseEverySeconds = None
        self._waitUntilValueSeen = DefaultVal
        self._fnFormatStateToPrint = DefaultVal
        self._didMeaningfulWork = True

        # convert to iter
        if isinstance(listOrLambda, list):
            self._len = len(listOrLambda)
            self._iter = iter(listOrLambda)
        elif callable(listOrLambda):
            tempIter = listOrLambda()
            self._len = SrssLooper.countIterable(tempIter)
            self._iter = listOrLambda()
        elif isinstance(listOrLambda, Iterable):
            # there might be some __getitem__ iterables
            # that don't qualify as Iterable, but I've never needed to support them.
            self._len = -1
            self._iter = listOrLambda
        else:
            assertTrue(False, 'input must be list or iterable')

    def showPercentageEstimates(self, displayStr='\n...'):
        # it will be an estimate, since the iterable
        # might return a different number of items
        self._showPercentages = displayStr

    def setFormatStateToPrint(self, fn):
        self._fnFormatStateToPrint = fn

    def addPauses(self, pauseEveryNTimes=20, seconds=20):
        self._pauseEveryNTimes = pauseEveryNTimes
        self._pauseEverySeconds = seconds

    def waitUntilValueSeen(self, valOrFn):
        self._waitUntilValueSeen = valOrFn

    def flagDidNoMeaningfulWork(self):
        self._didMeaningfulWork = False

    def __iter__(self):
        countMeaningfulWork = 0 # we only want to pause when we've worked a lot
        counter = 0
        prevPercentShown = 0
        isStillWaiting = True
        shouldSkip = True
        self._didMeaningfulWork = True
        for v in self._iter:
            counter += 1
            counter, prevPercentShown = self._showPercent(v, counter, prevPercentShown)
            isStillWaiting, shouldSkip = self._shouldSkip(v, isStillWaiting, shouldSkip)
            if shouldSkip:
                continue

            if self._didMeaningfulWork:
                countMeaningfulWork += 1
                if self._pauseEveryNTimes and countMeaningfulWork % self._pauseEveryNTimes == 0:
                    trace('sleeping')
                    _time.sleep(self._pauseEverySeconds)
                    trace('waking')

            self._didMeaningfulWork = True
            yield v

    def _showPercent(self, v, counter, prevPercentShown):
        if not self._showPercentages:
            return counter, prevPercentShown

        if self._len == -1:
            # impossible to know the length of a raw iterator
            return counter, prevPercentShown
        elif self._len == 0:
            # prevent divide by 0
            self._len = 0.01

        percentage = int(100 * counter / (self._len))
        
        # clamp to 99% - because _len might be inaccurate
        percentage = clampNumber(percentage, 0.0, 99.9)
        if percentage != prevPercentShown:
            prevPercentShown = percentage
            s = str(percentage) + '%'
            if self._fnFormatStateToPrint is not DefaultVal:
                s += ' ' + str(self._fnFormatStateToPrint(v))

            trace(self._showPercentages, s)

        return counter, prevPercentShown
    
    def _shouldSkip(self, v, isStillWaiting, shouldSkip):
        if not isStillWaiting:
            isStillWaiting = False
            shouldSkip = False
            return isStillWaiting, shouldSkip

        if self._waitUntilValueSeen is DefaultVal:
            isStillWaiting = False
            shouldSkip = False
        elif callable(self._waitUntilValueSeen):
            isStillWaiting = not self._waitUntilValueSeen(v)
            shouldSkip = shouldSkip if isStillWaiting else False
        else:
            isStillWaiting = not self._waitUntilValueSeen == v
            shouldSkip = shouldSkip if isStillWaiting else False
        
        return isStillWaiting, shouldSkip

    @staticmethod
    def countIterable(itr):
        return sum(1 for _item in itr)

class SrssFileIterator:
    """Helpful for file iteration,
    adding some extra features to files.recurseFiles.
    Can be used to skip node_modules directories."""

    def __init__(self, rootOrListOfRoots, fnIncludeTheseFiles=None,
                 fnFilterDirs=None,
               allowRelativePaths=None,  excludeNodeModules=False, **params):
        self.fnIncludeTheseFiles = fnIncludeTheseFiles
        self.allowRelativePaths = allowRelativePaths
        self.excludeNodeModules = excludeNodeModules
        self.paramsForIterating = params
        self.fnFilterDirsFromUser = fnFilterDirs

        roots = [rootOrListOfRoots] if isinstance(rootOrListOfRoots, str) else rootOrListOfRoots
        self.roots = roots
        self._currentIter = None

        for root in self.roots:
            assertTrue(
                self.allowRelativePaths or _os.path.isabs(root),
                'relative paths not allowed',
                root,
            )
    
    def _filterDirs(self, path):
        if self.excludeNodeModules and (
            SrssFileIterator.pathContainsThisName(path, 'node_modules', )
        ):
            return False
        elif self.fnFilterDirsFromUser and not self.fnFilterDirsFromUser(path):
            return False
        else:
            return True

    def __iter__(self):
        from .. import files
        for root in self.roots:
            for obj in files.recurseFileInfo(
                root,
                fnFilterDirs=lambda path: self._filterDirs(path),
                **self.paramsForIterating
            ):
                if self.fnIncludeTheseFiles and not self.fnIncludeTheseFiles(
                    obj.path
                ):
                    continue

                yield obj

    @staticmethod
    def pathContainsThisName(path, exclude, ):
        regexp = _re.compile(r'[/\\]' + exclude + r'([/\\]|$)')
        return bool(regexp.search(path))

class CleanupTempFilesOnClose(_contextlib.ExitStack):
    """Register temp files to be deleted later.
    Example:

    with CleanupTempFilesOnClose() as cleanup:
        cleanup.registerTempFile('out.tmp')
        files.writeAll('out.tmp', 'abc')
        ...something that might throw
        files.delete('out.tmp')
    """

    def registerTempFile(self, path):
        def fn():
            if _os.path.exists(path):
                _os.unlink(path)

        self.callback(fn)


def removeEmptyFolders(path, removeRootIfEmpty=True, verbose=False):
    "Recursively removes empty directories"
    def removeEmptyFoldersImpl(path, removeRootIfEmpty=True, _weAreRecursing=False, verbose=False):
        if not _os.path.isdir(path):
            return

        # remove empty subfolders
        subPaths = _os.listdir(path)
        if len(subPaths):
            for subpath in subPaths:
                fullPath = _os.path.join(path, subpath)
                if _os.path.isdir(fullPath):
                    removeEmptyFoldersImpl(fullPath, removeRootIfEmpty=removeRootIfEmpty, _weAreRecursing=True)

        # if folder empty, delete it
        subPaths = _os.listdir(path)
        if len(subPaths) == 0:
            if not _weAreRecursing and not removeRootIfEmpty:
                pass
            else:
                if verbose:
                    trace('Deleting empty dir', path)

                _os.rmdir(path)

    return removeEmptyFoldersImpl(path, removeRootIfEmpty=removeRootIfEmpty, verbose=verbose)

