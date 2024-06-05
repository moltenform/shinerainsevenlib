
import time as _time
import os as _os
from .m4_core_ui import *

class SrssLooper:
    def __init__(self, input):
        self._showPercentages = False
        self._pauseEveryNTimes = None
        self._pauseEverySeconds = None
        self._input = input
        self._resetState()
    
    def _resetState(self):
        self._didNoMeaningfulWork = False
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
                newIter, lambda item: item==self._waitUntilValueSeen)
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
        self._didNoMeaningfulWork = True

    def __iter__(self):
        self._resetState()
        self._currentIter = self._getIter()
        self._estimateCount = SrssLooper.countIterable(self._getIter())
        return self

    def __next__(self):
        self._counter += 1
        self._showPercent()
        if not self.flagDidNoMeaningfulWork:
            self._countMeaningfulWork += 1
            if self._countMeaningfulWork % self._pauseEveryNTimes == 0:
                trace('sleeping')
                _time.sleep(self._pauseEverySeconds)
                trace('waking')
        
        return next(self._currentIter)
    
    def _showPercent(self):
        if not self._showPercentages:
            return
        
        percentage = int(100*self._counter/self._estimateCount)
        percentage = clampNumber(percentage, 0.0, 99.9)
        if percentage != self._prevPercentShown:
            self._prevPercentShown = percentage
            trace(self._showPercentages, str(percentage) + '%')

    @staticmethod
    def skipForwardUntilTrue(iter, fnWaitUntil):
        if isinstance(iter, list):
            iter = (item for item in iter)
            
        hasSeen = False
        for value in iter:
            if not hasSeen and fnWaitUntil(value):
                hasSeen = True
            if hasSeen:
                yield value
    
    @staticmethod
    def countIterable(iter):
        return sum(1 for item in iter)
    

class SrssFileIterator:
    def getDefaultPrefs(self):
        prefs = Bucket()
        prefs.allowedExtsWithDot = None
        prefs.fnIncludeTheseFiles = None
        prefs.fnIncludeTheseDirs = None
        prefs.followSymlinks = False
        prefs.filesOnly = True
        prefs.allowRelativePaths = False
        prefs.excludeNodeModules = True
        prefs.recurse = True
        return prefs

    def __init__(self, rootOrListOfRoots, **params):
        self.prefs = mergeParamsIntoBucket(self.getDefaultPrefs(), params)
        roots = [rootOrListOfRoots] if isinstance(self.roots, str) else rootOrListOfRoots
        self.roots = roots
        
        for root in self.roots:
            assertTrue(self.prefs.allowRelativePaths or _os.path.isabs(root), 'relative paths not allowed', root)
        
        # make it a little faster
        if isinstance(self.prefs.allowedExtsWithDot, list):
            self.prefs.allowedExtsWithDot = set(self.prefs.allowedExtsWithDot)
    
    def getIterator(self):
        def fnFilterDirs(path):
            if self.prefs.excludeNodeModules and ('/node_modules/' in path or '\\node_modules\\' in path):
                return False
            elif self.prefs.fnIncludeTheseDirs and not self.prefs.fnIncludeTheseDirs(path):
                return False
            else:
                return True
        
        def fnIterator():
            from .. import files
            
            for root in self.roots:
                for obj in files.recurseFileInfo(root,
                        followSymlinks=self.prefs.followSymlinks, filesOnly=self.prefs.filesOnly, 
                        fnFilterDirs=fnFilterDirs, 
                        fnDirectExceptionsTo=None, recurse=self.prefs.recurse):
                    
                    if self.prefs.allowedExtsWithDot:
                        ext = files.splitExt(obj.path)[1].lower()
                        if ext not in self.prefs.allowedExtsWithDot:
                            continue
                    
                    if self.prefs.fnIncludeTheseFiles and not self.prefs.fnIncludeTheseFiles(obj.path):
                        continue
                        
                    yield obj
        return fnIterator
    
    def getCount(self):
        return SrssLooper.countIterable(self.getIterator())

