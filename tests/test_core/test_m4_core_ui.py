
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

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


#~ def interactiveTests():

