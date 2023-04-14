
from shinerainsoftsevencommon.infrastructure import gen_tests

exampleTypical = '''
# commentHeader1

import foo

# commentHeader2

import bar

# commentE

code1 = 1

# begin tests

code2 = 2

class TestE:
    def test_typicalCases(self):
        pass

def helperFnF():
    pass

class TestF:
    def test_typicalCases(self):
        pass

class HelperClassG():
    pass

class TestG:
    def test_typicalCases(self):
        pass

""" docstring H """

class TestH:
    def test_typicalCases(self):
        pass

\'\'\' docstring I \'\'\'

class TestI:
    def test_typicalCases(self):
        pass

# commentBeforeEnd

# end tests

# commentFooterAfterEnd

footerCodeHere = 1
'''

exampleEmptyHeader = r'''
class TestF:
    def test_typicalCases(self):
        pass

class TestG:
    def test_typicalCases(self):
        pass

extraCodeHere = 1
'''

exampleEmptyFooter = r'''
import foo

class TestF:
    def test_typicalCases(self):
        pass

class TestG:
    def test_typicalCases(self):
        pass
'''


exampleIndentedBlocksThatArentAClass = '''
import foo

def fn1():
    pass

class NotATest:
    pass

otherLines = 1

class TestIsATest:
    pass

'''

exampleEdgeCases = '''

@decorator
class TestWhitespace:
    def test_blankLineAfterThis(self):
        pass

    def test_lineWithSpacesAfterThis(self):
        pass
            
    def test_lineWithTabsAfterThis(self):
        pass
\t\t\t
    def stillPartOfThis(self):
        pass

nowLeavingTest = 1
'''



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
        


