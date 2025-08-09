

# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
import os
import enum
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from common import fixtureDir
from collections import OrderedDict

@pytest.mark.skipif('not isPy3OrNewer')
class TestPersistedDict:
    def test_noPersistYet(self, fixtureDir):
        # won't persist since 5 things haven't been written
        path = join(fixtureDir, 'test.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=5)
        obj.set('key1', 'val1')
        assert 1 == len(obj.data)
        objRead = PersistedDict(path)
        assert 0 == len(objRead.data)

    def test_willPersist(self, fixtureDir):
        path = join(fixtureDir, 'test.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=5)
        for i in range(6):
            obj.set('key%d' % i, 'val%d' % i)
        assertEq(6, len(obj.data))
        objRead = PersistedDict(path)
        assertEq(5, len(objRead.data))
        for i in range(5):
            assert 'val%d' % i == objRead.data['key%d' % i]

    def test_canLoadEmpty(self, fixtureDir):
        path = join(fixtureDir, 'test.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=5)
        obj.persist()
        assertTrue(files.isFile(path))
        objRead = PersistedDict(path, warnIfCreatingNew=True)
        assert 0 == len(objRead.data)

    def test_canWriteUnicode(self, fixtureDir):
        path = join(fixtureDir, u'test\u1101.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=1)
        obj.set('key\u1101', '\u1101val')
        objRead = PersistedDict(path, warnIfCreatingNew=True)
        assert 1 == len(objRead.data)
        assert '\u1101val' == objRead.data['key\u1101']

    def test_canWriteDataTypes(self, fixtureDir):
        path = join(fixtureDir, u'test.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=1)
        obj.set('testInt', 123)
        obj.set('testString', 'abc')
        obj.set('testBool', True)
        obj.set('testList', [12, 34, 56])
        obj.set('testFloat', 1.2345)
        objRead = PersistedDict(path, warnIfCreatingNew=True)
        assert 123 == objRead.data['testInt']
        assert 'abc' == objRead.data['testString']
        assert True is objRead.data['testBool']
        assert [12, 34, 56] == objRead.data['testList']
        assertFloatEq(1.2345, objRead.data['testFloat'])

    def test_canWriteDataTypesAsKeys(self, fixtureDir):
        path = join(fixtureDir, u'test.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=1)
        obj.set(123, 'testInt')
        obj.set('abc', 'testString')
        obj.set(True, 'testBool')
        objRead = PersistedDict(path, warnIfCreatingNew=True)
        assert 'testInt' == objRead.data['123']
        assert 'testString' == objRead.data['abc']
        assert 'testBool' == objRead.data['true']

    def test_twoDeep(self, fixtureDir):
        path = join(fixtureDir, u'test.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=1)
        obj.set('rkey1', {})
        obj.set('rkey2', {})
        obj.setSubDict('rkey1', 'k1', 'v11')
        obj.setSubDict('rkey1', 'k2', 'v12')
        obj.setSubDict('rkey2', 'k1', 'v21')
        obj.setSubDict('rkey2', 'k2', 'v22')
        objRead = PersistedDict(path, warnIfCreatingNew=True)
        assert 2 == len(objRead.data)
        assert 'v11' == objRead.data['rkey1']['k1']
        assert 'v12' == objRead.data['rkey1']['k2']
        assert 'v21' == objRead.data['rkey2']['k1']
        assert 'v22' == objRead.data['rkey2']['k2']

    def test_threeDeep(self, fixtureDir):
        path = join(fixtureDir, u'test.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=1)
        obj.set('rrkey1', {})
        obj.set('rrkey2', {})
        obj.setSubDict('rrkey1', 'rkey1', {})
        obj.setSubDict('rrkey1', 'rkey2', {})
        obj.setSubDict('rrkey2', 'rkey1', {})
        obj.setSubDict('rrkey2', 'rkey2', {})
        obj.setSubSubDict('rrkey1', 'rkey2', 'rkeya', 'va')
        obj.setSubSubDict('rrkey2', 'rkey2', 'rkeyb', 'vb')
        objRead = PersistedDict(path, warnIfCreatingNew=True)
        assert 2 == len(objRead.data)
        assert {} == objRead.data['rrkey1']['rkey1']
        assert 'va' == objRead.data['rrkey1']['rkey2']['rkeya']
        assert {} == objRead.data['rrkey2']['rkey1']
        assert 'vb' == objRead.data['rrkey2']['rkey2']['rkeyb']

    def test_keepHandle(self, fixtureDir):
        path = join(fixtureDir, 'test.json')
        obj = PersistedDict(path, warnIfCreatingNew=False, persistEveryNWrites=1, keepHandle=True)
        for i in range(6):
            obj.set('key%d' % i, 'val%d' % i)
        assertEq(6, len(obj.data))
        obj.close()
        del obj
        objRead = PersistedDict(path)
        assertEq(6, len(objRead.data))
        for i in range(6):
            assert 'val%d' % i == objRead.data['key%d' % i]

class TestOrderedDict:
    def test_checkOrderedDictEqualitySame(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d1same = OrderedDict()
        d1same['a'] = 1
        d1same['b'] = 2
        assert d1 == d1
        assert d1 == d1same
        assert d1same == d1

    def test_checkOrderedDictEqualityDifferentOrder(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d2 = OrderedDict()
        d2['b'] = 2
        d2['a'] = 1
        assert d1 != d2

    def test_checkOrderedDictEqualityDifferentValues(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d2 = OrderedDict()
        d2['a'] = 1
        d2['b'] = 3
        assert d1 != d2

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

class TestParsePlus:
    def runBasicParse(self, s, pattern):
        parser = ParsePlus(pattern)
        return parser.match(s)

    def test_basic(self):
        found = self.runBasicParse(r'<p>abc</p>', r'<p>{content}</p>')
        assert found.content == 'abc'

    def test_mustMatchEntire1(self):
        found = self.runBasicParse(r'a<p>abc</p>', r'<p>{content}</p>')
        assert found is None

    def test_mustMatchEntire2(self):
        found = self.runBasicParse(r'<p>abc</p>a', r'<p>{content}</p>')
        assert found is None

    def test_mustMatchEntire3(self):
        found = self.runBasicParse(r'a<p>abc</p>a', r'<p>{content}</p>')
        assert found is None

    def test_mustMatchEntire4(self):
        found = self.runBasicParse(r'a\n<p>abc</p>', r'<p>{content}</p>')
        assert found is None

    def test_mustMatchEntire5(self):
        found = self.runBasicParse(r'<p>abc</p>\na', r'<p>{content}</p>')
        assert found is None

    def test_mustMatchEntire6(self):
        found = self.runBasicParse(r'a\n<p>abc</p>\na', r'<p>{content}</p>')
        assert found is None

    def test_shouldEscapeBackslash(self):
        found = self.runBasicParse(r'<p>abc</p>a\b', r'<p>{content}</p>a\b')
        assert found.content == 'abc'

    def test_shouldEscapeSymbols(self):
        found = self.runBasicParse(r'<p>abc</p>a??**)b', r'<p>{content}</p>a??**)b')
        assert found.content == 'abc'

    def test_shouldEscapeDotStar(self):
        found = self.runBasicParse(r'<p>abc</p>a.*?', r'<p>{content}</p>a.*?')
        assert found.content == 'abc'

    def test_ignoreDoubleBracketsOpen1(self):
        found = self.runBasicParse(r'{<p>abc</p>', r'{{<p>{content}</p>')
        assert found.content == 'abc'

    def test_ignoreDoubleBracketsOpen2(self):
        found = self.runBasicParse(r'<p>a{bc</p>', r'<p>{content}</p>')
        assert found.content == 'a{bc'

    def test_ignoreDoubleBracketsOpen3(self):
        found = self.runBasicParse(r'<p>abc</p>{', r'<p>{content}</p>{{')
        assert found.content == 'abc'

    def test_ignoreDoubleBracketsClose1(self):
        found = self.runBasicParse(r'}<p>abc</p>', r'}}<p>{content}</p>')
        assert found.content == 'abc'

    def test_ignoreDoubleBracketsClose2(self):
        found = self.runBasicParse(r'<p>a}bc</p>', r'<p>{content}</p>')
        assert found.content == 'a}bc'

    def test_ignoreDoubleBracketsClose3(self):
        found = self.runBasicParse(r'<p>abc</p>}', r'<p>{content}</p>}}')
        assert found.content == 'abc'

    def test_ignoreDoubleBracketsBoth1(self):
        found = self.runBasicParse(r'{}<p>abc</p>', r'{{}}<p>{content}</p>')
        assert found.content == 'abc'

    def test_ignoreDoubleBracketsBoth2(self):
        found = self.runBasicParse(r'<p>a{}bc</p>', r'<p>{content}</p>')
        assert found.content == 'a{}bc'

    def test_ignoreDoubleBracketsBoth3(self):
        found = self.runBasicParse(r'<p>abc</p>{}', r'<p>{content}</p>{{}}')
        assert found.content == 'abc'

    def test_ignoreDoubleBracketsBothInside1(self):
        found = self.runBasicParse(r'1{<p>abc</p>}1', r'1{{<p>{content}</p>}}1')
        assert found.content == 'abc'

    def test_ignoreDoubleBracketsBothInside2(self):
        found = self.runBasicParse(r'{<p>abc</p>}', r'{{<p>{content}</p>}}')
        assert found.content == 'abc'

    def test_emptyNameIsOk1(self):
        found = self.runBasicParse(r'456|ABC|123', r'{}|{main}|123')
        assert found.main == 'ABC'

    def test_emptyNamesIsOk2(self):
        found = self.runBasicParse(r'456|ABC|123', r'{}|{main}|{}')
        assert found.main == 'ABC'

    def test_nameMustBeAlphanum1(self):
        found = self.runBasicParse(r'456|ABC|123', r'{}|{bad name}|{}')
        assert found is None

    def test_nameMustBeAlphanum2(self):
        found = self.runBasicParse(r'456|ABC|123', r'{}|{bad)name}|{}')
        assert found is None

    def test_nameMustBeAlphanum3(self):
        found = self.runBasicParse(r'456|ABC|123', r'{}|{bad>name}|{}')
        assert found is None

    def test_nameCanHaveUnderscore(self):
        found = self.runBasicParse(r'456|ABC|123', r'{}|{good_name}|{}')
        assert found.good_name == 'ABC'

    def test_canNoteReturnEmpty(self):
        found = self.runBasicParse(r'456||123', r'{}|{fld}|{}')
        assert found is None

    def test_unnamedCanNotBeEmpty(self):
        found = self.runBasicParse(r'|a|', r'{}|{fld}|{}')
        assert found is None

    def test_hasNewline(self):
        found = self.runBasicParse('456|a\nb|123', r'{}|{fld}|{}')
        assert found.fld == 'a\nb'

    def test_hasWindowsNewline(self):
        found = self.runBasicParse('456|a\r\nb|123', r'{}|{fld}|{}')
        assert found.fld == 'a\r\nb'

    def test_hasNewlineRestricted(self):
        found = self.runBasicParse('456|a\nb|123', r'{}|{ss:NoNewlines}|{}')
        assert found is None

    def test_hasWindowsNewlineRestricted(self):
        found = self.runBasicParse('456|a\nb|123', r'{}|{ss:NoNewlines}|{}')
        assert found is None

    def test_hasSpaces(self):
        found = self.runBasicParse('456|a  b|123', r'{}|{ss}|{}')
        assert found.ss == 'a  b'

    def test_hasSpacesRestricted(self):
        found = self.runBasicParse('456|a  b|123', r'{}|{ss:NoSpaces}|{}')
        assert found is None

    def test_multipleFields2(self):
        found = self.runBasicParse(r'a|b', r'{c1}|{c2}')
        assert found.c1 == 'a'
        assert found.c2 == 'b'

    def test_multipleFields3(self):
        found = self.runBasicParse(r'a|b|c', r'{c1}|{c2}|{c3}')
        assert found.c1 == 'a'
        assert found.c2 == 'b'
        assert found.c3 == 'c'

    def test_multipleFields4(self):
        found = self.runBasicParse(r'a|b|c|d', r'{c1}|{c2}|{c3}|{c4}')
        assert found.c1 == 'a'
        assert found.c2 == 'b'
        assert found.c3 == 'c'
        assert found.c4 == 'd'

    def test_multipleFields5(self):
        found = self.runBasicParse(r'aa|bb|cc|dd', r'{c1}|{c2}|{c3}|{c4}')
        assert found.c1 == 'aa'
        assert found.c2 == 'bb'
        assert found.c3 == 'cc'
        assert found.c4 == 'dd'

    def test_multipleFieldsNotEnough(self):
        found = self.runBasicParse(r'a|b|c', r'{c1}|{c2}|{c3}|{c4}')
        assert found is None

    def test_multipleFieldsDemo(self):
        found = self.runBasicParse(r'<first>ff</first><second>ss</second>',
            r'<first>{c1}</first><second>{c2}</second>')
        assert found.c1 == 'ff'
        assert found.c2 == 'ss'

    def test_replaceTextFailsIfNotExists(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contentsFail = '<tag> Target</b> </tag>'
        files.writeAll(path, contentsFail)
        with pytest.raises(RuntimeError) as exc:
            ParsePlus('<b>{s}</b>').replaceFieldWithTextIntoFile(path,
                's', 'o')
        exc.match('pattern not found')

    def test_replaceTextFailsIfMultiple(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contentsFail = '<tag> <b>Target</b> <b>Other</b></tag>'
        files.writeAll(path, contentsFail)
        with pytest.raises(RuntimeError) as exc:
            ParsePlus('<b>{s}</b>').replaceFieldWithTextIntoFile(path,
                's', 'o', allowOnlyOnce=True)
        exc.match('only once')

    def test_replaceTextFailsIfMultipleOpen(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contentsFail = '<tag> <b>Target</b> <b>Other</tag></b>'
        files.writeAll(path, contentsFail)
        with pytest.raises(RuntimeError) as exc:
            ParsePlus('<b>{s}</b>').replaceFieldWithTextIntoFile(path,
                's', 'o', allowOnlyOnce=True)
        exc.match('only once')

    def test_replaceTextFailsIfMultipleClose(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contentsFail = '<tag> <b>Target</b> Othe<b>r</b></tag>'
        files.writeAll(path, contentsFail)
        with pytest.raises(RuntimeError) as exc:
            ParsePlus('<b>{s}</b>').replaceFieldWithTextIntoFile(path,
                's', 'o', allowOnlyOnce=True)
        exc.match('only once')

    def test_replaceTextAppendsIfNotExists(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contents = '<tag>Target</b> </tag>'
        files.writeAll(path, contents)
        ParsePlus('<b>{s}</b>').replaceFieldWithTextIntoFile(path,
            's', 'o', appendIfNotFound=':append:')

        newContents = files.readAll(path)
        assert newContents == '<tag>Target</b> </tag>:append:'

    def test_replaceTextSucceeds(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contents = '<tag> <b>Target</b> </tag>'
        files.writeAll(path, contents)
        ParsePlus('<b>{s}</b>').replaceFieldWithTextIntoFile(path,
            's', 'out', appendIfNotFound=':append:')
        newContents = files.readAll(path)
        assert newContents == '<tag> <b>out</b> </tag>'

    def test_replaceTextSucceedsManyClosers(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contents = '<tag> <b>Target</b> and</b></tag>'
        files.writeAll(path, contents)
        ParsePlus('<b>{s}</b>').replaceFieldWithTextIntoFile(path, 's', 'o')
        newContents = files.readAll(path)
        assert newContents == '<tag> <b>o</b> and</b></tag>'

    def test_replaceTextSucceedsManyBoth(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contents = '<tag> <b>Target</b> <b>other</b></tag>'
        files.writeAll(path, contents)
        ParsePlus('<b>{s}</b>').replaceFieldWithTextIntoFile(path, 's', 'o')
        newContents = files.readAll(path)
        assert newContents == '<tag> <b>o</b> <b>other</b></tag>'

    def test_replaceTextSucceedsLonger(self, fixtureDir):
        path = files.join(fixtureDir, 'testreplace.txt')
        contents = '<tag> <look>LongerTextIsHere</look> </tag>'
        files.writeAll(path, contents)
        ParsePlus('<look>{s}</look>').replaceFieldWithTextIntoFile(path,
            's', 'o')
        newContents = files.readAll(path)
        assert newContents == '<tag> <look>o</look> </tag>'

    def test_isCaseSensitive(self):
        found = ParsePlus('aa {s} bb').match('aA 123 bB')
        assert found is None

    def test_isNotCaseSensitive(self):
        found = ParsePlus('aa {s} bb', caseSensitive=False).match('aA 123 bB')
        assert found.s == '123'

    def parseCsvWithThreeFields(self, s):
        if not s.endswith('\n'):
            s += '\n'
        p = ParsePlus('1{f1:NoNewlines},{f2:NoNewlines},{f3:NoNewlines}\n',
            escapeSequences=['\\,', '\\\n'])
        return list(p.findAll(s))

    def test_findAllNotFound(self):
        found = self.parseCsvWithThreeFields('1a,b\n1c,d')
        assert len(found) == 0

    def test_findFalsePositive(self):
        # currently it detects it as one long string
        # I might consider finding a more elegant way around this sometime
        found = self.parseCsvWithThreeFields('1a,b,c|d,e,f|g,h,i')
        assert len(found) == 1

    def test_findFindFull(self):
        sInput = '1aa,bb,cc\n'
        found = self.parseCsvWithThreeFields(sInput)
        assert len(found) == 1
        assert found[0].f1 == 'aa'
        assert found[0].f2 == 'bb'
        assert found[0].f3 == 'cc'
        assert found[0].spans['f1'] == (1, 3)
        assert found[0].spans['f2'] == (4, 6)
        assert found[0].spans['f3'] == (7, 9)
        assert found[0].getTotalSpan() == (0, 10)
        assert sInput[1:3] == 'aa'
        assert sInput[4:6] == 'bb'
        assert sInput[7:9] == 'cc'
        assert sInput[0:10] == sInput

    def test_findFindOne(self):
        sInput = 'AAA1aa,bb,cc\nZZ'
        found = self.parseCsvWithThreeFields(sInput)
        assert len(found) == 1
        assert found[0].f1 == 'aa'
        assert found[0].f2 == 'bb'
        assert found[0].f3 == 'cc'
        assert found[0].spans['f1'] == (3 + 1, 3 + 3)
        assert found[0].spans['f2'] == (3 + 4, 3 + 6)
        assert found[0].spans['f3'] == (3 + 7, 3 + 9)
        assert found[0].getTotalSpan() == (3 + 0, 3 + 10)
        assert sInput[3 + 0: 3 + 10] == '1aa,bb,cc\n'

    def test_findFindThree(self):
        sInput = 'AAA1aa,bb,cc\n1ddd,eee,ff\n1gg,hh,iii\nZ'
        found = self.parseCsvWithThreeFields(sInput)
        assert len(found) == 3
        assert found[0].f1 == 'aa'
        assert found[0].f2 == 'bb'
        assert found[0].f3 == 'cc'
        assert found[0].spans['f1'] == (3 + 1, 3 + 3)
        assert found[0].spans['f2'] == (3 + 4, 3 + 6)
        assert found[0].spans['f3'] == (3 + 7, 3 + 9)
        assert found[0].getTotalSpan() == (3 + 0, 3 + 10)
        assert sInput[3 + 0: 3 + 10] == '1aa,bb,cc\n'
        assert found[1].f1 == 'ddd'
        assert found[1].f2 == 'eee'
        assert found[1].f3 == 'ff'
        assert found[1].spans['f1'] == (13 + 1, 13 + 4)
        assert found[1].spans['f2'] == (13 + 5, 13 + 8)
        assert found[1].spans['f3'] == (13 + 9, 13 + 11)
        assert found[1].getTotalSpan() == (13 + 0, 13 + 12)
        assert sInput[13 + 0: 13 + 12] == '1ddd,eee,ff\n'
        assert found[2].f1 == 'gg'
        assert found[2].f2 == 'hh'
        assert found[2].f3 == 'iii'
        assert found[2].spans['f1'] == (25 + 1, 25 + 3)
        assert found[2].spans['f2'] == (25 + 4, 25 + 6)
        assert found[2].spans['f3'] == (25 + 7, 25 + 10)
        assert found[2].getTotalSpan() == (25 + 0, 25 + 11)
        assert sInput[25 + 0: 25 + 11] == '1gg,hh,iii\n'

    def test_oneEscapeSequence(self):
        sInput = 'AAA1aa,bb,cc\n1dd\\\nd\\\n,eee,ff\nZ'
        found = self.parseCsvWithThreeFields(sInput)
        assert len(found) == 2
        assert found[0].f1 == 'aa'
        assert found[0].f2 == 'bb'
        assert found[0].f3 == 'cc'
        assert found[0].getTotalSpan() == (3, 13)
        assert found[1].f1 == 'dd\\\nd\\\n'
        assert found[1].f2 == 'eee'
        assert found[1].f3 == 'ff'
        assert found[1].getTotalSpan() == (13, 29)

    def test_twoEscapeSequences(self):
        sInput = 'AAA1aa,\\,,cc\n1\\,dd\\\nd\\\n,eee,ff\nZ'
        found = self.parseCsvWithThreeFields(sInput)
        assert len(found) == 2
        assert found[0].f1 == 'aa'
        assert found[0].f2 == '\\,'
        assert found[0].f3 == 'cc'
        assert found[0].getTotalSpan() == (3, 13)
        assert found[1].f1 == '\\,dd\\\nd\\\n'
        assert found[1].f2 == 'eee'
        assert found[1].f3 == 'ff'
        assert found[1].getTotalSpan() == (13, 31)

    def test_inputStringContainsRareChar1(self):
        with pytest.raises(RuntimeError) as exc:
            ParsePlus('{}', escapeSequences=['11', '22']).match('a\x01')
        exc.match('input string contains')

    def test_inputStringContainsRareChar2(self):
        with pytest.raises(RuntimeError) as exc:
            ParsePlus('{}', escapeSequences=['11', '22']).match('a\x02')
        exc.match('input string contains')

    def test_cannotYetSupportLotsOfSequences(self):
        with pytest.raises(ValueError) as exc:
            ParsePlus('{}', escapeSequences=['11', '22', '33', '44', '55', '66']).match('a')
        exc.match('a max of')

    def test_cannotYetSupportGetTotalSpanIfOpenBraces(self):
        with pytest.raises(RuntimeError) as exc:
            ParsePlus('{s}is {{').search('bis {').getTotalSpan()
        exc.match("don't yet support")

    def test_cannotYetSupportGetTotalSpanIfCloseBraces(self):
        with pytest.raises(RuntimeError) as exc:
            ParsePlus('{s}is }}').search('bis }').getTotalSpan()
        exc.match("don't yet support")


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
        assert 'f1=abc\nf2=def' == repr(a)

    def test_bucketGet(self):
        bck = Bucket(a=1, b=2)
        assert bck.get('a') == 1
        assert bck.get('notexist') == None
        assert bck.get('notexist', 999) == 999

    def test_bucketSet(self):
        bck = Bucket(a=1, b=2)
        bck.set('a', 100)
        bck.set('c', 300)
        assert bck.a == 100
        assert bck.b == 2
        assert bck.c == 300
    
    def test_bucketChildKeys(self):
        bck = Bucket(a=1, b=2)
        assert sorted(bck.getChildKeys()) == ['a', 'b']

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
        
        enumExampleInt.missing = 2
        with pytest.raises(AttributeError):
            enumExampleStr.first = "other"
        
        enumExampleStr.missing = "other"

class TestDataStructures:
    # takeBatch
    def test_takeBatchNonLazy(self):
        assert [[1, 2, 3], [4, 5, 6], [7]] == takeBatch([1, 2, 3, 4, 5, 6, 7], 3)
        assert [[1, 2, 3], [4, 5, 6]] == takeBatch([1, 2, 3, 4, 5, 6], 3)
        assert [[1, 2, 3], [4, 5]] == takeBatch([1, 2, 3, 4, 5], 3)
        assert  [[1, 2], [3, 4], [5]] == takeBatch([1, 2, 3, 4, 5], 2)

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
    
    def testListToNPArray(self):
        assert [[1, 2, 3, 4, 5, 6]] == list(listToNPieces([1, 2, 3, 4, 5, 6], 1))
        assert [[1, 3, 5], [2, 4, 6]] == list(listToNPieces([1, 2, 3, 4, 5, 6], 2))
        assert [[1, 4], [2, 5], [3, 6]]     == list(listToNPieces([1, 2, 3, 4, 5, 6], 3))
        assert [[1, 5], [2, 6], [3], [4]]    == list(listToNPieces([1, 2, 3, 4, 5, 6], 4))
        assert [[1, 6], [2], [3], [4], [5]] == list(listToNPieces([1, 2, 3, 4, 5, 6], 5))
        assert [[1], [2], [3], [4], [5], [6]] == list(listToNPieces([1, 2, 3, 4, 5, 6], 6))
        with pytest.raises(ValueError):
            list(listToNPieces([1, 2, 3, 4, 5, 6], 7))


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

    def test_memoizeSetLimit(self):
        countCalls = Bucket(count=0)

        @BoundedMemoize
        def addTwoNumbers(a, b, countCalls=countCalls):
            countCalls.count += 1
            return a + b

        addTwoNumbers.limit = 3
        assert 2 == addTwoNumbers(1, 1)
        assert 1 == countCalls.count
        assert 2 == addTwoNumbers(1, 1)
        assert 1 == countCalls.count
        assert 3 == addTwoNumbers(1, 2)
        assert 2 == countCalls.count
        assert 4 == addTwoNumbers(1, 3)
        assert 3 == countCalls.count
        assert 5 == addTwoNumbers(1, 4)
        assert 4 == countCalls.count
        assert 2 == addTwoNumbers(1, 1)
        assert 5 == countCalls.count

