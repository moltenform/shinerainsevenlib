


# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import pytest
import time
import os
import re
import datetime
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from common import fixture_dir

class TestAsserts:
    # assertTrue
    def test_assertTrueExpectsTrue(self):
        assertTrue(True)
        assertTrue(1)
        assertTrue('string')

    def test_assertTrueFailsIfFalse(self):
        with pytest.raises(AssertionError):
            assertTrue(False)

    def test_assertTrueFailsIfFalseWithMessage(self):
        with pytest.raises(AssertionError) as exc:
            assertTrue(False, 'custom msg')
        exc.match('custom msg')

    # assertEq
    def test_assertEq(self):
        assertEq(True, True)
        assertEq(1, 1)
        assertEq((1, 2, 3), (1, 2, 3))

    def test_assertEqFailsIfNotEqual(self):
        with pytest.raises(AssertionError):
            assertEq(1, 2, 'msg here')

    # assertEqArray
    def test_assertEqArray(self):
        assertEqArray([], [])
        assertEqArray([1], [1])
        assertEqArray([1, 2, 3], [1, 2, 3])
        assertEqArray('1|2|3', ['1', '2', '3'])

    def test_assertEqArrayFailsIfNotEqual(self):
        with pytest.raises(AssertionError):
            assertEqArray([1, 2, 3], [1, 2, 4])

        with pytest.raises(AssertionError):
            assertEqArray([1, 2, 3], [1, 2, 3, 4])

        with pytest.raises(AssertionError):
            assertEqArray('1|2|3', ['1', '2', '4'])

    # test assertFloatEq
    def test_assertFloatEqEqual(self):
        assertFloatEq(0.0, 0)
        assertFloatEq(0.1234, 0.1234)
        assertFloatEq(-0.1234, -0.1234)

    def test_assertFloatEqEqualWithinPrecision(self):
        assertFloatEq(0.123456788, 0.123456789)

    def test_assertFloatNotEqualGreater(self):
        with pytest.raises(AssertionError):
            assertFloatEq(0.4, 0.1234)

    def test_assertFloatNotEqualSmaller(self):
        with pytest.raises(AssertionError):
            assertFloatEq(0.1234, 0.4)

    def test_assertFloatNotEqualBitGreater(self):
        with pytest.raises(AssertionError):
            assertFloatEq(-0.123457, -0.123456)

    def test_assertFloatNotEqualBitSmaller(self):
        with pytest.raises(AssertionError):
            assertFloatEq(-0.123457, -0.123458)

    def test_assertFloatNotEqualNegative(self):
        with pytest.raises(AssertionError):
            assertFloatEq(0.1234, -0.1234)
    
    # testCatch
    def test_runAndCatchException_Raises(self):
        def fn():
            raise Exception('abc')

        result = runAndCatchException(fn)
        assertEq(None, result.result)
        assertTrue(isinstance(result.err, Exception))

    def test_runAndCatchException_NotRaises(self):
        def fn():
            return 'abc'

        result = runAndCatchException(fn)
        assertEq('abc', result.result)
        assertEq(None, result.err)

class TestCustomAsserts:
    def exampleRaiseValueErr(self):
        raise ValueError('msg')

    # assertException
    def test_assertExceptionExpectsAnyException(self):
        assertException(self.exampleRaiseValueErr, None)

    def test_assertExceptionExpectsSpecificException(self):
        assertException(self.exampleRaiseValueErr, ValueError)

    def test_assertExceptionExpectsSpecificExceptionAndMessage(self):
        assertException(self.exampleRaiseValueErr, ValueError, 'msg')

    def test_assertExceptionExpectsSpecificExceptionAndMessage(self):
        r = re.compile('.*msg.*')
        assertException(self.exampleRaiseValueErr, ValueError, r)

    def test_assertExceptionFailsIfNoExceptionThrown(self):
        with pytest.raises(AssertionError) as exc:
            assertException(lambda: 1, None)
        exc.match('did not throw')

    def test_assertExceptionFailsIfWrongExceptionThrown(self):
        with pytest.raises(AssertionError) as exc:
            assertException(self.exampleRaiseValueErr, ValueError, 'notmsg')
        exc.match('exception string check failed')

    def test_assertExceptionFailsIfWrongExceptionThrownRe(self):
        r = re.compile('.*notmsg.*')
        with pytest.raises(AssertionError) as exc:
            assertException(self.exampleRaiseValueErr, ValueError, r)
        exc.match('exception string check failed')

class TestTiming:
    def test_renderTime(self):
        t = getNowAsMillisTime()
        s = renderMillisTime(t)
        assert len(s) > 16
        s = renderMillisTimeStandard(t)
        assert len(s) > 16

    def test_simpleTimer(self):
        tmer = SimpleTimer()
        time.sleep(2)
        got = tmer.check()
        assert got >= 1.8 and got <= 2.2
    
class TestStringHelpers:
    # truncateWithEllipsis
    def test_truncateWithEllipsisEmptyString(self):
        assert '' == truncateWithEllipsis('', 2)

    def test_truncateWithEllipsisStringLength1(self):
        assert 'a' == truncateWithEllipsis('a', 2)

    def test_truncateWithEllipsisStringLength2(self):
        assert 'ab' == truncateWithEllipsis('ab', 2)

    def test_truncateWithEllipsisStringLength3(self):
        assert 'ab' == truncateWithEllipsis('abc', 2)

    def test_truncateWithEllipsisStringLength4(self):
        assert 'ab' == truncateWithEllipsis('abcd', 2)

    def test_truncateWithEllipsisEmptyStringTo4(self):
        assert '' == truncateWithEllipsis('', 4)

    def test_truncateWithEllipsisStringTo4Length1(self):
        assert 'a' == truncateWithEllipsis('a', 4)

    def test_truncateWithEllipsisStringTo4Length2(self):
        assert 'ab' == truncateWithEllipsis('ab', 4)

    def test_truncateWithEllipsisStringTo4Length4(self):
        assert 'abcd' == truncateWithEllipsis('abcd', 4)

    def test_truncateWithEllipsisStringLength5TruncatedTo4(self):
        assert 'a...' == truncateWithEllipsis('abcde', 4)

    def test_truncateWithEllipsisStringLength6TruncatedTo4(self):
        assert 'a...' == truncateWithEllipsis('abcdef', 4)

    # formatSize
    def test_formatSizeTb(self):
        assert '3.00TB' == formatSize(3 * 1024 * 1024 * 1024 * 1024)

    def test_formatSizeGb(self):
        assert '3.00GB' == formatSize(3 * 1024 * 1024 * 1024)

    def test_formatSizeGbAndFewBytes(self):
        assert '3.00GB' == formatSize(3 * 1024 * 1024 * 1024 + 123)

    def test_formatSizeGbDecimal(self):
        assert '3.12GB' == formatSize(3 * 1024 * 1024 * 1024 + 123 * 1024 * 1024)

    def test_formatSizeGbDecimalRound(self):
        assert '3.17GB' == formatSize(3 * 1024 * 1024 * 1024 + 169 * 1024 * 1024)

    def test_formatSizeMb(self):
        assert '2.31MB' == formatSize(2 * 1024 * 1024 + 315 * 1024)

    def test_formatSizeKb(self):
        assert '1.77KB' == formatSize(1 * 1024 + 789)

    def test_formatSizeB(self):
        assert '1000b' == formatSize(1000)

    def test_formatSize1000B(self):
        assert '678b' == formatSize(678)

    def test_formatSizeZeroB(self):
        assert '0b' == formatSize(0)

    def test_formatSizeCornerCases(self):
        assert 'NaN' == formatSize(None)
        assert 'NaN' == formatSize('')

class TestToValidFilename:
    def test_toValidFilenameEmpty(self):
        assert '' == toValidFilename('')

    def test_toValidFilenameAFew(self):
        assert 'a-b c' == toValidFilename('a:b\nc')

    def test_toValidFilenameWindowsNewline(self):
        assert 'a c' == toValidFilename('a\r\nc')

    def test_toValidFilenameWithSeps(self):
        assert 'a-b-c' == toValidFilename('a\\b/c')

    def test_toValidFilenameAndKeepSeps(self):
        if os.path.sep == '/':
            test = 'a\n?b\\c/d\\e/f'
            expect = 'a b-c/d-e/f'
        else:
            test = 'a\n?b\\c/d\\e/f'
            expect = 'a b\\c-d\\e-f'

        assert expect == toValidFilename(test, dirsepOk=True)

    def test_toValidFilenameAndKeepSepsWithSpaces(self):
        if os.path.sep == '/':
            test = 'a\n?b\\ c/ d\\ e/ f'
            expect = 'a b, c/ d, e/ f'
        else:
            test = 'a\n?b\\ c/ d\\ e/ f'
            expect = 'a b\\ c, d\\ e, f'

        assert expect == toValidFilename(test, dirsepOk=True)

    def test_toValidFilenameLengthOK(self):
        s = 'a/'.replace('/', os.path.sep) + 'a' * 42 + '.jpg'
        assert s == toValidFilename(s, dirsepOk=True, maxLen=50)
        s = 'a/'.replace('/', os.path.sep) + 'a' * 43 + '.jpg'
        assert s == toValidFilename(s, dirsepOk=True, maxLen=50)
        s = 'a/'.replace('/', os.path.sep) + 'a' * 44 + '.jpg'
        assert s == toValidFilename(s, dirsepOk=True, maxLen=50)

    def test_toValidFilenameLengthTooLong(self):
        s = 'a/'.replace('/', os.path.sep) + 'a' * 45 + '.jpg'
        expected = 'a/'.replace('/', os.path.sep) + 'a' * 44 + '.jpg'
        assert expected == toValidFilename(s, dirsepOk=True, maxLen=50)
        s = 'a/'.replace('/', os.path.sep) + 'a' * 46 + '.jpg'
        expected = 'a/'.replace('/', os.path.sep) + 'a' * 44 + '.jpg'
        assert expected == toValidFilename(s, dirsepOk=True, maxLen=50)
        s = 'a/'.replace('/', os.path.sep) + 'a' * 47 + '.jpg'
        expected = 'a/'.replace('/', os.path.sep) + 'a' * 44 + '.jpg'
        assert expected == toValidFilename(s, dirsepOk=True, maxLen=50)

    def test_toValidFilenameDirLengthTooLong(self):
        s = 'a' * 44 + '/a.jpg'.replace('/', os.path.sep)
        assert s == toValidFilename(s, dirsepOk=True, maxLen=50)
        s = 'a' * 45 + '/a.jpg'.replace('/', os.path.sep)
        expected = 'a' * 45 + '/.jpg'.replace('/', os.path.sep)
        assert expected == toValidFilename(s, dirsepOk=True, maxLen=50)
        s = 'a' * 46 + '/a.jpg'.replace('/', os.path.sep)
        with pytest.raises(AssertionError):
            toValidFilename(s, dirsepOk=True, maxLen=50)
        s = 'a' * 47 + '/a.jpg'.replace('/', os.path.sep)
        with pytest.raises(AssertionError):
            toValidFilename(s, dirsepOk=True, maxLen=50)


def dateParserAvailable():
    "Checks if the dateparser module is available."
    try:
        import dateparser
        return True
    except ImportError:
        return False

if not dateParserAvailable:
    print("We will skip dateparsing tests because the module dateparser is not found.")



@pytest.mark.skipif('not dateParserAvailable()')
class TestDateParsing:
    def test_spanish_dates_should_not_parsed(self):
        uu = EnglishDateParserWrapper()
        assert uu.parse(u'Martes 21 de Octubre de 2014') is None

    def test_spanish_dates_will_parse_if_we_hack_it_and_give_it_a_different_parser(self):
        import dateparser
        uu = EnglishDateParserWrapper()
        uu.p = dateparser.date.DateDataParser()
        parsed = uu.parse(u'Martes 21 de Octubre de 2014')
        assert 2014 == parsed.year

    def test_incomplete_dates_should_not_parsed(self):
        uu = EnglishDateParserWrapper()
        assert uu.parse(u'December 2015') is None

    def test_incomplete_dates_will_parse_if_we_hack_it_and_give_it_a_different_parser(self):
        import dateparser
        uuu = EnglishDateParserWrapper()
        uuu.p = dateparser.date.DateDataParser()
        parsed = uuu.parse(u'December 2015')
        assert 2015 == parsed.year

    def test_dates_can_get_this(self):
        uu = EnglishDateParserWrapper()
        got = uu.parse('30 Jan 2018')
        assert 30 == got.day
        assert 1 == got.month
        assert 2018 == got.year

    def test_and_confirm_MDY(self):
        uu = EnglishDateParserWrapper()
        got = uu.parse('4/5/2016')
        assert 5 == got.day
        assert 4 == got.month
        assert 2016 == got.year

        got = uu.parse('18 feb 12')
        assert 18 == got.day
        assert 2 == got.month
        assert 2012 == got.year

        got = uu.parse('August 24 2018')
        assert 24 == got.day
        assert 8 == got.month
        assert 2018 == got.year

        got = uu.parse('2016-04-11 21:07:47.763957')
        assert 11 == got.day
        assert 4 == got.month
        assert 2016 == got.year

        got = uu.parse('Mar 31, 2011 17:41:41 GMT')
        assert 31 == got.day
        assert 3 == got.month
        assert 2011 == got.year

    def test_twitter_api_format_we_needed_to_tweak_it_a_bit(self):
        uu = EnglishDateParserWrapper()
        assert "Wed Nov 07 04:01:10 2018 +0000" == uu.fromFullWithTimezone("Wed Nov 07 04:01:10 +0000 2018")
        got = uu.parse(uu.fromFullWithTimezone("Wed Nov 07 04:01:10 +0000 2018"))
        assert 7 == got.day
        assert 11 == got.month
        assert 2018 == got.year

        assert "Wed Nov 07 04:01:10 2018" == uu.fromFullWithTimezone("Wed Nov 07 04:01:10 2018")
        got = uu.parse(uu.fromFullWithTimezone("Wed Nov 07 04:01:10 2018"))
        assert 7 == got.day
        assert 11 == got.month
        assert 2018 == got.year

    def test_ensure_month_day_year(self):
        # 1362456244 is 3(month)/5(day)/2013
        uu = EnglishDateParserWrapper()
        test1 = uu.getDaysBeforeInMilliseconds('3/5/2013 4:04:04 GMT', 0)
        assert 1362456244000 == test1
        test2 = uu.getDaysBeforeInMilliseconds('3/5/2013 4:04:04 GMT', 1)
        assert 1362456244000 - 86400000 == test2
        test3 = uu.getDaysBeforeInMilliseconds('3/5/2013 4:04:04 GMT', 100)
        assert 1362456244000 - 100 * 86400000 == test3
    
    def test_getDaysBefore(self):
        dt = datetime.datetime(2013, 3, 5, 4, 4, 4)
        uu = EnglishDateParserWrapper()
        got = uu.getDaysBefore(dt, 5)
        assert got == datetime.datetime(2013, 2, 28, 4, 4, 4)
        

    def test_render_time(self):
        sampleMillisTime = 1676603866779
        assert '02/16/2023 07:17:46 PM' == renderMillisTime(sampleMillisTime)
        assert '2023-02-16 07:17:46' == renderMillisTimeStandard(sampleMillisTime)

    def test_toUnixMillis(self):
        uu = EnglishDateParserWrapper()
        got = uu.toUnixMilliseconds('3/5/2013 4:04:04 GMT')
        assert got == 1362456244000
        

class TestRegexWrappers:
    # replaceMustExist
    def test_replaceMustExist(self):
        assert 'abc DEF ghi' == replaceMustExist('abc def ghi', 'def', 'DEF')
        assert 'ABC def ABC' == replaceMustExist('abc def abc', 'abc', 'ABC')
        with pytest.raises(AssertionError):
            replaceMustExist('abc def abc', 'abcd', 'ABC')

    # replaceWholeWord
    def test_replaceWholeWord(self):
        assert 'w,n,w other,wantother,w.other' == reReplaceWholeWord('want,n,want other,wantother,want.other', 'want', 'w')

    def test_replaceWholeWordWithPunctation(self):
        assert 'w,n,w other,w??|tother,w.other' == reReplaceWholeWord('w??|t,n,w??|t other,w??|tother,w??|t.other', 'w??|t', 'w')

    def test_replaceWholeWordWithCasing(self):
        assert 'and A fad pineapple A da' == reReplaceWholeWord('and a fad pineapple a da', 'a', 'A')

    def test_replaceAll(self):
        assert 'aBc B aBc' == reReplace('abc b abc', 'b', 'B')

    # searchWholeWord
    def test_searchWholeWordFound(self):
        assert 11 == reSearchWholeWord('wantother, want other', 'want').span()[0]

    def test_searchWholeWordWithPunctationFound(self):
        assert 11 == reSearchWholeWord('w()wother, w()w other', 'w()w').span()[0]

    def test_searchWholeWordNotFound(self):
        assert reSearchWholeWord('otherwantother', 'want') is None

    def test_searchWholeWordWithPunctationNotFound(self):
        assert reSearchWholeWord('otherw()wother', 'w()w') is None

class TestStripHtml:
    # stripHtmlTags
    def test_stripHtmlTagsBasic(self):
        assert 'a b c' == stripHtmlTags('a b c')
        assert '' == stripHtmlTags('')
        assert '' == stripHtmlTags('<a b c>')
        assert '1 2' == stripHtmlTags('1<a b c>2')

    def test_stripHtmlTagsNested(self):
        assert '1 c?2' == stripHtmlTags('1<a <b> c>2')
        assert '1 2' == stripHtmlTags('1<a <b c>2')
        assert '1 c?2' == stripHtmlTags('1<a b> c>2')
        assert '1 c?2' == stripHtmlTags('1<a <b> c>2')

    def test_stripHtmlTagsUnclosed(self):
        assert 'open?' == stripHtmlTags('open>')
        assert 'open? abc' == stripHtmlTags('open> abc')
        assert '?open abc' == stripHtmlTags('>open abc')
        assert '' == stripHtmlTags('<close')
        assert 'abc' == stripHtmlTags('abc<close')
        assert 'abc close?' == stripHtmlTags('abc close<')

    def test_stripHtmlTagsManyTagsRepeatedSpace(self):
        assert 'a b c d e', stripHtmlTags('a b c<abc> d </abc>e')
        assert 'a b c d e', stripHtmlTags('a b c<abc>d</abc>e')
        assert 'a b c d e', stripHtmlTags('a b c<abc><b>d</abc>e')


class TestReplaceAscii:
    def testReplaceNonAsciiWith(self):
        assert replaceNonAsciiWith('aéaé', '<>') == 'a<>a<>'
        assert replaceNonAsciiWith('aeae', '<>') == 'aeae'
        assert containsNonAscii('aéaé')
        assert not containsNonAscii('aeae')


class TestObjectHelpers:
    def testGetObjAttributes(self):
        class BasicBucket:
            def __init__(self, **kwargs):
                for key, val in kwargs.items():
                    object.__setattr__(self, key, val)

        test = BasicBucket(a=1, b=2)
        assert sorted(getObjAttributes(test)) == ['a', 'b']

        test = BasicBucket(a=1, c=3)
        test._hidden = 4
        assert sorted(getObjAttributes(test)) == ['a', 'c']

    def testGetClassName(self):
        test = Bucket(a=1)
        assert getClassNameFromInstance(test) == 'Bucket'

class TestCompatFunctions:
    def testStartswith(self):
        assert startsWith('abc', 'ab')
        assert not startsWith('abc', 'ac')
        assert startsWith(b'abc', b'ab')
        assert not startsWith(b'abc', b'ac')
        assert startsWith(b'abc', 'ab')
        assert not startsWith(b'abc', 'ac')
        assert startsWith('abc', b'ab')
        assert not startsWith('abc', b'ac')

    def testEndwsith(self):
        assert endsWith('abc', 'bc')
        assert not endsWith('abc', 'bd')
        assert endsWith(b'abc', b'bc')
        assert not endsWith(b'abc', b'bd')
        assert endsWith(b'abc', 'bc')
        assert not endsWith(b'abc', 'bd')
        assert endsWith('abc', b'bc')
        assert not endsWith('abc', b'bd')

    
    def testBytesHelpers(self):
        assert list(iterBytes(b'abc')) == [b'a', b'b', b'c']
        assert bytesToString(b'abc') == 'abc'
        assert asBytes('abc', encoding='utf-8') == b'abc'


