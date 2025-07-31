
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsevenlib import *

class TestJslikeConcat:
    def testBasic(self):
        a = [1, 2]
        b = [3, 4]
        c = jslike.concat(a, b)
        assert c == [1, 2, 3, 4]
    
    def testTypicalCases(self):
        assert jslike.concat([1, 2], []) == [1, 2]
        assert jslike.concat([], [1, 2]) == [1, 2]
        assert jslike.concat([1, 2], [3, 4]) == [1, 2, 3, 4]
        assert jslike.concat([1, 2], [3, 4, 5]) == [1, 2, 3, 4, 5]

    def testEdgeCases(self):
        assert jslike.concat([], []) == []
        assert jslike.concat([1], []) == [1]
        assert jslike.concat([], [1]) == [1]
    
    def testDoesNotModifyInputs(self):
        a = [1]
        b = [2]
        assert jslike.concat(a, b) == [1, 2]
        assert a == [1]
        assert b == [2]


class TestEveryAndSome:
    def testBasicEvery(self):
        fn = lambda x: x > 0
        assert jslike.every([], fn) is True
        assert jslike.every([1], fn) is True
        assert jslike.every([1, 2], fn) is True
        assert jslike.every([1, 2, 0], fn) is False
        assert jslike.every([1, 0, 2], fn) is False
        assert jslike.every([0], fn) is False
        assert jslike.every([0, 0], fn) is False
        assert jslike.every([0, 0, 1], fn) is False
    
    def testBasicSome(self):
        fn = lambda x: x > 0
        assert jslike.some([], fn) is False
        assert jslike.some([1], fn) is True
        assert jslike.some([1, 2], fn) is True
        assert jslike.some([1, 2, 0], fn) is True
        assert jslike.some([1, 0, 2], fn) is True
        assert jslike.some([0], fn) is False
        assert jslike.some([0, 0], fn) is False
        assert jslike.some([0, 0, 1], fn) is True

class TestFilter:
    def testBasic(self):
        fn = lambda x: x > 0
        assert jslike.filter([], fn) == []
        assert jslike.filter([1], fn) == [1]
        assert jslike.filter([1, 2], fn) == [1, 2]
        assert jslike.filter([1, 2, 0], fn) == [1, 2]
        assert jslike.filter([1, 0, 2], fn) == [1, 2]
        assert jslike.filter([0], fn) == []
        assert jslike.filter([0, 0], fn) == []
        assert jslike.filter([0, 0, 1], fn) == [1]

class TestFindAndFindIndex:
    def testBasicFind(self):
        fn = lambda x: x > 0
        assert jslike.find([], fn) is None
        assert jslike.find([1], fn) == 1
        assert jslike.find([1, 2], fn) == 1
        assert jslike.find([1, 2, 0], fn) == 1
        assert jslike.find([1, 0, 2], fn) == 1
        assert jslike.find([2, 0, 1], fn) == 2
        assert jslike.find([0], fn) is None
        assert jslike.find([0, 0], fn) is None
        assert jslike.find([0, 0, 1], fn) == 1
    
    def testBasicFindIndex(self):
        fn = lambda x: x > 0
        assert jslike.findIndex([], fn) == -1
        assert jslike.findIndex([1], fn) == 0
        assert jslike.findIndex([1, 2], fn) == 0
        assert jslike.findIndex([1, 2, 0], fn) == 0
        assert jslike.findIndex([1, 0, 2], fn) == 0
        assert jslike.findIndex([2, 0, 1], fn) == 0
        assert jslike.findIndex([0], fn) == -1
        assert jslike.findIndex([0, 0], fn) == -1
        assert jslike.findIndex([0, 0, 1], fn) == 2
    
    def testIndexOf(self):
        assert jslike.indexOf([], 1) == -1
        assert jslike.indexOf([1], 1) == 0
        assert jslike.indexOf([1, 2], 1) == 0
        assert jslike.indexOf([1, 2, 0], 1) == 0
        assert jslike.indexOf([1, 0, 2], 1) == 0
        assert jslike.indexOf([1, 0, 1], 1) == 0
        assert jslike.indexOf([2, 0, 1], 1) == 2
        assert jslike.indexOf([0], 1) == -1
        assert jslike.indexOf([0, 0], 1) == -1
        assert jslike.indexOf([0, 0, 1], 1) == 2
    
    def testLastIndexOf(self):
        assert jslike.lastIndexOf([], 1) == -1
        assert jslike.lastIndexOf([1], 1) == 0
        assert jslike.lastIndexOf([1, 2], 1) == 0
        assert jslike.lastIndexOf([1, 2, 0], 1) == 0
        assert jslike.lastIndexOf([1, 0, 2], 1) == 0
        assert jslike.lastIndexOf([1, 0, 1], 1) == 2
        assert jslike.lastIndexOf([2, 0, 1], 1) == 2
        assert jslike.lastIndexOf([0], 1) == -1
        assert jslike.lastIndexOf([0, 0], 1) == -1
        assert jslike.lastIndexOf([0, 0, 1], 1) == 2


class TestMap:
    def testBasic(self):
        fn = lambda x: x + 10
        assert jslike.map([], fn) == []
        assert jslike.map([1], fn) == [11]
        assert jslike.map([1, 2], fn) == [11, 12]

    def test_mapShouldReturnList(self):
        fn = lambda x: x + 10
        input = [1, 2]
        out = jslike.map(input, fn)
        assert isinstance(out, list)
        assert input == [1, 2]
        assert out == [11, 12]

class TestTimes:
    def testBasic(self):
        fn = lambda: 1
        assert jslike.times(0, fn) == []
        assert jslike.times(1, fn) == [1]
        assert jslike.times(5, fn) == [1, 1, 1, 1, 1]

    def testWithContext(self):
        class Counter:
            counter = 0

        context = Counter()
        def incCounter():
            context.counter += 1
            return context.counter
        assert jslike.times(0, incCounter) == []
        assert jslike.times(1, incCounter) == [1]
        assert jslike.times(5, incCounter) == [2, 3, 4, 5, 6]


class TestReduce:
    def testBasic(self):
        fn = lambda initialVal, head: initialVal + head
        assert jslike.reduce([2], fn) == 2
        assert jslike.reduce([2, 3], fn) == 5
        assert jslike.reduce([2, 3, 4], fn) == 9
        with pytest.raises(Exception):
            jslike.reduce([], fn)
        
    def test_reduceWithInitialVal(self):
        fn = lambda initialVal, head: initialVal + head
        assert jslike.reduce([], fn, 1) == 1
        assert jslike.reduce([2], fn, 1) == 3
        assert jslike.reduce([2, 3], fn, 1) == 6
        assert jslike.reduce([2, 3, 4], fn, 1) == 10

    def test_reduceMultiply(self):
        fn = lambda initialVal, head: initialVal * head
        assert jslike.reduce([2], fn) == 2
        assert jslike.reduce([2, 3], fn) == 6
        assert jslike.reduce([2, 3, 4], fn) == 24
        with pytest.raises(Exception):
            jslike.reduce([], fn)

    def test_reduceMultiplyWithInitialVal(self):
        fn = lambda initialVal, head: initialVal * head
        assert jslike.reduce([2], fn, 2) == 4
        assert jslike.reduce([2, 3], fn, 2) == 12
        assert jslike.reduce([2, 3, 4], fn, 2) == 48
        assert jslike.reduce([], fn, 2) == 2

    def test_reduceMultiplyWithZero(self):
        fn = lambda initialVal, head: initialVal * head
        assert jslike.reduce([2], fn, 0) == 0
        assert jslike.reduce([2, 3], fn, 0) == 0
        assert jslike.reduce([2, 3, 4], fn, 0) == 0
        assert jslike.reduce([], fn, 0) == 0

    def test_reduceRecorded(self):
        def fn(initialVal, head):
            return 'initialVal=%s;head=%s;' % \
                (initialVal, head)
        assert jslike.reduce([2], fn) == 2
        assert jslike.reduce([2, 3], fn) == 'initialVal=2;head=3;'
        assert jslike.reduce([2, 3, 4], fn) == 'initialVal=initialVal=2;head=3;;head=4;'
        with pytest.raises(Exception):
            jslike.reduce([], fn)


class TestSplice:
    def testBasic(self):
        assert 'abef' == jslike.splice('abcdef', 2, 2, '')
        assert 'ab1ef' == jslike.splice('abcdef', 2, 2, '1')
        assert 'ab12ef' == jslike.splice('abcdef', 2, 2, '12')
        assert 'ab123ef' == jslike.splice('abcdef', 2, 2, '123')
        assert 'ab123def' == jslike.splice('abcdef', 2, 1, '123')
        assert 'ab123cdef' == jslike.splice('abcdef', 2, 0, '123')


