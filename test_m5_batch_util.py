
# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
import os
import random
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from common import fileInfoListToList, fxDirPlain, fxTreePlain

class TestSrssLooper:
    def testSrssLooperBasic(self):
        loop = srss.SrssLooper([1,2,3])
        numbersSeen = []
        for number in loop:
            numbersSeen.append(number)

        assert numbersSeen == [1,2,3]
    
    def getIteratorOptions(self):
        class GetIteratorWithUnreliableLength:
            countCalls = 0
            def get(self):
                self.countCalls += 1
                if self.countCalls > 1:
                    return (x for x in [1, 2,3])
                else:
                    return (x for x in [])
        
        instance = GetIteratorWithUnreliableLength()
        return {
            'plain': [1,2,3],
            'iter': (x for x in [1,2,3]),
            # SrssLooper has a feature where it can estimate iter length,
            'lambda': lambda: (x for x in [1,2,3]),
            # SrssLooper should be resilient to inaccurate lengths
            'lambdaUnreliableLen': lambda: instance.get(),
        }

    def getWaitUntilOptions(self):
        return {
            'default': DefaultVal,
            'valNone': None, # literally waits until 'None' appears
            'plain': 2,
            'lambda': lambda item: item == 2,
        }

    def testSrssLooperTryOptions(self):
        for listInputKey in self.getIteratorOptions().keys():
            for waitUntilKey in self.getWaitUntilOptions().keys():
                for showPercentageEstimates in [True, False]:
                    self.runOne(listInputKey, waitUntilKey, showPercentageEstimates)
    
    def runOne(self, listInputKey, waitUntilKey, showPercentageEstimates):
        # important: generate a new instance each time through loop,
        # since you can't re-use an iterator
        listInput = self.getIteratorOptions()[listInputKey]
        waitUntil = self.getWaitUntilOptions()[waitUntilKey]
        numbersSeen = []
        loop = srss.SrssLooper(listInput)
        loop.waitUntilValueSeen(waitUntil)
        if showPercentageEstimates:
            loop.showPercentageEstimates()
        
        for number in loop:
            numbersSeen.append(number)
        
        if listInputKey == 'iter':
            assert loop._len == -1
        elif listInputKey == 'lambdaUnreliableLen':
            assert loop._len == 0 or loop._len == 0.01
        else:
            assert loop._len == 3
        
        if waitUntilKey == 'default':
            assert numbersSeen == [1,2,3]
        elif waitUntilKey == 'valNone':
            assert numbersSeen == []
        else:
            assert numbersSeen == [2,3]

    #~ def testSrssLooperAdvanced(self):
        #~ # you should now see a loop from 3 to 100 that pauses every 20
        #~ loop = srss.SrssLooper(list(range(100)))
        #~ loop.showPercentageEstimates()
        #~ loop.addPauses(10, seconds=2)
        #~ loop.waitUntilValueSeen(3)
        #~ loop.setFormatStateToPrint(lambda x: f'currently at: {x}')
        #~ timeStart = srss.getNowAsMillisTime()
        #~ numbersSeen = []
        #~ evensSeen = []
        #~ oddsSeen = []
        #~ for number in loop:
            #~ numbersSeen.append(number)
            #~ if number % 2 == 0:
                #~ evensSeen.append(number)
                #~ loop.flagDidNoMeaningfulWork()
            #~ else:
                #~ oddsSeen.append(number)
        
        #~ timeTaken = srss.getNowAsMillisTime() - timeStart
        #~ timeTakenInSeconds = timeTaken / 1000
        #~ assert numbersSeen == list(range(3, 100))
        #~ assert evensSeen == list(range(4, 100, 2))
        #~ assert oddsSeen == list(range(3, 100, 2))
        #~ expectedTime = 2 * ((100-3)/20)
        #~ assert timeTakenInSeconds == pytest.approx(expectedTime, abs=5)

class TestFileIterator:
    def testPathContainsDirWithThisName(self):
        for SEP in ('/', '\\'):
            assert (not SrssFileIterator.pathContainsThisName('', 'node_modules'))
            assert (not SrssFileIterator.pathContainsThisName('abcd', 'node_modules'))
            assert (not SrssFileIterator.pathContainsThisName(f'ab{SEP}cd', 'node_modules'))

            assert (not SrssFileIterator.pathContainsThisName(f'a{SEP}node{SEP}_modules{SEP}b', 'node_modules'))
            assert (not SrssFileIterator.pathContainsThisName(f'a{SEP}notnode_modules{SEP}b', 'node_modules'))
            assert (not SrssFileIterator.pathContainsThisName(f'a{SEP}notnode_modules{SEP}', 'node_modules'))
            assert (not SrssFileIterator.pathContainsThisName(f'a{SEP}notnode_modules', 'node_modules'))
            assert (not SrssFileIterator.pathContainsThisName(f'a{SEP}node_modulesnot{SEP}b', 'node_modules'))
            assert (not SrssFileIterator.pathContainsThisName(f'a{SEP}node_modulesnot{SEP}', 'node_modules'))
            assert (not SrssFileIterator.pathContainsThisName(f'a{SEP}node_modulesnot', 'node_modules'))
            assert (SrssFileIterator.pathContainsThisName(f'a{SEP}node_modules{SEP}b', 'node_modules'))
            assert (SrssFileIterator.pathContainsThisName(f'a{SEP}node_modules{SEP}', 'node_modules'))
            assert (SrssFileIterator.pathContainsThisName(f'a{SEP}node_modules', 'node_modules'))
    
    def testWithFilters(self, fxTreePlain):
        files.makeDirs(fxTreePlain + '/node_modules')
        files.writeAll(fxTreePlain + '/node_modules/a.txt', 'a')
        iter = SrssFileIterator(fxTreePlain, 
            fnFilterDirs=lambda path: not path.replace('\\', '/').endswith('fb/a/fb'), excludeNodeModules=True)
        expected = ['/fb/a/bz/aa.txt', '/fb/a/bz/bb.txt', '/fb/a/bz/fb/cc.txt', 
                       '/fb/a/bz/zz.txt', '/fb/a/r1.txt', '/fb/fb/cc.txt', 
                       '/fb/r2.txt', '/r3.txt']
        assert fileInfoListToList(fxTreePlain, iter) == expected
        

        iter = SrssFileIterator(fxTreePlain,
            fnFilterDirs=lambda path: not path.replace('\\', '/').endswith('fb/a/bz'), excludeNodeModules=False)
        expected = ['/fb/a/fb/a.txt', '/fb/a/fb/b.txt', '/fb/a/fb/c/c0.txt', 
                       '/fb/a/fb/c/c1.txt', '/fb/a/r1.txt', '/fb/fb/cc.txt', 
                       '/fb/r2.txt', '/node_modules/a.txt', '/r3.txt']
        assert fileInfoListToList(fxTreePlain, iter) == expected

    def testPassIterParams(self, fxTreePlain):
        files.writeAll(fxTreePlain + '/fb/a/fb/a.mp3', 'a')
        files.writeAll(fxTreePlain + '/fb/a/bz/b.mp3', 'a')
        iter = SrssFileIterator(fxTreePlain, allowedExts=['mp3'])
        got = fileInfoListToList(fxTreePlain, iter)
        assert got == ['/fb/a/bz/b.mp3', '/fb/a/fb/a.mp3']

    def testIncludeTheseFiles(self, fxTreePlain):
        files.writeAll(fxTreePlain + '/fb/a/fb/a.mp3', 'a')
        files.writeAll(fxTreePlain + '/fb/a/bz/b.mp3', 'a')
        iter = SrssFileIterator(fxTreePlain, fnIncludeTheseFiles=lambda s: s.endswith('.mp3'))
        got = fileInfoListToList(fxTreePlain, iter)
        assert got == ['/fb/a/bz/b.mp3', '/fb/a/fb/a.mp3']
    
    def testMultipleRoots(self, fxTreePlain):
        root1 = fxTreePlain + '/fb/a/fb'
        root2 = fxTreePlain + '/fb/a/bz/fb'
        iter = SrssFileIterator([root1, root2])
        got = fileInfoListToList(fxTreePlain, iter)
        assert got == ['/fb/a/bz/fb/cc.txt', '/fb/a/fb/a.txt', '/fb/a/fb/b.txt', 
                       '/fb/a/fb/c/c0.txt', '/fb/a/fb/c/c1.txt']

    def testNeedsAbsPaths(self):
        with pytest.raises(AssertionError, match='relative paths'):
            _instance = SrssFileIterator('./directory')

        with pytest.raises(AssertionError, match='relative paths'):
            _instance = SrssFileIterator('..')

class TestCleanupTempFiles:
    def testCleanupTempFilesOnClose(self, fxDirPlain):
        files.writeAll(f'{fxDirPlain}/a.txt', 'aaa')
        files.writeAll(f'{fxDirPlain}/b.txt', 'bbb')
        files.writeAll(f'{fxDirPlain}/c.txt', 'ccc')
        with srss.CleanupTempFilesOnClose() as cleanup:
            # clean up a newly created file
            files.writeAll(f'{fxDirPlain}/new.txt', 'new')
            cleanup.registerTempFile(f'{fxDirPlain}/new.txt')
            assert files.exists(f'{fxDirPlain}/new.txt')

            # clean up a previously made file
            cleanup.registerTempFile(f'{fxDirPlain}/a.txt')
            files.exists(f'{fxDirPlain}/a.txt')

            # should silently skip non-existant files
            cleanup.registerTempFile(f'{fxDirPlain}/not-exist.txt')
            assert not files.exists(f'{fxDirPlain}/not-exist.txt')
        
        # check they were deleted
        assert not files.exists(f'{fxDirPlain}/new.txt')
        assert not files.exists(f'{fxDirPlain}/a.txt')
        assert not files.exists(f'{fxDirPlain}/not-exist.txt')
        assert files.exists(f'{fxDirPlain}/b.txt')
        assert files.exists(f'{fxDirPlain}/c.txt')

    def testCleanupTempFilesOnException(self, fxDirPlain):
        files.writeAll(f'{fxDirPlain}/a.txt', 'aaa')
        files.writeAll(f'{fxDirPlain}/b.txt', 'bbb')
        files.writeAll(f'{fxDirPlain}/c.txt', 'ccc')
        def fn():
            with srss.CleanupTempFilesOnClose() as cleanup:
                cleanup.registerTempFile(f'{fxDirPlain}/b.txt')
                raise RuntimeError("cause exception")

        # should delete b but leave behind the other file(s)
        assertException(fn, RuntimeError, "cause exception")
        assert files.exists(f'{fxDirPlain}/a.txt')
        assert not files.exists(f'{fxDirPlain}/b.txt')
        assert files.exists(f'{fxDirPlain}/c.txt')

class TestCleanupEmptyDirs:
    def testBasic(self, fxTreePlain):
        files.delete(fxTreePlain + '/fb/a/fb/c/c0.txt')
        files.delete(fxTreePlain + '/fb/a/fb/c/c1.txt')
        files.delete(fxTreePlain + '/fb/a/bz/fb/cc.txt')
        removeEmptyDirs(fxTreePlain)
        got = fileInfoListToList(fxTreePlain, files.recurseDirs)
        assert got ==['', '/fb', '/fb/a', '/fb/a/bz', 
                      '/fb/a/fb', '/fb/fb']
    
    def testRemoveRootToo(self, fxTreePlain):
        files.delete(fxTreePlain + '/fb/a/fb/c/c0.txt')
        files.delete(fxTreePlain + '/fb/a/fb/c/c1.txt')
        files.delete(fxTreePlain + '/fb/a/bz/fb/cc.txt')
        
        removeEmptyDirs(fxTreePlain + '/fb/a/bz/fb', 
                           removeRootIfEmpty=False)
        got = fileInfoListToList(fxTreePlain, files.recurseDirs)
        assert got == ['', '/fb', '/fb/a', '/fb/a/bz', 
                       '/fb/a/bz/fb', '/fb/a/fb', 
                       '/fb/a/fb/c', '/fb/fb']
        
        removeEmptyDirs(fxTreePlain + '/fb/a/bz/fb', 
                           removeRootIfEmpty=True)
        got = fileInfoListToList(fxTreePlain, files.recurseDirs)
        assert got == ['', '/fb', '/fb/a', '/fb/a/bz', 
                       '/fb/a/fb', '/fb/a/fb/c', 
                       '/fb/fb']

    def testShouldIgnoreIfMissingOrIsFile(self, fxTreePlain):
        assert files.exists(fxTreePlain + '/fb/a/fb/c/c0.txt')
        removeEmptyDirs(fxTreePlain + '/fb/a/fb/c/c0.txt')
        assert files.exists(fxTreePlain + '/fb/a/fb/c/c0.txt')

        assert not files.exists(fxTreePlain + '/notexist')
        removeEmptyDirs(fxTreePlain + '/notexist')
        assert not files.exists(fxTreePlain + '/notexist')

