
#~ from ..src import shinerainsoftsevencommon_shinerainsoftseven
#~ import sys
#~ sys.path.append('../src')
from shinerainsoftsevencommon import *

class TestConcat:
    def test_typicalCases(self):
        assert jslike.concat([1, 2], []) == [1, 2]
        assert jslike.concat([], [1, 2]) == [1, 2]
        assert jslike.concat([1, 2], [3, 4]) == [1, 2, 3, 4]
        assert jslike.concat([1, 2], [3, 4, 5]) == [1, 2, 3, 4, 5]
        
    def test_edgeCases(self):
        assert jslike.concat([], []) == []
        assert jslike.concat([1], []) == [1]
        assert jslike.concat([], [1]) == [1]
        
    def test_doesNotModify(self):
        a = [1]
        b = [2]
        assert jslike.concat(a, b) == [1, 2]
        assert a == [1]
        assert b == [2]
        
