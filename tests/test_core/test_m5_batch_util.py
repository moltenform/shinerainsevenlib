
# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
import os
import random
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from common import fileInfoListToList, fixtureDir, fixtureFileTree

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

    def testSrssLooperAdvanced(self):
        # you should now see a loop from 3 to 100 that pauses every 20
        loop = srss.SrssLooper(list(range(100)))
        loop.showPercentageEstimates()
        loop.addPauses(10, seconds=2)
        loop.waitUntilValueSeen(3)
        loop.setFormatStateToPrint(lambda x: f'currently at: {x}')
        timeStart = srss.getNowAsMillisTime()
        numbersSeen = []
        evensSeen = []
        oddsSeen = []
        for number in loop:
            numbersSeen.append(number)
            if number % 2 == 0:
                evensSeen.append(number)
                loop.flagDidNoMeaningfulWork()
            else:
                oddsSeen.append(number)
        
        timeTaken = srss.getNowAsMillisTime() - timeStart
        timeTakenInSeconds = timeTaken / 1000
        assert numbersSeen == list(range(3, 100))
        assert evensSeen == list(range(4, 100, 2))
        assert oddsSeen == list(range(3, 100, 2))
        assert abs(timeTakenInSeconds - 2 * ((100-3)/20)) < 5


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
    
    def testWithFilters(self, fixtureFileTree):
        files.makeDirs(fixtureFileTree + '/node_modules')
        files.writeAll(fixtureFileTree + '/node_modules/a.txt', 'a')
        iter = SrssFileIterator(fixtureFileTree, 
            fnFilterDirs=lambda path: not path.replace('\\', '/').endswith('foobar/a/foobar'), excludeNodeModules=True)
        expected = ['/foobar/a/baz/aa.txt', '/foobar/a/baz/bb.txt', '/foobar/a/baz/foobar/cc.txt', 
                       '/foobar/a/baz/zz.txt', '/foobar/a/r1.txt', '/foobar/foobar/cc.txt', 
                       '/foobar/r2.txt', '/r3.txt']
        assert fileInfoListToList(fixtureFileTree, iter) == expected
        

        iter = SrssFileIterator(fixtureFileTree,
            fnFilterDirs=lambda path: not path.replace('\\', '/').endswith('foobar/a/baz'), excludeNodeModules=False)
        expected = ['/foobar/a/foobar/a.txt', '/foobar/a/foobar/b.txt', '/foobar/a/foobar/c/c0.txt', 
                       '/foobar/a/foobar/c/c1.txt', '/foobar/a/r1.txt', '/foobar/foobar/cc.txt', 
                       '/foobar/r2.txt', '/node_modules/a.txt', '/r3.txt']
        assert fileInfoListToList(fixtureFileTree, iter) == expected

    def testPassIterParams(self, fixtureFileTree):
        files.writeAll(fixtureFileTree + '/foobar/a/foobar/a.mp3', 'a')
        files.writeAll(fixtureFileTree + '/foobar/a/baz/b.mp3', 'a')
        iter = SrssFileIterator(fixtureFileTree, allowedExts=['mp3'])
        got = fileInfoListToList(fixtureFileTree, iter)
        assert got == ['/foobar/a/baz/b.mp3', '/foobar/a/foobar/a.mp3']

    def testIncludeTheseFiles(self, fixtureFileTree):
        files.writeAll(fixtureFileTree + '/foobar/a/foobar/a.mp3', 'a')
        files.writeAll(fixtureFileTree + '/foobar/a/baz/b.mp3', 'a')
        iter = SrssFileIterator(fixtureFileTree, fnIncludeTheseFiles=lambda s: s.endswith('.mp3'))
        got = fileInfoListToList(fixtureFileTree, iter)
        assert got == ['/foobar/a/baz/b.mp3', '/foobar/a/foobar/a.mp3']
    
    def testMultipleRoots(self, fixtureFileTree):
        root1 = fixtureFileTree + '/foobar/a/foobar'
        root2 = fixtureFileTree + '/foobar/a/baz/foobar'
        iter = SrssFileIterator([root1, root2])
        got = fileInfoListToList(fixtureFileTree, iter)
        assert got == ['/foobar/a/baz/foobar/cc.txt', '/foobar/a/foobar/a.txt', '/foobar/a/foobar/b.txt', 
                       '/foobar/a/foobar/c/c0.txt', '/foobar/a/foobar/c/c1.txt']

    def testNeedsAbsPaths(self):
        with pytest.raises(AssertionError, match='relative paths'):
            _instance = SrssFileIterator('./directory')

        with pytest.raises(AssertionError, match='relative paths'):
            _instance = SrssFileIterator('..')

class TestCleanupTempFiles:
    def testCleanupTempFilesOnClose(self, fixtureDir):
        files.writeAll(f'{fixtureDir}/a.txt', 'aaa')
        files.writeAll(f'{fixtureDir}/b.txt', 'bbb')
        files.writeAll(f'{fixtureDir}/c.txt', 'ccc')
        with srss.CleanupTempFilesOnClose() as cleanup:
            # clean up a newly created file
            files.writeAll(f'{fixtureDir}/new.txt', 'new')
            cleanup.registerTempFile(f'{fixtureDir}/new.txt')
            assert files.exists(f'{fixtureDir}/new.txt')

            # clean up a previously made file
            cleanup.registerTempFile(f'{fixtureDir}/a.txt')
            files.exists(f'{fixtureDir}/a.txt')

            # should silently skip non-existant files
            cleanup.registerTempFile(f'{fixtureDir}/not-exist.txt')
            assert not files.exists(f'{fixtureDir}/not-exist.txt')
        
        # check they were deleted
        assert not files.exists(f'{fixtureDir}/new.txt')
        assert not files.exists(f'{fixtureDir}/a.txt')
        assert not files.exists(f'{fixtureDir}/not-exist.txt')
        assert files.exists(f'{fixtureDir}/b.txt')
        assert files.exists(f'{fixtureDir}/c.txt')

    def testCleanupTempFilesOnException(self, fixtureDir):
        files.writeAll(f'{fixtureDir}/a.txt', 'aaa')
        files.writeAll(f'{fixtureDir}/b.txt', 'bbb')
        files.writeAll(f'{fixtureDir}/c.txt', 'ccc')
        def fn():
            with srss.CleanupTempFilesOnClose() as cleanup:
                cleanup.registerTempFile(f'{fixtureDir}/b.txt')
                raise RuntimeError("cause exception")

        # should delete b but leave behind the other file(s)
        assertException(fn, RuntimeError, "cause exception")
        assert files.exists(f'{fixtureDir}/a.txt')
        assert not files.exists(f'{fixtureDir}/b.txt')
        assert files.exists(f'{fixtureDir}/c.txt')

class TestCleanupEmptyDirs:
    def testBasic(self, fixtureFileTree):
        files.delete(fixtureFileTree + '/foobar/a/foobar/c/c0.txt')
        files.delete(fixtureFileTree + '/foobar/a/foobar/c/c1.txt')
        files.delete(fixtureFileTree + '/foobar/a/baz/foobar/cc.txt')
        removeEmptyDirs(fixtureFileTree)
        got = fileInfoListToList(fixtureFileTree, files.recurseDirs)
        assert got ==['', '/foobar', '/foobar/a', '/foobar/a/baz', 
                      '/foobar/a/foobar', '/foobar/foobar']
    
    def testRemoveRootToo(self, fixtureFileTree):
        files.delete(fixtureFileTree + '/foobar/a/foobar/c/c0.txt')
        files.delete(fixtureFileTree + '/foobar/a/foobar/c/c1.txt')
        files.delete(fixtureFileTree + '/foobar/a/baz/foobar/cc.txt')
        
        removeEmptyDirs(fixtureFileTree + '/foobar/a/baz/foobar', 
                           removeRootIfEmpty=False)
        got = fileInfoListToList(fixtureFileTree, files.recurseDirs)
        assert got == ['', '/foobar', '/foobar/a', '/foobar/a/baz', 
                       '/foobar/a/baz/foobar', '/foobar/a/foobar', 
                       '/foobar/a/foobar/c', '/foobar/foobar']
        
        removeEmptyDirs(fixtureFileTree + '/foobar/a/baz/foobar', 
                           removeRootIfEmpty=True)
        got = fileInfoListToList(fixtureFileTree, files.recurseDirs)
        assert got == ['', '/foobar', '/foobar/a', '/foobar/a/baz', 
                       '/foobar/a/foobar', '/foobar/a/foobar/c', 
                       '/foobar/foobar']

    def testShouldIgnoreIfMissingOrIsFile(self, fixtureFileTree):
        assert files.exists(fixtureFileTree + '/foobar/a/foobar/c/c0.txt')
        removeEmptyDirs(fixtureFileTree + '/foobar/a/foobar/c/c0.txt')
        assert files.exists(fixtureFileTree + '/foobar/a/foobar/c/c0.txt')

        assert not files.exists(fixtureFileTree + '/notexist')
        removeEmptyDirs(fixtureFileTree + '/notexist')
        assert not files.exists(fixtureFileTree + '/notexist')

