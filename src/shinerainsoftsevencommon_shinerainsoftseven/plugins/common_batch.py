
from ..common_util import *
from .. import files
import os


class FileIteratorHelper(object):
    def getDefaultConfigs(self):
        configs = Bucket()
        configs.allowedExtsWithDot = None
        configs.fnIncludeThese = None
        configs.followSymlinks = False
        configs.filesOnly = True
        configs.resumeFrom = None
        configs.allowRelativePaths = False
        configs.excludeNodeModules = True
        configs.recurse = True
        return configs

    def __init__(self, roots, **params):
        self.configs = mergeParamsIntoBucket(self.getDefaultConfigs(), params)
        self.roots = roots
        for root in roots:
            assertTrue(allowRelativePaths or os.path.isabs(root), 'relative paths not allowed', root)
        
    def getIterator(self):
        def _getIterator():
            for root in self.roots:
                for obj in files.recursefileinfo(root,
                        followSymlinks=self.configs.followSymlinks, filesOnly=self.configs.filesOnly, fnFilterDirs=None, 
                        fnDirectExceptionsTo=None, recurse=self.configs.recurse):
                    
                    if self.configs.allowedExtsWithDot:
                        ext = files.getExt(obj.path)[1].lower()
                        if ext not in self.configs.allowedExtsWithDot:
                            continue
                    
                    if self.configs.fnIncludeThese and not self.configs.fnIncludeThese(obj.path):
                        continue
                        
                    if self.configs.excludeNodeModules and ('/node_modules/' in obj.path or '\\node_modules\\' in obj.path):
                        continue
                        
                    yield obj
        
        if self.resumeFrom:
            return files.waitUntilTrue(_getIterator(), lambda obj: obj.path==self.resumeFrom)
        else:
            return _getIterator()
    
    def getCount(self):
        return len(self.getIterator())

    

class BatchJobDisplayer:
    def __init__(self, totalCount):
        self.totalCount = totalCount
        self.prevShown = None
        self.autoCounter = 0
    
    def updateAuto(self, showProgressString=''):
        self.autoCounter += 1
        self.update(self.autoCounter, showProgressString=showProgressString)
        
    def update(self, currentCount, showProgressString=''):
        percentage = int(100*currentCount/self.totalCount)
        if percentage != self.prevShown:
            self.prevShown = percentage
            trace(str(percentage) + '%', showProgressString)

    
class BatchJobDisplayerWithPauses(BatchJobDisplayer):
    def __init__(self, totalCount, sleepAfterEveryN=None, sleepDuration=5):
        self.sleepAfterEveryN = sleepAfterEveryN
        self.sleepDuration = sleepDuration
        super().__init__(totalCount=totalCount)
    
    def update(self, currentCount, showProgressString=''):
        if self.sleepAfterEveryN and currentCount % self.sleepAfterEveryN == 0:
            trace('sleeping', showProgressString)
            import time
            time.sleep(self.sleepDuration)
            trace('waking')
            
        super().update(currentCount, showProgressString=showProgressString)
    

def removeEmptyFolders(path, removeRootIfEmpty=True, isRecurse=False, verbose=False):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath, removeRootIfEmpty=removeRootIfEmpty, isRecurse=True)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0:
        if not isRecurse and not removeRootIfEmpty:
            pass
        else:
            if verbose:
                trace('Deleting empty dir', path)
                
            os.rmdir(path)

from enum import Enum, auto

class WhatIfResultIsBigger(Enum):
    warn = auto()
    alwaysUseNewFile = auto()
    neverReplace = auto()


# inPath -- target file, like /home/ben/my_song.wav
# tmpPath -- send output to working dir, like /tmp/my_program/my_song.flac
# using a working dir is good 1) in case programs don't support unicode filenames 2) crashes don't leave any partial files behind.
# outPath -- result location, like /home/ben/my_song.flac

class TrackTotalSaved:
    def __init__(self, mustSaveAtLeastBytes=0, whatIfResultIsBigger=WhatIfResultIsBigger.neverReplace, 
            minimumValidSize=16):
        self.mustSaveAtLeastBytes = mustSaveAtLeastBytes
        self.whatIfResultIsBigger = whatIfResultIsBigger
        self.minimumValidSize = minimumValidSize
    
    def _useNewFileAndRemoveExistingFile(self, inPath, tmpPath, outPath, inSize, outSize):
        # the move to a temp name handles the case where inPath==outPath,
        # but we don't want to softDelete first, which leaves a window where no files are there anymore
        inPathWithSuffix = inPath + '$$$---temp---$$$'
        files.move(inPath, inPathWithSuffix, False)
        files.move(tmpPath, outPath, False)
        softDeleteFile(inPathWithSuffix)
            
        self.totalSaved += (inSize - outSize)
    
    def seeIfSavedEnough(self, inPath, tmpPath, outPath):
        inSize = files.getsize(inPath)
        outSize = files.getsize(tmpPath)
        if outSize < self.minimumValidSize:
            assertTrue(False, 'error-- output is very small or 0 size ', inPath, tmpPath)
        
        if inSize - outSize >= mustSaveAtLeastBytes:
            self._successReplace(inPath, tmpPath, outPath, inSize, outSize)
        else:
            trace(f'output {outPath} did not save enough - the difference is {formatSize(outSize - inSize)}')
            if self.whatIfResultIsBigger == WhatIfResultIsBigger.warn:
                shouldMoveIn = getInputBool('use the output even though it did not save enough? y/n')
                if shouldMoveIn:
                    self._successReplace(inPath, tmpPath, outPath, inSize, outSize)
                else:
                    pass
            elif self.whatIfResultIsBigger == WhatIfResultIsBigger.alwaysUseNewFile:
                self._successReplace(inPath, tmpPath, outPath, inSize, outSize)
            elif self.whatIfResultIsBigger == WhatIfResultIsBigger.neverReplace:
                pass
            else:
                assertTrue(False, 'unknown whatIfResultIsBigger')



