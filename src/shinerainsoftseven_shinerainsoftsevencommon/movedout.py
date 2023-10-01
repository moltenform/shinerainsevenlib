
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




