# shinerainsoftsevencommon
# Released under the LGPLv3 License

import os
import sys
import traceback
import pprint
import re
import time


# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ assertions ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def assertTrue(condition, *messageArgs):
    if not condition:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        raise AssertionError(msg)

def assertEq(expected, received, *messageArgs):
    if expected != received:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        msg += '\nassertion failed, expected:\n'
        msg += pprint.pformat(expected)
        msg += '\nbut got:\n'
        msg += pprint.pformat(received)
        raise AssertionError(msg)

def assertWarn(condition, *messageArgs):
    from . import common_ui
    if not condition:
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        common_ui.warn(msg)

def assertWarnEq(expected, received, *messageArgs):
    from . import common_ui
    if expected != received:
        import pprint
        msg = ' '.join(map(str, messageArgs)) if messageArgs else ''
        msg += '\nexpected:\n'
        msg += pprint.pformat(expected)
        msg += '\nbut got:\n'
        msg += pprint.pformat(received)
        common_ui.warn(msg)

def assertFloatEq(expected, received, *messageArgs):
    import math
    precision = 0.000001
    difference = math.fabs(expected - received)
    if difference > precision:
        messageArgs = list(messageArgs) or []
        messageArgs.append('expected %f, got %f, difference of %f' % (
            expected, received, difference))
        assertTrue(False, *messageArgs)

def assertEqArray(expected, received):
    if isinstance(expected, str):
        expected = expected.split('|')

    assertEq(len(expected), len(received))
    for i in range(len(expected)):
        assertEq(repr(expected[i]), repr(received[i]))

def assertException(fn, excType, excTypeExpectedString=None, msg='', regexp=False):
    e = None
    try:
        fn()
    except:
        e = getCurrentException()

    assertTrue(e is not None, 'did not throw ' + msg)
    if excType:
        assertTrue(isinstance(e, excType), 'exception type check failed ' + msg +
            ' \ngot \n' + pprint.pformat(e) + '\n not \n' + pprint.pformat(excType))
    if excTypeExpectedString:
        if regexp:
            passed = re.search(excTypeExpectedString, str(e))
        else:
            passed = excTypeExpectedString in str(e)
        assertTrue(passed, 'exception string check failed ' + msg +
            '\ngot exception string:\n' + str(e))

def getTraceback(e):
    lines = traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(lines)

def getCurrentException():
    return sys.exc_info()[1]

class ShineRainSoftSevenCommonError(RuntimeError):
    "feature, you can pass in many strings like ShineRainSoftSevenCommonError('a', 'b', 'c')"
    def __init__(self, *args):
        combined = ' '.join((str(arg) for arg in args))
        super().__init__(combined)

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ trace helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def getPrintable(s, okToIgnore=False):
    ""
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

gTraceHook = None
def trace(*args, always=False):
    '''certain terminals throw exceptions if given unicode characters. this is a safer way to
    output any string.'''
    if gTraceHook and not always:
        gTraceHook(*args)
    else:
        print(' '.join(map(getPrintable, args)))

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ time helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def renderMillisTime(millisTime):
    '''"millistime" is number of milliseconds past epoch (unix time * 1000)'''
    t = millisTime / 1000.0
    return time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(t))

def renderMillisTimeStandard(millisTime):
    t = millisTime / 1000.0
    return time.strftime("%Y-%m-%d %I:%M:%S", time.localtime(t))

def getNowAsMillisTime():
    t = time.time()
    return int(t * 1000)

class EnglishDateParserWrapper:
    def __init__(self, dateOrder='MDY'):
        # default to month-day-year
        # restrict to English, less possibility of accidentally parsing a non-date string
        import dateparser
        settings = {'STRICT_PARSING': True}
        if dateOrder:
            settings['DATE_ORDER'] = dateOrder
        self.p = dateparser.date.DateDataParser(languages=['en'], settings=settings)

    def parse(self, s):
        return self.p.get_date_data(s)['date_obj']

    def fromFullWithTimezone(self, s):
        # compensate for +0000
        # Wed Nov 07 04:01:10 +0000 2018
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

    def getDaysBefore(self, baseDate, n):
        import datetime
        assertTrue(isinstance(n, int))
        diff = datetime.timedelta(days=n)
        return baseDate - diff

    def getDaysBeforeInMilliseconds(self, sBaseDate, nDaysBefore):
        import datetime
        dObj = self.parse(sBaseDate)
        diff = datetime.timedelta(days=nDaysBefore)
        dBefore = dObj - diff
        return int(dBefore.timestamp() * 1000)

    def toUnixMilliseconds(self, s):
        assertTrue(isPy3OrNewer, 'requires python 3 or newer')
        dt = self.parse(s)
        return int(dt.timestamp() * 1000)

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ string helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃    

def replaceMustExist(haystack, needle, replace):
    assertTrue(needle in haystack, "not found", needle)
    return haystack.replace(needle, replace)

def reSearchWholeWord(haystack, needle):
    reNeedle = '\\b' + re.escape(needle) + '\\b'
    return re.search(reNeedle, haystack)
    
def reReplaceWholeWord(haystack, sNeedle, replace):
    sNeedle = '\\b' + re.escape(sNeedle) + '\\b'
    return re.sub(sNeedle, replace, haystack)

def reReplace(haystack, reNeedle, replace):
    return re.sub(reNeedle, replace, haystack)

'''
cliffnotes documentation of re module included here for convenience:
re.search(pattern, string, flags=0)
    look for at most one match starting anywhere

re.match(pattern, string, flags=0)
    look for match starting only at beginning of string

re.findall(pattern, string, flags=0)
    returns list of strings

re.finditer(pattern, string, flags=0)
    returns iterator of match objects

flags include re.IGNORECASE, re.MULTILINE, re.DOTALL
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

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ type conversion helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

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

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ flow helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def skipForwardUntilTrue(iter, fnWaitUntil):
    if isinstance(iter, list):
        iter = (item for item in iter)
        
    hasSeen = False
    for value in iter:
        if not hasSeen and fnWaitUntil(value):
            hasSeen = True
        if hasSeen:
            yield value

def runAndCatchException(fn):
    try:
        result = fn()
        return Bucket(result=result, err=None)
    except:
        import sys
        return Bucket(result=None, err=getCurrentException())

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ ascii char helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def toValidFilename(pathOrig, dirsepOk=False, maxLen=None):
    path = pathOrig
    if dirsepOk:
        # sometimes we want to leave directory-separator characters in the string.
        if os.path.sep == '/':
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
        ext = os.path.splitExt(path)[1]
        beforeExt = path[0:-len(ext)]
        while len(result) > maxLen:
            result = beforeExt + ext
            beforeExt = beforeExt[0:-1]
        
        # if it ate into the directory, though, throw an error
        assertTrue(os.path.split(pathOrig)[0] == os.path.split(result)[0])

    return result

def stripHtmlTags(s, removeRepeatedWhitespace=True):
    # a (?:) is a non-capturing group
    # see also: html.escape, html.unescape
    reTags = re.compile(r'<[^>]+(?:>|$)', re.DOTALL)
    s = reTags.sub(' ', s)
    if removeRepeatedWhitespace:
        regNoDblSpace = re.compile(r'\s+')
        s = regNoDblSpace.sub(' ', s)
        s = s.strip()

    # for malformed tags like "<a<" with no close, replace with ?
    s = s.replace('<', '?').replace('>', '?')
    return s

def replaceNonAsciiWith(s, replaceWith):
    # total range 0-127
    # printable 32-126
    return re.sub(r'[^\x20-\x7e]', replaceWith, s)

def containsNonAscii(s):
    withoutAscii = replaceNonAsciiWith(s, '')
    return len(s) != len(withoutAscii)

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ object helpers and wrappers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def dirFields(obj):
    return [fld for fld in dir(obj) if not fld.startswith('_')]
    
def getClassNameFromInstance(obj):
    return obj.__class__.__name__

if sys.version_info[0] >= 2:
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
    # inspired by mutagen/_compat.py
    raise Exception("We no longer support python 2")

