
# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
import os
import random
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from common import fixture_dir


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
                # important: generate a new instance each time through loop,
                # since you can't re-use an iterator
                listInput = self.getIteratorOptions()[listInputKey]
                waitUntil = self.getWaitUntilOptions()[waitUntilKey]
                numbersSeen = []
                loop = srss.SrssLooper(listInput)
                loop.waitUntilValueSeen(waitUntil)
                for number in loop:
                    numbersSeen.append(number)
                
                if listInputKey == 'iter':
                    assert loop._len == -1
                elif listInputKey == 'lambdaUnreliableLen':
                    assert loop._len == 0
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


#~ class TestskipForwardUntilTrue:
    #~ def test_skipForwardUntilTrueArr(self):
        #~ arr = [0, 1, 2, 3, 4, 5]
        #~ results = [item for item in srss.SrssLooper.skipForwardUntilTrue(arr, lambda x: x == 3)]
        #~ assert results == [3, 4, 5]

    #~ def test_skipForwardUntilTrueIter(self):
        #~ def exampleIter():
            #~ for i in range(6):
                #~ yield i

        #~ results = [item for item in srss.SrssLooper.skipForwardUntilTrue(exampleIter(), lambda x: x == 3)]
        #~ assert results == [3, 4, 5]

    #~ def test_skipForwardUntilTrueArr_NeverSeen(self):
        #~ arr = [0, 1, 2, 3, 4, 5]
        #~ results = [item for item in srss.SrssLooper.skipForwardUntilTrue(arr, lambda x: x == 9)]
        #~ assert results == []

    #~ def test_skipForwardUntilTrueIter_NeverSeen(self):
        #~ def exampleIter():
            #~ for i in range(6):
                #~ yield i

        #~ results = [item for item in srss.SrssLooper.skipForwardUntilTrue(exampleIter(), lambda x: x == 9)]
        #~ assert results == []

#~ class TestTemporary:
    #~ def testSrssFileIteratorDirectoryFilter(self):
        #~ for SEP in ('/', '\\'):
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', ''))
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', 'abcd'))
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'ab{SEP}cd'))

            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node{SEP}_modules{SEP}b'))
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules{SEP}b'))
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules{SEP}'))
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules'))
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot{SEP}b'))
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot{SEP}'))
            #~ assert (not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot'))
            #~ assert (srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules{SEP}b'))
            #~ assert (srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules{SEP}'))
            #~ assert (srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules'))
    
    #~ def testCleanupTempFilesOnException(self, fixture_dir):
        #~ files.writeAll(f'{fixture_dir}/a.txt', 'aaa')
        #~ files.writeAll(f'{fixture_dir}/b.txt', 'bbb')
        #~ files.writeAll(f'{fixture_dir}/c.txt', 'ccc')
        #~ with srss.CleanupTempFilesOnException() as cleanup:
            #~ # clean up a newly created file
            #~ files.writeAll(f'{fixture_dir}/new.txt', 'new')
            #~ cleanup.registerTempFile(f'{fixture_dir}/new.txt')
            #~ assertTrue(files.exists(f'{fixture_dir}/new.txt'))

            #~ # clean up a previously made file
            #~ cleanup.registerTempFile(f'{fixture_dir}/a.txt')
            #~ assertTrue(files.exists(f'{fixture_dir}/a.txt'))

            #~ # should silently skip non-existant files
            #~ cleanup.registerTempFile(f'{fixture_dir}/not-exist.txt')
            #~ assertTrue(not files.exists(f'{fixture_dir}/not-exist.txt'))
        
        #~ # check they were deleted
        #~ assertTrue(not files.exists(f'{fixture_dir}/new.txt'))
        #~ assertTrue(not files.exists(f'{fixture_dir}/a.txt'))
        #~ assertTrue(not files.exists(f'{fixture_dir}/not-exist.txt'))

        #~ # should also cleanup if exceptions occur
        #~ def fn():
            #~ with srss.CleanupTempFilesOnException() as cleanup:
                #~ cleanup.registerTempFile(f'{fixture_dir}/b.txt')
                #~ raise RuntimeError("cause exception")

        #~ # should delete b but leave behind the other file(s)
        #~ assertException(fn, RuntimeError, "cause exception")
        #~ assertTrue(not files.exists(f'{fixture_dir}/b.txt'))
        #~ assertTrue(files.exists(f'{fixture_dir}/c.txt'))


