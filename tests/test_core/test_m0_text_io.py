

# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import pytest
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from common import fixtureDir

class TestStrToListAndSet:
    def test_strToList(self):
        lst = strToList('''a\nbb\nc''')
        assert lst == ['a', 'bb', 'c']

        lst = strToList('''a\r\nbb\r\nc''')
        assert lst == ['a', 'bb', 'c']

        lst = strToList('''\r\na\r\n  bb  \r\nc\r\n''')
        assert lst == ['a', 'bb', 'c']

    def test_strToListWithComments(self):
        lst = strToList('''a\n#comment\nbb\nc''')
        assert lst == ['a', 'bb', 'c']

        lst = strToList('''a\r\n#comment\r\nbb\r\nc''')
        assert lst == ['a', 'bb', 'c']

        lst = strToList('''\r\n#comment\r\na\r\n  bb  \r\nc\r\n''')
        assert lst == ['a', 'bb', 'c']

    def test_strToSetWithComments(self):
        lst = strToSet('''a\n#comment\nbb\nc''')
        assert lst == set(['a', 'bb', 'c'])

        lst = strToSet('''a\r\n#comment\r\nbb\r\nc''')
        assert lst == set(['a', 'bb', 'c'])

        lst = strToSet('''\r\n#comment\r\na\r\n  bb  \r\nc\r\n''')
        assert lst == set(['a', 'bb', 'c'])

class TestEntryFromStrings:
    def testLongStr(self):
        fromLongStr = longStr("""
a string
that spans
multiple lines  """)
        assert fromLongStr == "a string that spans multiple lines"
        fromLongStr = longStr("with \nnewlines\r\n \n and   tabs\tand spaces")
        assert fromLongStr == "with newlines and tabs and spaces"
        fromLongStr = longStr("   \n")
        assert fromLongStr == ""

    def testEasyToEnterFilepathBasic(self, fixtureDir):
        existingFile = files.join(fixtureDir, 'a.txt')
        nonExistingFile = files.join(fixtureDir, 'b.txt')
        files.writeAll(existingFile, 'contents')

        # no whitespace
        assert easyToEnterFilepath(existingFile) == existingFile
        
        # whitespace before and after
        assert easyToEnterFilepath(f"""
                                   {existingFile}
        """) == existingFile
        
        # comments
        assert easyToEnterFilepath(f"""
        # ignored comment
        # {nonExistingFile}
                                   {existingFile}
        # other comment
        """) == existingFile

    def testEasyToEnterFilepathCornerCases(self, fixtureDir):
        existingFile = files.join(fixtureDir, 'a.txt')
        nonExistingFile = files.join(fixtureDir, 'b.txt')
        files.writeAll(existingFile, 'contents')

        # no content
        with pytest.raises(ValueError):
            easyToEnterFilepath('   ')
        
        # multiple content
        with pytest.raises(ValueError):
            easyToEnterFilepath(f"""
        {existingFile}          
        {existingFile}          
        """)
            
        # multiple content with comments
        with pytest.raises(ValueError):
            easyToEnterFilepath(f"""
        # comment
        {existingFile}          
        # comment 2
        {existingFile}          
        """)
        
        # path not found
        with pytest.raises(ValueError):
            easyToEnterFilepath(f"""
        {nonExistingFile}          
        """)
            
        # forgot to escape backslashes
        with pytest.raises(ValueError):
            easyToEnterFilepath(f"""
        C:\to\file         
        """)


class TestParseOrFallback:
    def testBasic(self):
        assert parseIntOrFallback('1') == 1
        assert parseIntOrFallback('1.23') is None
        assert parseIntOrFallback('123') == 123
        assert parseIntOrFallback('0') == 0
        assert parseIntOrFallback('-6') == -6
        assert parseIntOrFallback('n123') is None
        assert parseIntOrFallback('n123', 'fallback') == 'fallback'

    def testCornerCases(self):
        assert parseIntOrFallback('123abc') is None
        assert parseIntOrFallback('123   ') == 123
        assert parseIntOrFallback('') is None
        assert parseIntOrFallback(' ') is None
        assert parseIntOrFallback('ab') is None

    def testFloatBasic(self):
        assert parseFloatOrFallback('1') == pytest.approx(1)
        assert parseFloatOrFallback('1.23') == pytest.approx(1.23)
        assert parseFloatOrFallback('123') == pytest.approx(123)
        assert parseFloatOrFallback('0') == pytest.approx(0)
        assert parseFloatOrFallback('-6') == pytest.approx(-6)
        assert parseFloatOrFallback('n123') is None
        assert parseFloatOrFallback('n123', 'fallback') == 'fallback'

    def testFloatCornerCases(self):
        assert parseFloatOrFallback('123abc') is None
        assert parseFloatOrFallback('123   ') == pytest.approx(123)
        assert parseFloatOrFallback('12.3   ') == pytest.approx(12.3)
        assert parseFloatOrFallback('') is None
        assert parseFloatOrFallback(' ') is None
        assert parseFloatOrFallback('ab') is None


class TestClampNumber:
    def testBasic(self):
        assert clampNumber(1, 3, 6) == 3
        assert clampNumber(2, 3, 6) == 3
        assert clampNumber(3, 3, 6) == 3
        assert clampNumber(4, 3, 6) == 4
        assert clampNumber(5, 3, 6) == 5
        assert clampNumber(6, 3, 6) == 6
        assert clampNumber(7, 3, 6) == 6

    def testCornerCases(self):
        assert clampNumber(4, 3, 3) == 3
        assert clampNumber(3, 3, 3) == 3
        assert clampNumber(5, 3, 3) == 3
        with pytest.raises(ValueError):
            clampNumber(3, 3, 2)

class TestCompareAsSets:
    def testCompareTwoListsAsSets(self):
        l1 = 'a,b,c'.split(',')
        l2 = 'a,b,c'.split(',')
        result = compareTwoListsAsSets(l1, l2)
        assertEq([], result.addedItems)
        assertEq([], result.lostItems)

        l1 = 'a,b,c'.split(',')
        l2 = 'a,b,C'.split(',')
        result = compareTwoListsAsSets(l1, l2)
        assertEq(['C'], result.addedItems)
        assertEq(['c'], result.lostItems)

        l1 = 'a,b,c'.split(',')
        l2 = 'a,b,C,d'.split(',')
        result = compareTwoListsAsSets(l1, l2)
        assertEq(['C', 'd', ], result.addedItems)
        assertEq(['c'], result.lostItems)

        l1 = 'a,b,c'.split(',')
        l2 = 'b,C'.split(',')
        result = compareTwoListsAsSets(l1, l2)
        assertEq(['C'], result.addedItems)
        assertEq(['a', 'c', ], result.lostItems)

    def testCompareTwoListsAsSetsCornerCases(self):
        l1 = []
        l2 = []
        result = compareTwoListsAsSets(l1, l2)
        assertEq([], result.addedItems)
        assertEq([], result.lostItems)

        l1 = 'aX,bX,cX'.split(',')
        l2 = 'aY,bY,cY'.split(',')
        result = compareTwoListsAsSets(l1, l2, lambda x: x[0], lambda x: x[0])
        assertEq([], result.addedItems)
        assertEq([], result.lostItems)

        l1 = 'aX,bX,cX'.split(',')
        l2 = 'aY,BY,cY'.split(',')
        result = compareTwoListsAsSets(l1, l2, lambda x: x[0], lambda x: x[0])
        assertEq(['B'], result.addedItems)
        assertEq(['b'], result.lostItems)

        l1 = 'a,b,a'.split(',')
        l2 = 'a,b,c'.split(',')
        with pytest.raises(ValueError):
            compareTwoListsAsSets(l1, l2)
        
        l1 = 'a,b,c'.split(',')
        l2 = 'a,b,a'.split(',')
        with pytest.raises(ValueError):
            compareTwoListsAsSets(l1, l2)
        

class TestExpectEqualityAsSets:
    def testExpectEqualityTwoListsAsSets(self):
        try:
            setRedirectTraceCalls(lambda x: None)
            l1 = 'a,b,c'.split(',')
            l2 = 'a,b,c'.split(',')
            assert expectEqualityTwoListsAsSets(l1, l2) == True

            l1 = 'a,b,c'.split(',')
            l2 = 'a,b'.split(',')
            assert expectEqualityTwoListsAsSets(l1, l2) == False

            l1 = 'a,b,c'.split(',')
            l2 = 'a,b,c,d'.split(',')
            assert expectEqualityTwoListsAsSets(l1, l2) == False
        finally:
            setRedirectTraceCalls(None)


class TestThrowIfDuplicates:
    def testBasic(self):
        throwIfDuplicates([])
        throwIfDuplicates([1, 2, 3])
        with pytest.raises(ShineRainSevenLibError):
            throwIfDuplicates([1, 2, 3, 1])
        with pytest.raises(ShineRainSevenLibError):
            throwIfDuplicates([1, 2, 2, 3])
    
    def testWithConverter(self):
        throwIfDuplicates([])
        throwIfDuplicates(['a1', 'a2', 'a3'], lambda x: x[1])
        with pytest.raises(ShineRainSevenLibError):
            throwIfDuplicates(['a1', 'a2', 'a3', 'b1'], lambda x: x[1])
        with pytest.raises(ShineRainSevenLibError):
            throwIfDuplicates(['a1', 'b2', 'c2', 'a3'], lambda x: x[1])

class TestMergeDict:
    def testMergeDict(self):
        a = dict(a=1, b=2, c=3)
        b = dict(a=100, d=6)
        merged = mergeDict(a, b)
        assert merged == dict(a=100, b=2, c=3, d=6)
        
        a = dict(a=1, b=2, c=3)
        b = dict()
        merged = mergeDict(a, b)
        assert merged == dict(a=1, b=2, c=3)
    
    def testMergeIntoBucket(self):
        a = Bucket(a=1, b=2, c=3)
        b = dict(a=100, d=6)
        mergeDictIntoBucket(a, b, allowNewKeys=True)
        assert a.a == 100
        assert a.b == 2
        assert a.c == 3
        assert a.d == 6
        

        a = Bucket(a=1, b=2, c=3)
        b = dict()
        mergeDictIntoBucket(a, b, allowNewKeys=True)
        assert a.a == 1
        assert a.b == 2
        assert a.c == 3

    def testMergeDictCornerCases(self):
        a = Bucket(a=1, b=2, c=3)
        b = dict(b=20, c=30)
        mergeDictIntoBucket(a, b)
        assert a.a == 1
        assert a.b == 20
        assert a.c == 30

        with pytest.raises(RuntimeError):
            a = Bucket(a=1, b=2, c=3)
            b = dict(a=100, d=6)
            mergeDictIntoBucket(a, b)
    
    def test_compareDict(self):
        assert dict() == dict()
        assert dict(a=1, b=2) == dict(a=1, b=2)
        assert dict(b=2, a=1) == dict(a=1, b=2)
        assert dict(a=1, b=2) != dict(a=1, b=3)
        assert dict(a=1, b=2) != dict(a=1, aa=2)
        assert dict(a=1, b=2) != dict(a=1, b=2, c=3)
        assert dict(a=1, b=2) != dict(a=1)

    def test_mergedBasic(self):
        assert mergeDict(dict(), dict()) == dict()
        assert mergeDict(dict(a=1), dict()) == dict(a=1)
        assert mergeDict(dict(), dict(a=1)) == dict(a=1)
        assert mergeDict(dict(a=1), dict(a=2)) == dict(a=2)
        assert mergeDict(dict(a=2), dict(a=1)) == dict(a=1)
        assert mergeDict(dict(a=1), dict(a=2, b=3)) == dict(a=2, b=3)
        assert mergeDict(dict(a=2), dict(a=1, b=3)) == dict(a=1, b=3)
        assert mergeDict(dict(a=1, b=3), dict(a=1, b=3)) == dict(a=1, b=3)
        assert mergeDict(dict(a=1, b=3), dict(a=4, b=5)) == dict(a=4, b=5)
        assert mergeDict(dict(a=1, b=3), dict(a=1)) == dict(a=1, b=3)
        assert mergeDict(dict(a=1, b=3), dict(a=2)) == dict(a=2, b=3)
        assert mergeDict(dict(a=1, b=3), dict()) == dict(a=1, b=3)
        assert mergeDict(dict(a=1), dict(b=3)) == dict(a=1, b=3)

    def test_mergedShouldNotModify(self):
        a = dict(a=1, b=2, c=1)
        b = dict(a=3, b=2)
        out = mergeDict(a, b)
        assert a == dict(a=1, b=2, c=1)
        assert b == dict(a=3, b=2)
        assert out == dict(a=3, b=2, c=1)

class TestGetPrintable:
    def test_getPrintableEmpty(self):
        assert '' == getPrintable('')

    def test_getPrintableNormalAscii(self):
        assert 'normal ascii' == getPrintable('normal ascii')
    
    def test_getPrintableNormalUnicode(self):
        assert u'normal unicode' == getPrintable(u'normal unicode')
    
    def test_getPrintableBytes(self):
        assert 'abc' == getPrintable(b'abc')

    def test_getPrintableWithUniCharsIgnore(self):
        assert 'kuon' == getPrintable(u'\u1E31\u1E77\u1E53\u006E', okToIgnore=True)

    def test_getPrintableWithUniChars(self):
        assert 'k?u?o??n' == getPrintable(u'\u1E31\u1E77\u1E53\u006E')

    def test_getPrintableWithUniCharsSimple(self):
        assert 'de?f' == getPrintable(u'déf')

    def test_getPrintableWithUniCompositeSequence(self):
        assert 'k?u?o??n' == getPrintable(u'\u006B\u0301\u0075\u032D\u006F\u0304\u0301\u006E')
    
    def testRedirect(self):
        try:
            setRedirectTraceCalls(lambda x: captured.append(x))
            captured = []
            trace(u'\u1E31\u1E77\u1E53\u006E')
            assert 'k?u?o??n' == captured[0]
        finally:
            setRedirectTraceCalls(None)
        

    def testRedirectMultipleArgs(self):
        try:
            setRedirectTraceCalls(lambda x: captured.append(x))
            captured = []
            trace('abc', 12, True)
            assert 'abc 12 True' == captured[0]
        finally:
            setRedirectTraceCalls(None)
    
    def testRedirectPretty(self):
        try:
            setRedirectTraceCalls(lambda x: captured.append(x))
            captured = []
            tracep({'k': 'v'})
            assert "{'k': 'v'}" == captured[0]
        finally:
            setRedirectTraceCalls(None)

    def testRedirectPrettyUnicode(self):
        try:
            setRedirectTraceCalls(lambda x: captured.append(x))
            captured = []
            tracep({'k': u'\u1E31\u1E77\u1E53\u006E'})
            assert "{'k': 'k?u?o??n'}" == captured[0]
        finally:
            setRedirectTraceCalls(None)


