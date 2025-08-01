
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import os as _os
import sys as _sys
import traceback as _traceback
import pprint as _pprint
import re as _re
import time as _time
import datetime as _datetime
import math as _math

from .m0_text_io import *

# region assertions
# in other platforms, assertions might be configured to silently log,
# but these ones are loud, they always throw on failure.

def assertTrue(condition, *messageArgs):
    "Throw if condition is false"
    if not condition:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        raise AssertionError(msg)

def assertEq(expected, received, *messageArgs):
    "Throw if values are not equal"
    if expected != received:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        msg += '\nassertion failed, expected:\n'
        msg += _pprint.pformat(expected)
        msg += '\nbut got:\n'
        msg += _pprint.pformat(received)
        raise AssertionError(msg)

def assertWarn(condition, *messageArgs):
    "Show a message to user if condition is false"
    from . import m4_core_ui

    if not condition:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        m4_core_ui.warn(msg)

def assertWarnEq(expected, received, *messageArgs):
    "Show a message to user if values are not equal"
    from . import m4_core_ui

    if expected != received:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        msg += '\nexpected:\n'
        msg += _pprint.pformat(expected)
        msg += '\nbut got:\n'
        msg += _pprint.pformat(received)
        m4_core_ui.warn(msg)

def assertFloatEq(expected, received, *messageArgs):
    "Throw if values are not very close, use this if comparing floats"
    precision = 0.000001
    difference = _math.fabs(expected - received)
    if difference > precision:
        messageArgs = list(messageArgs) or []
        messageArgs.append(
            'expected %f, got %f, difference of %f' % (expected, received, difference)
        )
        assertTrue(False, *messageArgs)

def assertEqArray(expected, received):
    "Throw if arrays are not the same, with a convenient message"
    if isinstance(expected, str):
        expected = expected.split('|')

    assertEq(len(expected), len(received))
    for i, expectedVal in enumerate(expected):
        assertEq(repr(expectedVal), repr(received[i]))

def assertException(fn, excType, excTypeExpectedString=None, msg='', regexp=False):
    "Expect fn to throw"
    e = None
    try:
        fn()
    except:
        e = getCurrentException()

    assertTrue(e is not None, 'did not throw ' + msg)
    if excType:
        assertTrue(
            isinstance(e, excType),
            'exception type check failed ',
            msg,
            ' \ngot \n',
            _pprint.pformat(e),
            '\n not \n',
            _pprint.pformat(excType),
        )

    if excTypeExpectedString:
        if regexp:
            passed = _re.search(excTypeExpectedString, str(e))
        else:
            passed = excTypeExpectedString in str(e)
        assertTrue(
            passed, 'exception string check failed ' + msg + '\ngot exception string:\n' + str(e)
        )

def getTraceback(e):
    "Get _traceback from an exception"
    lines = _traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(lines)

def getCurrentException():
    "Get current exception"
    return _sys.exc_info()[1]

class ShineRainSevenLibError(RuntimeError):
    def __init__(self, *args):
        "You can pass in more than one string"
        combined = ' '.join(str(arg) for arg in args)
        super().__init__(combined)

# endregion

# region _time helpers

def renderMillisTime(millisTime):
    "`millistime` is number of milliseconds past epoch (unix _time * 1000)"
    t = millisTime / 1000.0
    return _time.strftime('%m/%d/%Y %I:%M:%S %p', _time.localtime(t))

def renderMillisTimeStandard(millisTime):
    "`millistime` is number of milliseconds past epoch (unix _time * 1000)"
    t = millisTime / 1000.0
    return _time.strftime('%Y-%m-%d %I:%M:%S', _time.localtime(t))

def getNowAsMillisTime():
    "Gets the number of milliseconds past epoch (unix _time * 1000)"
    t = _time.time()
    return int(t * 1000)

class SimpleTimer:
    "Simple timer to measure elapsed time"
    def __init__(self):
        self.startedAt = self.getTime()

    def getTime(self):
        import time, sys
        if sys.platform=='win32':
            return time.time()
        else:
            return time.clock()
    
    def check(self):
        return self.getTime() - self.startedAt
    
    def print(self):
        print('%04f second(s)' % self.check())

class EnglishDateParserWrapper:
    """More convenient than directly calling dateparser
    defaults to month-day-year
    restrict to English, less possibility of accidentally parsing a non-date string"""

    def __init__(self, dateOrder='MDY'):
        import dateparser

        settings = {'STRICT_PARSING': True}
        if dateOrder:
            settings['DATE_ORDER'] = dateOrder
        self.p = dateparser.date.DateDataParser(languages=['en'], settings=settings)

    def parse(self, s):
        return self.p.get_date_data(s)['date_obj']

    def fromFullWithTimezone(self, s):
        """Able to parse timestamps with a timezone
        compensate for +0000
        Wed Nov 07 04:01:10 +0000 2018"""
        pts = s.split(' ')
        newpts = []
        isTimeZone = ''
        for pt in pts:
            if pt.startswith('+'):
                assertEq('', isTimeZone)
                isTimeZone = ' ' + pt
            else:
                newpts.append(pt)

        return ' '.join(newpts) + isTimeZone

    def getDaysBefore(self, baseDate, nDaysBefore):
        "Subtract n days (simple), return datetime object"
        assertTrue(isinstance(nDaysBefore, int))
        diff = _datetime.timedelta(days=nDaysBefore)
        return baseDate - diff

    def getDaysBeforeInMilliseconds(self, sBaseDate, nDaysBefore):
        "Subtract n days (simple), return number of milliseconds past epoch"
        dObj = self.parse(sBaseDate)
        diff = _datetime.timedelta(days=nDaysBefore)
        dBefore = dObj - diff
        return int(dBefore.timestamp() * 1000)

    def toUnixMilliseconds(self, s):
        "Conviently go straight from string to the number of milliseconds past epoch"
        assertTrue(isPy3OrNewer, 'requires python 3 or newer')
        dt = self.parse(s)
        assertTrue(dt, 'not parse dt', s)
        return int(dt.timestamp() * 1000)

# endregion
# region string helpers

def replaceMustExist(haystack, needle, replace):
    "Replace needle in haystack, fail if needle not in haystack"
    assertTrue(needle in haystack, 'not found', needle)
    return haystack.replace(needle, replace)

def reSearchWholeWord(haystack, needle):
    "Search haystack for needle, return match object"
    reNeedle = '\\b' + _re.escape(needle) + '\\b'
    return _re.search(reNeedle, haystack)

def reReplaceWholeWord(haystack, needle, replace):
    "Replace needle in haystack with a 'whole word' style search"
    needle = '\\b' + _re.escape(needle) + '\\b'
    return _re.sub(needle, replace, haystack)

def reReplace(haystack, reNeedle, replace):
    "Replace needle in haystack"
    return _re.sub(reNeedle, replace, haystack)

# cliffnotes documentation of re module included here for convenience:
# re.search(pattern, string, flags=0)
#     look for at most one match starting anywhere
#
# re.match(pattern, string, flags=0)
#     look for match starting only at beginning of string
#
# re.findall(pattern, string, flags=0)
#     returns list of strings
#
# re.finditer(pattern, string, flags=0)
#     returns iterator of match objects
#
# flags include re.IGNORECASE, re.MULTILINE, re.DOTALL

def truncateWithEllipsis(s, maxLength):
    "Truncate a string with an ellipsis if it is too long"
    if len(s) <= maxLength:
        return s
    else:
        ellipsis = '...'
        if maxLength < len(ellipsis):
            return s[0:maxLength]
        else:
            return s[0 : maxLength - len(ellipsis)] + ellipsis

def formatSize(n):
    "Format a number of bytes into a human-readable string"
    if not isinstance(n, int):
        return 'NaN'
    elif n >= 1024 * 1024 * 1024 * 1024:
        return '%.2fTB' % (n / (1024.0 * 1024.0 * 1024.0 * 1024.0))
    elif n >= 1024 * 1024 * 1024:
        return '%.2fGB' % (n / (1024.0 * 1024.0 * 1024.0))
    elif n >= 1024 * 1024:
        return '%.2fMB' % (n / (1024.0 * 1024.0))
    elif n >= 1024:
        return '%.2fKB' % (n / (1024.0))
    else:
        return '%db' % n

# endregion

# region flow helpers

def runAndCatchException(fn):
    """Can be convenient to not need a try/except structure.
    use like golang,
    result, err = callFn()"""
    try:
        result = fn()
        return result, None
    except:
        return None, getCurrentException()

# endregion
# region ascii char helpers

def toValidFilename(pathOrig, dirsepOk=False, maxLen=None):
    "Convert path to a valid filename, especially on Windows where many characters are not allowed"
    path = pathOrig
    if dirsepOk:
        # sometimes we want to leave directory-separator characters in the string.
        if _os.path.sep == '/':
            path = path.replace('\\ ', ', ').replace('\\', '-')
        else:
            path = path.replace('/ ', ', ').replace('/', '-')
    else:
        path = path.replace('\\ ', ', ').replace('\\', '-')
        path = path.replace('/ ', ', ').replace('/', '-')

    result = (
        path.replace('\u2019', "'")
        .replace('?', '')
        .replace('!', '')
        .replace(': ', ', ')
        .replace(':', '-')
        .replace('| ', ', ')
        .replace('|', '-')
        .replace('*', '')
        .replace('"', "'")
        .replace('<', '[')
        .replace('>', ']')
        .replace('\r\n', ' ')
        .replace('\r', ' ')
        .replace('\n', ' ')
    )

    if maxLen and len(result) > maxLen:
        assertTrue(maxLen > 1)
        ext = _os.path.splitext(path)[1]
        beforeExt = path[0 : -len(ext)]
        while len(result) > maxLen:
            result = beforeExt + ext
            beforeExt = beforeExt[0:-1]

        # if it ate into the directory, though, throw an error
        assertTrue(_os.path.split(pathOrig)[0] == _os.path.split(result)[0])

    return result

def stripHtmlTags(s, removeRepeatedWhitespace=True):
    """Remove all html tags.
    see also: html.escape, html.unescape
    a (?:) is a non-capturing group"""

    reTags = _re.compile(r'<[^>]+(?:>|$)', _re.DOTALL)
    s = reTags.sub(' ', s)
    if removeRepeatedWhitespace:
        regNoDblSpace = _re.compile(r'\s+')
        s = regNoDblSpace.sub(' ', s)
        s = s.strip()

    # for malformed tags like "<a<" with no close, replace with ?
    s = s.replace('<', '?').replace('>', '?')
    return s

def replaceNonAsciiWith(s, replaceWith):
    """Replace non-ascii or control chars.
    printable is 32-126"""
    return _re.sub(r'[^\x20-\x7e]', replaceWith, s)

def containsNonAscii(s):
    """Does string contain non-ascii or control chars?
    aka does string contain chars outside 32-126"""
    withoutAscii = replaceNonAsciiWith(s, '')
    return len(s) != len(withoutAscii)

# endregion
# region object helpers and wrappers

def unused(_obj):
    "Use this to tell linters the variable is intentionally unused"

def getObjAttributes(obj):
    "Get properties on an object"
    return [att for att in dir(obj) if not att.startswith('_')]

def getClassNameFromInstance(obj):
    "Get class name from an instance"
    return obj.__class__.__name__

if _sys.version_info[0] >= 2:
    # inspired by mutagen/_compat.py
    def endsWith(a, b):
        "a endsWith that works with either str or bytes"
        if isinstance(a, str):
            if not isinstance(b, str):
                b = b.decode('ascii')
        else:
            if not isinstance(b, bytes):
                b = b.encode('ascii')
        return a.endswith(b)

    def startsWith(a, b):
        "a startsWith that works with either str or bytes"
        if isinstance(a, str):
            if not isinstance(b, str):
                b = b.decode('ascii')
        else:
            if not isinstance(b, bytes):
                b = b.encode('ascii')
        return a.startswith(b)

    def iterBytes(b):
        "iterate through the bytes"
        return (bytes([v]) for v in b)

    def bytesToString(b):
        "convert bytes to string"
        return b.decode('utf-8')

    def asBytes(s, encoding='ascii'):
        "convert string to bytes"
        return bytes(s, encoding)

    rinput = input
    ustr = str
    uchr = chr
    anystringtype = str
    bytetype = bytes
    xrange = range
    isPy3OrNewer = True
else:
    raise NotImplementedError('We no longer support python 2')

# endregion
