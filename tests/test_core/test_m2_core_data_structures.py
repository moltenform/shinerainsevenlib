

# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
import os
import enum
from os.path import join
from collections import OrderedDict

class TestAppendList:
    # add/append
    def test_appendToListInDictOrStartNewListNoRepeats(self):
        d = {}
        appendToListInDictOrStartNewList(d, 'a', 'a')
        appendToListInDictOrStartNewList(d, 'b', 'b')
        appendToListInDictOrStartNewList(d, 'c', 'c')
        assert d == dict(a=['a'], b=['b'], c=['c'])

    def test_appendToListInDictOrStartNewListManyRepeats(self):
        d = {}
        appendToListInDictOrStartNewList(d, 'a', 'a')
        appendToListInDictOrStartNewList(d, 'a', 'a')
        appendToListInDictOrStartNewList(d, 'b', 'b')
        appendToListInDictOrStartNewList(d, 'b', 'b')
        appendToListInDictOrStartNewList(d, 'c', 'c')
        appendToListInDictOrStartNewList(d, 'c', 'c')
        assert d == dict(a=['a', 'a'], b=['b', 'b'], c=['c', 'c'])

    def test_appendToListInDictOrStartNewListAlternateRepeats(self):
        d = {}
        appendToListInDictOrStartNewList(d, 'a', 'a')
        appendToListInDictOrStartNewList(d, 'b', 'b')
        appendToListInDictOrStartNewList(d, 'c', 'c')
        appendToListInDictOrStartNewList(d, 'a', 'a')
        appendToListInDictOrStartNewList(d, 'b', 'b')
        assert d == dict(a=['a', 'a'], b=['b', 'b'], c=['c'])

class TestBucket:
    def test_bucket(self):
        a = Bucket()
        a.f1 = 'abc'
        assert a.f1 == 'abc'
        a.f1 = 'def'
        assert a.f1 == 'def'
        a.f2 = 'abc'
        assert a.f1 == 'def'
        assert a.f2 == 'abc'

    def test_bucketCtor(self):
        a = Bucket(f1='start1', f2='start2')
        a.f3 = 'start3'
        assert a.f1 == 'start1'
        assert a.f2 == 'start2'
        assert a.f3 == 'start3'

    def test_bucketRepr(self):
        a = Bucket()
        a.f1 = 'abc'
        a.f2 = 'def'
        assert 'f1=abc\n\n\nf2=def' == repr(a)

class enumExampleInt(enum.IntEnum):
    first = enum.auto()
    second = enum.auto()
    third = enum.auto()

class enumExampleStr(enum.StrEnum):
    first = enum.auto()
    second = enum.auto()
    third = enum.auto()


class TestSimpleEnum:
    def test_values(self):
        assert enumExampleInt.first == 1
        assert enumExampleInt.third == 3
        assert enumExampleStr.first == 'first'
        assert enumExampleStr.third == 'third'
        
        # accessing invalid one should throw
        with pytest.raises(AttributeError):
            enumExampleInt.invalid
        with pytest.raises(AttributeError):
            enumExampleStr.invalid

    def test_shouldNotBeAbleToModify(self):
        with pytest.raises(AttributeError):
            enumExampleInt.first = 2
        with pytest.raises(AttributeError):
            enumExampleInt.missing = 2
        with pytest.raises(AttributeError):
            enumExampleStr.first = "other"
        with pytest.raises(AttributeError):
            enumExampleStr.missing = "other"

class TestDataStructures:
    # takeBatch
    def test_takeBatchNonLazy(self):
        assert [[1, 2, 3], [4, 5, 6], [7]] == takeBatch([1, 2, 3, 4, 5, 6, 7], 3)
        assert [[1, 2, 3], [4, 5, 6]] == takeBatch([1, 2, 3, 4, 5, 6], 3)
        assert [[1, 2, 3], [4, 5]] == takeBatch([1, 2, 3, 4, 5], 3)
        assert [[1, 2], [3, 4], [5]] == takeBatch([1, 2, 3, 4, 5], 2)

    def test_takeBatchWithCallbackOddNumber(self):
        log = []

        def callback(batch, log=log):
            log.append(list(batch))
        with TakeBatch(2, callback) as obj:
            obj.append(1)
            obj.append(2)
            obj.append(3)
        assert [[1, 2], [3]] == log

    def test_takeBatchWithCallbackEvenNumber(self):
        log = []

        def callback(batch, log=log):
            log.append(list(batch))
        with TakeBatch(2, callback) as obj:
            obj.append(1)
            obj.append(2)
            obj.append(3)
            obj.append(4)
        assert [[1, 2], [3, 4]] == log

    def test_takeBatchWithCallbackSmallNumber(self):
        log = []

        def callback(batch, log=log):
            log.append(list(batch))
        with TakeBatch(3, callback) as obj:
            obj.append(1)
        assert [[1]] == log

    def test_takeBatchWithCallbackDoNotCallOnException(self):
        log = []

        def callback(batch, log=log):
            log.append(list(batch))

        # normally, leaving scope of TakeBatch makes final call, but don't if leaving because of exception
        with pytest.raises(IOError):
            with TakeBatch(2, callback) as obj:
                obj.append(1)
                obj.append(2)
                obj.append(3)
                raise IOError()
        assert [[1, 2]] == log


class TestRecentlyUsed:
    def test_recentlyUsedList_MaxNotExceeded(self):
        mruTest = RecentlyUsedList(maxSize=5)
        mruTest.add('abc')
        mruTest.add('def')
        mruTest.add('ghi')
        assert ['ghi', 'def', 'abc'] == mruTest.getList()

    def test_recentlyUsedList_RedundantEntryMovedToTop(self):
        mruTest = RecentlyUsedList(maxSize=5)
        mruTest.add('aaa')
        mruTest.add('bbb')
        mruTest.add('ccc')
        mruTest.add('bbb')
        assert ['bbb', 'ccc', 'aaa'] == mruTest.getList()

    def test_recentlyUsedList_MaxSizePreventsGrowth(self):
        mruTest = RecentlyUsedList(maxSize=2)
        mruTest.add('aaa')
        mruTest.add('bbb')
        mruTest.add('ccc')
        assert ['ccc', 'bbb'] == mruTest.getList()

    def test_recentlyUsedList_MaxSizePreventsMoreGrowth(self):
        mruTest = RecentlyUsedList(maxSize=2)
        mruTest.add('aaa')
        mruTest.add('bbb')
        mruTest.add('ccc')
        mruTest.add('ddd')
        assert ['ddd', 'ccc'] == mruTest.getList()

class TestMemoize:
    def test_memoizeCountNumberOfCalls_RepeatedCall(self):
        countCalls = Bucket(count=0)

        @BoundedMemoize
        def addTwoNumbers(a, b, countCalls=countCalls):
            countCalls.count += 1
            return a + b
        assert 20 == addTwoNumbers(10, 10)
        assert 1 == countCalls.count
        assert 20 == addTwoNumbers(10, 10)
        assert 40 == addTwoNumbers(20, 20)
        assert 2 == countCalls.count

    def test_memoizeCountNumberOfCalls_InterleavedCall(self):
        countCalls = Bucket(count=0)

        @BoundedMemoize
        def addTwoNumbers(a, b, countCalls=countCalls):
            countCalls.count += 1
            return a + b
        assert 20 == addTwoNumbers(10, 10)
        assert 1 == countCalls.count
        assert 40 == addTwoNumbers(20, 20)
        assert 20 == addTwoNumbers(10, 10)
        assert 2 == countCalls.count

