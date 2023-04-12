
# shinerainsoftsevencommon
# Released under the LGPLv3 License
from .common_util_assertions import *

import sys
import os
import re


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
re.search(pattern, string, flags=0)
    look for at most one match starting anywhere

re.match(pattern, string, flags=0)
    look for match starting only at beginning of string

re.findall(pattern, string, flags=0)
    returns list of strings

re.finditer(pattern, string, flags=0)
    returns iterator of match objects

re.IGNORECASE, re.MULTILINE, re.DOTALL
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
    return re.sub(r'[^\x00-\x7f]', replaceWith, s)

def containsNonAscii(s):
    withoutAscii = replaceNonAsciiWith(s, '')
    return len(s) != len(withoutAscii)

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

