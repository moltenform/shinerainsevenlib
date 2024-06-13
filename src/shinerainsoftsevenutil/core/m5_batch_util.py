
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import time as _time
import os as _os
import re as _re
import shutil as _shutil
import contextlib as _contextlib

from .m4_core_ui import *

class SrssLooper:
    """Helpful for batch processing, when you want to add pauses every n iterations
    Example:
    loop = SrssLooper(list(range(10)))
    loop.showPercentageEstimates()
    loop.addPauses(2, seconds=2)
    loop.waitUntilValueSeen(3)
    for number in loop:
        if number % 2 == 0:
            print('skipping even number', number)
            loop.flagDidNoMeaningfulWork()
        else:
            print('found an odd number', number)
    """

    def __init__(self, listOrLambda):
        self._showPercentages = False
        self._pauseEveryNTimes = None
        self._pauseEverySeconds = None
        self._waitUntilValueSeen = None
        self._input = listOrLambda

        # reset state
        self._didMeaningfulWork = True
        self._currentIter = None
        self._counter = 0
        self._countMeaningfulWork = 0
        self._estimateCount = None
        self._prevPercentShown = None

    def _resetState(self):
        self._didMeaningfulWork = True
        self._currentIter = None
        self._counter = 0
        self._countMeaningfulWork = 0
        self._estimateCount = None
        self._prevPercentShown = None

    def _getIter(self):
        if callable(self._input):
            # must be a lambda that returns an iterable
            newIter = self._input()
        else:
            # must be a list
            assertTrue(isinstance(self._input, list))
            newIter = self._input

        if self._waitUntilValueSeen:
            return SrssLooper.skipForwardUntilTrue(
                newIter, lambda item: item == self._waitUntilValueSeen
            )
        else:
            return newIter

    def showPercentageEstimates(self, displayStr='\n...'):
        # it will be an estimate, since the iterable
        # might return a different number of items
        self._showPercentages = displayStr

    def addPauses(self, pauseEveryNTimes=20, seconds=20):
        self._pauseEveryNTimes = pauseEveryNTimes
        self._pauseEverySeconds = seconds

    def waitUntilValueSeen(self, v):
        self._waitUntilValueSeen = v

    def flagDidNoMeaningfulWork(self):
        self._didMeaningfulWork = False

    def __iter__(self):
        self._resetState()
        self._currentIter = self._getIter()
        self._estimateCount = SrssLooper.countIterable(self._getIter())
        return self

    def __next__(self):
        self._counter += 1
        self._showPercent()
        if self._didMeaningfulWork:
            self._countMeaningfulWork += 1
            if self._countMeaningfulWork % self._pauseEveryNTimes == 0:
                trace('sleeping')
                _time.sleep(self._pauseEverySeconds)
                trace('waking')

        self._didMeaningfulWork = True
        return next(self._currentIter)

    def _showPercent(self):
        if not self._showPercentages:
            return

        percentage = int(100 * self._counter / self._estimateCount)
        percentage = clampNumber(percentage, 0.0, 99.9)
        if percentage != self._prevPercentShown:
            self._prevPercentShown = percentage
            trace(self._showPercentages, str(percentage) + '%')

    @staticmethod
    def skipForwardUntilTrue(itr, fnWaitUntil):
        if isinstance(itr, list):
            itr = (item for item in itr)

        hasSeen = False
        for value in itr:
            if not hasSeen and fnWaitUntil(value):
                hasSeen = True
            if hasSeen:
                yield value

    @staticmethod
    def countIterable(itr):
        return sum(1 for item in itr)

class SrssFileIterator:
    """
    Helpful for file iteration,
    adding some extra features to files.recurseFiles.
    Very useful for skipping big node_modules directories.
    """

    def getDefaultPrefs(self):
        self.prefs.allowedExtsWithDot = None
        self.prefs.fnIncludeTheseFiles = None
        self.prefs.fnIncludeTheseDirs = None
        self.prefs.fnDirectExceptionsTo = None
        self.prefs.followSymlinks = False
        self.prefs.filesOnly = True
        self.prefs.allowRelativePaths = False
        self.prefs.excludeNodeModules = False
        self.prefs.recurse = True

    def __init__(self, rootOrListOfRoots, **params):
        self.prefs = Bucket()
        self.getDefaultPrefs()
        mergeDictIntoBucket(self.prefs, params)
        roots = [rootOrListOfRoots] if isinstance(rootOrListOfRoots, str) else rootOrListOfRoots
        self.roots = roots
        self._currentIter = None

        for root in self.roots:
            assertTrue(
                self.prefs.allowRelativePaths or _os.path.isabs(root),
                'relative paths not allowed',
                root,
            )

        # make it a little faster
        if isinstance(self.prefs.allowedExtsWithDot, list):
            self.prefs.allowedExtsWithDot = set(self.prefs.allowedExtsWithDot)

    def __iter__(self):
        self._currentIter = self._getIterator()()
        return self

    def __next__(self):
        return next(self._currentIter)

    def _getIterator(self):
        def fnFilterDirs(path):
            if self.prefs.excludeNodeModules and (
                SrssFileIterator.pathHasThisDirectory('node_modules', path)
            ):
                return False
            elif self.prefs.fnIncludeTheseDirs and not self.prefs.fnIncludeTheseDirs(path):
                return False
            else:
                return True

        def fnIterator():
            from .. import files

            for root in self.roots:
                for obj in files.recurseFileInfo(
                    root,
                    followSymlinks=self.prefs.followSymlinks,
                    filesOnly=self.prefs.filesOnly,
                    fnFilterDirs=fnFilterDirs,
                    fnDirectExceptionsTo=self.prefs.fnDirectExceptionsTo,
                    recurse=self.prefs.recurse,
                ):
                    if self.prefs.allowedExtsWithDot:
                        ext = files.splitExt(obj.path)[1].lower()
                        if ext not in self.prefs.allowedExtsWithDot:
                            continue

                    if self.prefs.fnIncludeTheseFiles and not self.prefs.fnIncludeTheseFiles(
                        obj.path
                    ):
                        continue

                    yield obj

        return fnIterator

    def getCount(self):
        return SrssLooper.countIterable(self._getIterator()())

    @staticmethod
    def pathHasThisDirectory(suffix, path):
        regexp = _re.compile(r'[/\\]' + suffix + r'([/\\]|$)')
        return bool(regexp.search(path))

class CleanupTempFilesOnException(_contextlib.ExitStack):
    """Register temp files to be deleted later.
    Example:

    with CleanupTempFilesOnException() as cleanup:
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


def removeEmptyFolders(path, removeRootIfEmpty=True, isRecurse=False, verbose=False):
    "Recursively removes empty directories"
    if not _os.path.isdir(path):
        return

    # remove empty subfolders
    paths = _os.listdir(path)
    if len(paths):
        for path in paths:
            fullPath = _os.path.join(path, path)
            if _os.path.isdir(fullPath):
                removeEmptyFolders(fullPath, removeRootIfEmpty=removeRootIfEmpty, isRecurse=True)

    # if folder empty, delete it
    paths = _os.listdir(path)
    if len(paths) == 0:
        if not isRecurse and not removeRootIfEmpty:
            pass
        else:
            if verbose:
                trace('Deleting empty dir', path)

            _os.rmdir(path)
