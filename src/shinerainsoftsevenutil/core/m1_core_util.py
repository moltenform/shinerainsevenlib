# shinerainsoftsevencommon
# Released under the LGPLv3 License

import os as _os
import sys as _sys
import traceback as _traceback
import pprint as _pprint
import re as _re
import time as _time


# region assertions
# in other platforms, assertions might be configured to silently log,
# but these ones here are loud. it's safe to assume they always throw on failure.

def assertTrue(condition, *messageArgs):
    "throw if condition is false"
    if not condition:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        raise AssertionError(msg)

def assertEq(expected, received, *messageArgs):
    "throw if values are not equal"
    if expected != received:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        msg += '\nassertion failed, expected:\n'
        msg += _pprint.pformat(expected)
        msg += '\nbut got:\n'
        msg += _pprint.pformat(received)
        raise AssertionError(msg)

def assertWarn(condition, *messageArgs):
    "show a message to user if condition is false"
    from . import m4_core_ui
    if not condition:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        m4_core_ui.warn(msg)

def assertWarnEq(expected, received, *messageArgs):
    "show a message to user if values are not equal"
    from . import m4_core_ui
    if expected != received:
        import _pprint
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        msg += '\nexpected:\n'
        msg += _pprint.pformat(expected)
        msg += '\nbut got:\n'
        msg += _pprint.pformat(received)
        m4_core_ui.warn(msg)

def assertFloatEq(expected, received, *messageArgs):
    "throw if values are not very close, use this if comparing floats"
    import math
    precision = 0.000001
    difference = math.fabs(expected - received)
    if difference > precision:
        messageArgs = list(messageArgs) or []
        messageArgs.append('expected %f, got %f, difference of %f' % (
            expected, received, difference))
        assertTrue(False, *messageArgs)

def assertEqArray(expected, received):
    "throw if arrays are not the same, with a convenient message"
    if isinstance(expected, str):
        expected = expected.split('|')

    assertEq(len(expected), len(received))
    for i in range(len(expected)):
        assertEq(repr(expected[i]), repr(received[i]))

def assertException(fn, excType, excTypeExpectedString=None, msg='', regexp=False):
    "expect fn to throw"
    e = None
    try:
        fn()
    except:
        e = getCurrentException()

    assertTrue(e is not None, 'did not throw ' + msg)
    if excType:
        assertTrue(isinstance(e, excType), 'exception type check failed ' + msg +
            ' \ngot \n' + _pprint.pformat(e) + '\n not \n' + _pprint.pformat(excType))
        
    if excTypeExpectedString:
        if regexp:
            passed = _re.search(excTypeExpectedString, str(e))
        else:
            passed = excTypeExpectedString in str(e)
        assertTrue(passed, 'exception string check failed ' + msg +
            '\ngot exception string:\n' + str(e))

def getTraceback(e):
    "get _traceback from an exception"
    lines = _traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(lines)

def getCurrentException():
    "get current exception"
    return _sys.exc_info()[1]

class ShineRainSoftSevenCommonError(RuntimeError):
    def __init__(self, *args):
        "you can pass in more than one string"
        combined = ' '.join((str(arg) for arg in args))
        super().__init__(combined)

# endregion
# region trace helpers

def getPrintable(s, okToIgnore=False):
    "from a-with-accent to plain a"
    import unicodedata
    if isinstance(s, bytes):
        return s.decode('ascii')
    if not isinstance(s, str):
        return str(s)

    s = unicodedata.normalize('NFKD', s)
    if okToIgnore:
        return s.encode('ascii', 'ignore').decode('ascii')
    else:
        return s.encode('ascii', 'replace').decode('ascii')

gRedirectTraceCalls = None
def trace(*args, always=False):
    """similar to print, but
    1) distinguish debugging prints vs intentional production prints
    2) can be redirected
    3) certain terminals throw exceptions if given unicode characters"""
    if gRedirectTraceCalls and not always:
        gRedirectTraceCalls(*args)
    else:
        print(' '.join(map(getPrintable, args)))

# endregion
# region _time helpers

def renderMillisTime(millisTime):
    "`millistime` is number of milliseconds past epoch (unix _time * 1000)"
    t = millisTime / 1000.0
    return _time.strftime("%m/%d/%Y %I:%M:%S %p", _time.localtime(t))

def renderMillisTimeStandard(millisTime):
    "`millistime` is number of milliseconds past epoch (unix _time * 1000)"
    t = millisTime / 1000.0
    return _time.strftime("%Y-%m-%d %I:%M:%S", _time.localtime(t))

def getNowAsMillisTime():
    "gets the number of milliseconds past epoch (unix _time * 1000)"
    t = _time._time()
    return int(t * 1000)

class EnglishDateParserWrapper:
    """more convenent than directly calling dateparser
         default to month-day-year
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
        """able to parse ones with a timezone
        compensate for +0000
        Wed Nov 07 04:01:10 +0000 2018
        """
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
        "subtract n days (simple), return datetime object"
        import datetime
        assertTrue(isinstance(nDaysBefore, int))
        diff = datetime.timedelta(days=nDaysBefore)
        return baseDate - diff

    def getDaysBeforeInMilliseconds(self, sBaseDate, nDaysBefore):
        "subtract n days (simple), return number of milliseconds past epoch"
        import datetime
        dObj = self.parse(sBaseDate)
        diff = datetime.timedelta(days=nDaysBefore)
        dBefore = dObj - diff
        return int(dBefore.timestamp() * 1000)

    def toUnixMilliseconds(self, s):
        "conviently go straight from string to the number of milliseconds past epoch"
        assertTrue(isPy3OrNewer, 'requires python 3 or newer')
        dt = self.parse(s)
        assertTrue(dt, 'not parse dt', s)
        return int(dt.timestamp() * 1000)

# endregion
# region string helpers    

def replaceMustExist(haystack, needle, replace):
    assertTrue(needle in haystack, "not found", needle)
    return haystack.replace(needle, replace)

def reSearchWholeWord(haystack, needle):
    reNeedle = '\\b' + _re.escape(needle) + '\\b'
    return _re.search(reNeedle, haystack)
    
def reReplaceWholeWord(haystack, needle, replace):
    sNeedle = '\\b' + _re.escape(needle) + '\\b'
    return _re.sub(needle, replace, haystack)

def reReplace(haystack, reNeedle, replace):
    return _re.sub(reNeedle, replace, haystack)

'''
cliffnotes documentation of _re module included here for convenience:
_re.search(pattern, string, flags=0)
    look for at most one match starting anywhere

_re.match(pattern, string, flags=0)
    look for match starting only at beginning of string

_re.findall(pattern, string, flags=0)
    returns list of strings

_re.finditer(pattern, string, flags=0)
    returns iterator of match objects

flags include _re.IGNORECASE, _re.MULTILINE, _re.DOTALL
'''

def truncateWithEllipsis(s, maxLength):
    if len(s) <= maxLength:
        return s
    else:
        ellipsis = '...'
        if maxLength < len(ellipsis):
            return s[0:maxLength]
        else:
            return s[0:maxLength - len(ellipsis)] + ellipsis

def formatSize(n):
    if n >= 1024 * 1024 * 1024:
        return '%.2fGB' % (n / (1024.0 * 1024.0 * 1024.0))
    elif n >= 1024 * 1024:
        return '%.2fMB' % (n / (1024.0 * 1024.0))
    elif n >= 1024:
        return '%.2fKB' % (n / (1024.0))
    else:
        return '%db' % n

# endregion
# region type conversion helpers

def strToList(s, replaceComments=True):
    lines = s.replace('\r\n', '\n').split('\n')
    if replaceComments:
        lines = [line for line in lines if not line.startswith('#')]
    
    return [line.strip() for line in lines if line.strip()]
    
def strToSet(s, replaceComments=True):
    lst = strToList(s, replaceComments=replaceComments)
    return set(lst)

def parseIntOrFallback(s, fallBack=None):
    try:
        return int(s)
    except:
        return fallBack
        
def parseFloatOrFallback(s, fallBack=None):
    try:
        return float(s)
    except:
        return fallBack

# endregion
# region flow helpers

def runAndCatchException(fn):
    """can be convenient to not need a try/except structure.
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
    path = pathOrig
    if dirsepOk:
        # sometimes we want to leave directory-separator characters in the string.
        if _os.path.sep == '/':
            path = path.replace(u'\\ ', u', ').replace(u'\\', u'-')
        else:
            path = path.replace(u'/ ', u', ').replace(u'/', u'-')
    else:
        path = path.replace(u'\\ ', u', ').replace(u'\\', u'-')
        path = path.replace(u'/ ', u', ').replace(u'/', u'-')

    result = path.replace(u'\u2019', u"'").replace(u'?', u'').replace(u'!', u'') \
        .replace(u': ', u', ').replace(u':', u'-') \
        .replace(u'| ', u', ').replace(u'|', u'-') \
        .replace(u'*', u'') \
        .replace(u'"', u"'").replace(u'<', u'[').replace(u'>', u']') \
        .replace(u'\r\n', u' ').replace(u'\r', u' ').replace(u'\n', u' ')

    if maxLen and len(result) > maxLen:
        assertTrue(maxLen > 1)
        ext = _os.path.splitExt(path)[1]
        beforeExt = path[0:-len(ext)]
        while len(result) > maxLen:
            result = beforeExt + ext
            beforeExt = beforeExt[0:-1]
        
        # if it ate into the directory, though, throw an error
        assertTrue(_os.path.split(pathOrig)[0] == _os.path.split(result)[0])

    return result

def stripHtmlTags(s, removeRepeatedWhitespace=True):
    """remove all html tags.
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
    """replace non-ascii or control chars.
    printable is 32-126"""
    return _re.sub(r'[^\x20-\x7e]', replaceWith, s)

def containsNonAscii(s):
    """does string contain non-ascii or control chars?
    aka does string contain chars outside 32-126"""
    withoutAscii = replaceNonAsciiWith(s, '')
    return len(s) != len(withoutAscii)

# endregion
# region object helpers and wrappers

def dirAttributes(obj):
    return [att for att in dir(obj) if not att.startswith('_')]
    
def getClassNameFromInstance(obj):
    return obj.__class__.__name__

if _sys.version_info[0] >= 2:
    "inspired by mutagen/_compat.py"
    from io import StringIO
    StringIO = StringIO
    from io import BytesIO
    cBytesIO = BytesIO

    def endsWith(a, b):
        # use with either str or bytes
        if isinstance(a, str):
            if not isinstance(b, str):
                b = b.decode("ascii")
        else:
            if not isinstance(b, bytes):
                b = b.encode("ascii")
        return a.endswith(b)

    def startsWith(a, b):
        # use with either str or bytes
        if isinstance(a, str):
            if not isinstance(b, str):
                b = b.decode("ascii")
        else:
            if not isinstance(b, bytes):
                b = b.encode("ascii")
        return a.startswith(b)

    def iterBytes(b):
        return (bytes([v]) for v in b)

    def bytesToString(b):
        return b.decode('utf-8')

    def asBytes(s, encoding='ascii'):
        return bytes(s, encoding)

    rinput = input
    ustr = str
    uchr = chr
    anystringtype = str
    bytetype = bytes
    xrange = range
    isPy3OrNewer = True
else:
    raise Exception("We no longer support python 2")

