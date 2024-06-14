
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsoftsevenutil.standard import *


class TestCoreUIInteractive:
    def testSrssLooper(self):
        pass
    
    def testSrssLooperInteractive(self):
        alert('you should now see a loop from 3 to 100 that pauses every 20')
        loop = srss.SrssLooper(list(range(100)))
        loop.showPercentageEstimates()
        loop.addPauses(10, seconds=2)
        loop.waitUntilValueSeen(3)
        timeStart = srss.getNowAsMillisTime()
        for number in loop:
            if number % 2 == 0:
                print('skipping even number', number)
                loop.flagDidNoMeaningfulWork()
            else:
                print('found an odd number', number)
        
        timeTaken = srss.getNowAsMillisTime() - timeStart
        timeTaken = timeTaken / 1000 # milliseconds to seconds
        assert abs(timeTaken - 2 * ((100-3)/20)) < 5


#~ def interactiveTests():

