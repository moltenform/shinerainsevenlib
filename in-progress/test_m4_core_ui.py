
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import pytest
from src.shinerainsevenlib.standard import *


class TestCoreUIInteractive:
    def testSrssLooperInteractive(self):
        alert('you should now see a loop from 3 to 100 that pauses every 20')
        loop = srss.SrssLooper(list(range(100)))
        loop.showPercentageEstimates()
        loop.addPauses(10, seconds=2)
        loop.waitUntilValueSeen(3)
        timeStart = srss.getNowAsMillisTime()
        numbersSeen = []
        for number in loop:
            numbersSeen.append(number)
            if number % 2 == 0:
                print('skipping even number', number)
                loop.flagDidNoMeaningfulWork()
            else:
                print('found an odd number', number)
        
        timeTaken = srss.getNowAsMillisTime() - timeStart
        timeTaken = timeTaken / 1000 # milliseconds to seconds
        assert numbersSeen == list(range(3, 100))
        assert abs(timeTaken - 2 * ((100-3)/20)) < 5


class TestskipForwardUntilTrue:
    def test_skipForwardUntilTrueArr(self):
        arr = [0, 1, 2, 3, 4, 5]
        results = [item for item in srss.SrssLooper.skipForwardUntilTrue(arr, lambda x: x == 3)]
        assert results == [3, 4, 5]

    def test_skipForwardUntilTrueIter(self):
        def exampleIter():
            for i in range(6):
                yield i

        results = [item for item in srss.SrssLooper.skipForwardUntilTrue(exampleIter(), lambda x: x == 3)]
        assert results == [3, 4, 5]

    def test_skipForwardUntilTrueArr_NeverSeen(self):
        arr = [0, 1, 2, 3, 4, 5]
        results = [item for item in srss.SrssLooper.skipForwardUntilTrue(arr, lambda x: x == 9)]
        assert results == []

    def test_skipForwardUntilTrueIter_NeverSeen(self):
        def exampleIter():
            for i in range(6):
                yield i

        results = [item for item in srss.SrssLooper.skipForwardUntilTrue(exampleIter(), lambda x: x == 9)]
        assert results == []

#~ def interactiveTests():

