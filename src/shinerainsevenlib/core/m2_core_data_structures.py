
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

from collections import namedtuple
import os as _os
import sys as _sys
import json as _json
import enum as _enum
from enum import StrEnum as _StrEnum

from .m1_core_util import *

# region simple persistence

class PersistedDict:
    "Store a dict (or dict of dicts) on disk."

    _data = None
    _handle = None
    _counter = 0
    _persistEveryNWrites = 1

    def __init__(self, filename, warnIfCreatingNew=True, keepHandle=False, persistEveryNWrites=5):
        from .. import files
        from .m4_core_ui import alert

        self._filename = filename
        self._persistEveryNWrites = persistEveryNWrites
        if not files.exists(filename):
            if warnIfCreatingNew:
                alert('creating new cache at ' + filename)

            files.writeAll(filename, '{}')

        self.load()
        if keepHandle:
            self._handle = open(filename, 'w', encoding='utf-8')  # noqa
            self.persist()

    def load(self, encoding='utf-8'):
        "Load from disk"
        from .. import files

        txt = files.readAll(self._filename, encoding=encoding)
        self._data = _json.loads(txt)

    def close(self):
        "Close the connection"
        if self._handle:
            self._handle.close()
            self._handle = None

    def persist(self):
        "Save to disk. Must be called manually."
        from .. import files

        txt = _json.dumps(self._data)
        if self._handle:
            self._handle.seek(0, _os.SEEK_SET)
            self._handle.write(txt)
            self._handle.truncate()
        else:
            files.writeAll(self._filename, txt, encoding='utf-8')

    def _afterUpdate(self):
        self._counter += 1
        if self._counter % self._persistEveryNWrites == 0:
            self.persist()

    def set(self, key, value):
        "Set a value"
        self._data[key] = value
        self._afterUpdate()

    def setSubDict(self, subDictName, key, value):
        "Set a nested value"
        if subDictName not in self._data:
            self._data[subDictName] = {}
        self._data[subDictName][key] = value
        self._afterUpdate()

    def setSubSubDict(self, subDictName, key1, key2, value):
        "Set a doubly nested value"
        if subDictName not in self._data:
            self._data[subDictName] = {}
        self._data[subDictName][key1][key2] = value
        self._afterUpdate()

# endregion
# region retrieve text from strings

class ParsePlus:
    """
    Adds the following features to the "parse" module:
    
    {s:NoNewlines} field type
    
    {s:NoSpaces} works like {s:S}
    
    remember that "{s} and {s}" matches "a and a" but not "a and b",
    
    use "{s1} and {s2}" or "{} and {}" if the contents can differ.

    escapeSequences such as backslash-escapes (see examples in tests).
    
    Added features beyond parse, including:

    replaceFieldWithText()
    
    getTotalSpan attribute

    accessing results directly, writing result.name instead of result.get('name')
    """

    def __init__(self, pattern, extraTypes=None, escapeSequences=None, caseSensitive=True):
        try:
            import parse
        except ImportError as e:
            raise ImportError('Please run "pip install parse"') from e

        self._pattern = pattern
        self._caseSensitive = caseSensitive
        self._extraTypes = extraTypes if extraTypes else {}
        self._escapeSequences = escapeSequences if escapeSequences else []
        self.spans = None
        self.getTotalSpan = None
        self._escapeSequencesMap = None
        if 'NoNewlines' in pattern:

            @parse.with_pattern(r'[^\r\n]+')
            def parse_NoNewlines(s):
                return str(s)

            self._extraTypes['NoNewlines'] = parse_NoNewlines

        if 'NoSpaces' in pattern:

            @parse.with_pattern(r'[^\r\n\t ]+')
            def parse_NoSpaces(s):
                return str(s)

            self._extraTypes['NoSpaces'] = parse_NoSpaces

    def _createEscapeSequencesMap(self, s):
        self._escapeSequencesMap = {}
        if len(self._escapeSequences) > 5:
            raise ValueError('we support a max of 5 escape sequences')

        sTransformed = s
        for i, seq in enumerate(self._escapeSequences):
            assertTrue(
                len(seq) > 1,
                'an escape-sequence only makes sense if it is at least two characters',
            )

            # use a rarely-occurring ascii char,
            # \x01 (start of heading)
            rareChar = chr(i + 1)

            # raise error if there's any occurance of rareChar, not repl,
            # otherwise we would have incorrect expansions
            if rareChar in s:
                raise RuntimeError(
                    "we don't yet support escape sequences " +
                    'if the input string contains rare ascii characters. the ' +
                    'input string contains ' +
                    rareChar +
                    ' (ascii ' +
                    str(ord(rareChar)) +
                    ')'
                )

            # replacement string is the same length, so offsets aren't affected
            repl = rareChar * len(seq)
            self._escapeSequencesMap[repl] = seq
            sTransformed = sTransformed.replace(seq, repl)

        assertEq(len(s), len(sTransformed), 'internal error: len(s) changed.')
        return sTransformed

    def _unreplaceEscapeSequences(self, s):
        for key, val in self._escapeSequencesMap.items():
            s = s.replace(key, val)
        return s

    def _resultToMyResult(self, parseResult, s):
        "Be useful and tack on some extra information to the results"
        if not parseResult:
            return parseResult

        class _ParsePlusResults:
            # namedtuple is sometimes useful, but immutable
            def __init__(self, spans, getTotalSpan):
                self.spans = spans
                self.getTotalSpan = getTotalSpan

        lengthOfString = len(s)
        ret = _ParsePlusResults(spans = parseResult.spans, getTotalSpan =
            lambda: self._getTotalSpan(parseResult, lengthOfString))
        
        for name in parseResult.named:
            val = self._unreplaceEscapeSequences(parseResult.named[name])
            setattr(ret, name, val)

        return ret

    def _getTotalSpan(self, parseResult, lenS):
        if '{{' in self._pattern or '}}' in self._pattern:
            raise RuntimeError(
                "for simplicity, we don't yet support getTotalSpan " +
                'if the pattern contains {{ or }}'
            )

        locationOfFirstOpen = self._pattern.find('{')
        locationOfLastClose = self._pattern.rfind('}')
        if locationOfFirstOpen == -1 or locationOfLastClose == -1:
            # pattern contained no fields?
            return None

        if not len(parseResult.spans):
            # pattern contained no fields?
            return None
        smallestSpanStart = float('inf')
        largestSpanEnd = -1
        for key in parseResult.spans:
            lower, upper = parseResult.spans[key]
            smallestSpanStart = min(smallestSpanStart, lower)
            largestSpanEnd = max(largestSpanEnd, upper)

        # ex.: for the pattern aaa{field}bbb, widen by len('aaa') and len('bbb')
        smallestSpanStart -= locationOfFirstOpen
        largestSpanEnd += len(self._pattern) - (locationOfLastClose + len('}'))

        # sanity check that the bounds make sense
        assertTrue(0 <= smallestSpanStart <= lenS, 'internal error: span outside bounds')
        assertTrue(0 <= largestSpanEnd <= lenS, 'internal error: span outside bounds')
        assertTrue(largestSpanEnd >= smallestSpanStart, 'internal error: invalid span')
        return (smallestSpanStart, largestSpanEnd)

    def match(self, s):
        "Entire string must match"
        import parse

        sTransformed = self._createEscapeSequencesMap(s)
        parseResult = parse.parse(
            self._pattern,
            sTransformed,
            extra_types=self._extraTypes,
            case_sensitive=self._caseSensitive,
        )
        return self._resultToMyResult(parseResult, s)

    def search(self, s):
        "Get one result"
        import parse

        sTransformed = self._createEscapeSequencesMap(s)
        parseResult = parse.search(
            self._pattern,
            sTransformed,
            extra_types=self._extraTypes,
            case_sensitive=self._caseSensitive,
        )
        return self._resultToMyResult(parseResult, s)

    def findAll(self, s):
        "Get an iterator with all results"
        import parse

        sTransformed = self._createEscapeSequencesMap(s)
        parseResults = parse.findall(
            self._pattern,
            sTransformed,
            extra_types=self._extraTypes,
            case_sensitive=self._caseSensitive,
        )
        for parseResult in parseResults:
            yield self._resultToMyResult(parseResult, s)

    def replaceFieldWithText(self, s, key, newValue, appendIfNotFound=None, allowOnlyOnce=False):
        "Example: <title>{title}</title>"
        from . import m6_jslike

        results = list(self.findAll(s))
        if allowOnlyOnce and len(results) > 1:
            raise RuntimeError('we were told to allow pattern only once.')
        if len(results):
            span = results[0].spans[key]
            return m6_jslike.spliceSpan(s, span, newValue)
        else:
            if appendIfNotFound is None:
                raise RuntimeError('pattern not found.')
            else:
                return s + appendIfNotFound

    def replaceFieldWithTextIntoFile(
        self, path, key, newValue, appendIfNotFound=None, allowOnlyOnce=False, encoding='utf-8'
    ):
        "Convenience method to write the results to a file"
        from .. import files

        s = files.readAll(path, encoding=encoding)

        newS = self.replaceFieldWithText(
            s, key, newValue, appendIfNotFound=appendIfNotFound, allowOnlyOnce=allowOnlyOnce
        )

        files.writeAll(path, newS, 'w', encoding=encoding, skipIfSameContent=True)

# endregion

# region enum helpers

class Bucket:
    """Simple named-tuple; for cases where o.field looks nicer than o['field'].
    Similar to standard library's types.SimpleNamespace."""

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            object.__setattr__(self, key, val)

    def __repr__(self):
        return '\n'.join(
            '%s=%s' % ((key), (self.__dict__[key])) for key in sorted(self.__dict__)
        )

    def get(self, k, fallback=None):
        "You typically would say bucket.field, but if needed, bucket.get('field') is equivalent."
        if hasattr(self, k):
            return getattr(self, k)
        else:
            return fallback
    
    def set(self, k, v):
        "You typically would say bucket.field = 123, but if needed,"
        "bucket.set('field', 123) is equivalent."
        setattr(self, k, v)
    
    def getChildKeys(self):
        "Returns a list of keys in this bucket."
        return [k for k in dir(self) if not k.startswith('_') and not callable(self.get(k))]

# we used to have our own SimpleEnum implementation, before IntEnum was in std lib

class _EnumExampleInt(_enum.IntEnum):
    "Demo using IntEnum"
    first = _enum.auto()
    second = _enum.auto()
    third = _enum.auto()

# if running in python 3.10 or earlier, see backports.strenum

class _EnumExampleStr(_StrEnum):
    "Demo using StrEnum"
    first = _enum.auto()
    second = _enum.auto()
    third = _enum.auto()

assertEq(1, _EnumExampleInt.first.value)
assertEq('first', _EnumExampleStr.first)

class SentinalIndicatingDefault:
    def __repr__(self):
        return 'DefaultValue'


DefaultVal = SentinalIndicatingDefault()
"""Use this special constant when writing keyword args to see if an argument was passed
rather than fallback to a default, see pep 661"""


# endregion
# region data structure helpers

def appendToListInDictOrStartNewList(d, key, val):
    "Could use setdefault, but this is easier to read in my opinion"
    got = d.get(key, None)
    if got:
        got.append(val)
    else:
        d[key] = [val]

def takeBatchOnArbitraryIterable(iterable, size):
    "Yield successive n-sized chunks from a list, like javascript's _.chunk"
    import itertools

    itr = iter(iterable)
    item = list(itertools.islice(itr, size))
    while item:
        yield item
        item = list(itertools.islice(itr, size))

def takeBatch(itr, n):
    "Get successive n-sized chunks from a list, like javascript's _.chunk"
    return list(takeBatchOnArbitraryIterable(itr, n))

class TakeBatch:
    """Run a callback on n-sized chunks from a list, like javascript's _.chunk.
    The convenient part is that any leftover pieces will be automatically processed.
    
    >>> def callback(batch):
    >>>     print(batch)
    >>>    
    >>> with TakeBatch(batchSize=2, callback=callback) as obj:
    >>>    obj.append(1)
    >>>    obj.append(2)
    >>>    obj.append(3)
    >>>
    >>> # (at this point anything left in the object is run automatically)
    >>>
    >>> # prints:
    >>> # [1, 2]
    >>> # [3]
    
    """

    def __init__(self, batchSize, callback):
        self.batch = []
        self.batchSize = batchSize
        self.callback = callback

    def append(self, item):
        "Add an item, and if the batch is full, run the callback"
        self.batch.append(item)
        if len(self.batch) >= self.batchSize:
            self.callback(self.batch)
            self.batch = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, _exc_val, _exc_tb):
        # if exiting normally (not by exception), run the callback
        if not exc_type:
            if len(self.batch):
                self.callback(self.batch)

def listToNPieces(lst, nPieces):
    """Split a list into n pieces

    listToNPieces([1, 2, 3, 4, 5, 6], 2) -> [[1, 2, 3], [4, 5, 6]]"""
    if nPieces > len(lst):
        raise ValueError('list is not long enough')
    
    for i in range(nPieces):
        yield lst[i::nPieces]

class RecentlyUsedList:
    "Keep a list of items. Doesn't store duplicates"

    def __init__(self, maxSize=None, startList=None):
        self.list = startList or []
        self.maxSize = maxSize

    def getList(self):
        "Access the list"
        return self.list

    def add(self, s):
        "Add an item to the list. If we are full, removes an old item to make space"

        # if it's also elsewhere in the list, remove that one
        from . import m6_jslike

        index = m6_jslike.indexOf(self.list, s)
        if index != -1:
            self.list.pop(index)

        # insert new entry at the top
        self.list.insert(0, s)

        # if we've reached the limit, cut out the extra ones
        if self.maxSize:
            while len(self.list) > self.maxSize:
                self.list.pop()

# endregion
# region automatically memo-ize

def BoundedMemoize(fn, ):
    """Inspired by http://code.activestate.com/recipes/496879-memoize-decorator-function-with-cache-size-limit/
    
    The number of items cached defaults to 20.
    You can adjust the number of items cached by setting the .limit expando property on the function itself.
    
    >>> @BoundedMemoize
    >>> def addTwoNumbers(a, b):
    >>>     return a + b
    >>>
    >>> addTwoNumbers.limit = 20
    >>> 
    >>> # this will cause the results from addTwoNumbers to be cached,
    >>> # enabling fast performance on subsequent calls.
    """
    from collections import OrderedDict
    import pickle

    cache = OrderedDict()

    limit = 20

    def memoizeWrapper(*args, **kwargs):
        key = pickle.dumps((args, kwargs))
        try:
            return cache[key]
        except KeyError:
            result = fn(*args, **kwargs)
            cache[key] = result
            # pylint: disable-next=protected-access
            if len(cache) > memoizeWrapper.limit:
                cache.popitem(False)  # the false means to remove as FIFO
            return result

    memoizeWrapper.limit = limit
    memoizeWrapper.cache = cache
    if isPy3OrNewer:
        memoizeWrapper.__name__ = fn.__name__
    else:
        memoizeWrapper.func_name = fn.func_name

    return memoizeWrapper

# endregion

