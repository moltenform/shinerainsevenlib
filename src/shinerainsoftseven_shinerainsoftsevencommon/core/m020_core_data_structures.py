
# shinerainsoftsevencommon
# Released under the LGPLv3 License

from m010_core_util import *

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ simple persistence ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

class PersistedDict:
    data = None
    handle = None
    counter = 0
    persistEveryNWrites = 1

    def __init__(self, filename, warnIfCreatingNew=True,
            keepHandle=False, persistEveryNWrites=5):
        from . import files
        from . import common_ui
        self.filename = filename
        self.persistEveryNWrites = persistEveryNWrites
        if not files.exists(filename):
            if warnIfCreatingNew:
                common_ui.alert("creating new cache at " + filename)
            files.writeAll(filename, '{}')
            
        self.load()
        if keepHandle:
            self.handle = open(filename, 'w')
            self.persist()

    def load(self):
        import json
        from . import files
        txt = files.readAll(self.filename, encoding='utf-8')
        self.data = json.loads(txt)

    def close(self):
        if self.handle:
            self.handle.close()
            self.handle = None

    def persist(self):
        import json
        from . import files
        txt = json.dumps(self.data)
        if self.handle:
            self.handle.seek(0, os.SEEK_SET)
            self.handle.write(txt)
            self.handle.truncate()
        else:
            files.writeAll(self.filename, txt, encoding='utf-8')

    def afterUpdate(self):
        self.counter += 1
        if self.counter % self.persistEveryNWrites == 0:
            self.persist()

    def set(self, key, value):
        self.data[key] = value
        self.afterUpdate()

    def setSubDict(self, subdictname, key, value):
        if subdictname not in self.data:
            self.data[subdictname] = {}
        self.data[subdictname][key] = value
        self.afterUpdate()

    def setSubSubDict(self, subdictname, key1, key2, value):
        if subdictname not in self.data:
            self.data[subdictname] = {}
        self.data[subdictname][key1][key2] = value
        self.afterUpdate()

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ retrieve text from strings ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

class ParsePlus:
    '''
    ParsePlus, by Ben Fisher 2019

    Adds the following features to the "parse" module:
        {s:NoNewlines} field type
        {s:NoSpaces} works like {s:S}
        remember that "{s} and {s}" matches "a and a" but not "a and b",
            use "{s1} and {s2}" or "{} and {}" if the contents can differ
        escapeSequences such as backslash-escapes (see examples in tests)
        replaceFieldWithText (see examples in tests)
        getTotalSpan
    '''
    def __init__(self, pattern, extra_types=None, escapeSequences=None,
            case_sensitive=True):
        try:
            import parse
        except:
            raise ImportError('needs "parse", can install from pip, https://pypi.org/project/parse/')
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.extra_types = extra_types if extra_types else {}
        self.escapeSequences = escapeSequences if escapeSequences else []
        if 'NoNewlines' in pattern:
            @parse.with_pattern(r'[^\r\n]+')
            def parse_NoNewlines(s):
                return str(s)
            self.extra_types['NoNewlines'] = parse_NoNewlines
            
        if 'NoSpaces' in pattern:
            @parse.with_pattern(r'[^\r\n\t ]+')
            def parse_NoSpaces(s):
                return str(s)
            self.extra_types['NoSpaces'] = parse_NoSpaces

    def _createEscapeSequencesMap(self, s):
        self._escapeSequencesMap = {}
        if len(self.escapeSequences) > 5:
            raise ValueError('we support a max of 5 escape sequences')

        sTransformed = s
        for i, seq in enumerate(self.escapeSequences):
            assertTrue(len(seq) > 1, "an escape-sequence only makes sense if " +
                "it is at least two characters")

            # use a rarely-occurring ascii char like
            # \x01 (start of heading)
            rareChar = chr(i + 1)
            
            # raise error if there's any occurance of rareChar, not repl,
            # otherwise we would have incorrect expansions
            if rareChar in s:
                raise RuntimeError("we don't yet support escape sequences " +
                "if the input string contains rare ascii characters. the " +
                "input string contains " + rareChar + ' (ascii ' +
                str(ord(rareChar)) + ')')
                
            # replacement string is the same length, so offsets aren't affected
            repl = rareChar * len(seq)
            self._escapeSequencesMap[repl] = seq
            sTransformed = sTransformed.replace(seq, repl)

        assertEq(len(s), len(sTransformed), 'internal error: len(s) changed.')
        return sTransformed

    def _unreplaceEscapeSequences(self, s):
        for key in self._escapeSequencesMap:
            s = s.replace(key, self._escapeSequencesMap[key])
        return s

    def _resultToMyResult(self, parseResult, s):
        if not parseResult:
            return parseResult
        ret = Bucket()
        lenS = len(s)
        for name in parseResult.named:
            val = self._unreplaceEscapeSequences(parseResult.named[name])
            setattr(ret, name, val)
        ret.spans = parseResult.spans
        ret.getTotalSpan = lambda: self._getTotalSpan(parseResult, lenS)
        return ret

    def _getTotalSpan(self, parseResult, lenS):
        if '{{' in self.pattern or '}}' in self.pattern:
            raise RuntimeError("for simplicity, we don't yet support getTotalSpan " +
                "if the pattern contains {{ or }}")
        locationOfFirstOpen = self.pattern.find('{')
        locationOfLastClose = self.pattern.rfind('}')
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
        largestSpanEnd += len(self.pattern) - (locationOfLastClose + len('}'))

        # sanity check that the bounds make sense
        assertTrue(0 <= smallestSpanStart <= lenS,
            'internal error: span outside bounds')
        assertTrue(0 <= largestSpanEnd <= lenS,
            'internal error: span outside bounds')
        assertTrue(largestSpanEnd >= smallestSpanStart,
            'internal error: invalid span')
        return (smallestSpanStart, largestSpanEnd)

    def match(self, s):
        # entire string must match
        import parse
        sTransformed = self._createEscapeSequencesMap(s)
        parseResult = parse.parse(self.pattern, sTransformed,
            extra_types=self.extra_types, case_sensitive=self.case_sensitive)
        return self._resultToMyResult(parseResult, s)

    def search(self, s):
        import parse
        sTransformed = self._createEscapeSequencesMap(s)
        parseResult = parse.search(self.pattern, sTransformed,
            extra_types=self.extra_types, case_sensitive=self.case_sensitive)
        return self._resultToMyResult(parseResult, s)

    def findAll(self, s):
        import parse
        sTransformed = self._createEscapeSequencesMap(s)
        parseResults = parse.findall(self.pattern, sTransformed,
            extra_types=self.extra_types, case_sensitive=self.case_sensitive)
        for parseResult in parseResults:
            yield self._resultToMyResult(parseResult, s)

    def replaceFieldWithText(self, s, key, newValue,
            appendIfNotFound=None, allowOnlyOnce=False):
        from . import jslike
        # example: <title>{title}</title>
        results = list(self.findall(s))
        if allowOnlyOnce and len(results) > 1:
            raise RuntimeError('we were told to allow pattern only once.')
        if len(results):
            span = results[0].spans[key]
            return jslike.spliceSpan(s, span, newValue)
        else:
            if appendIfNotFound is None:
                raise RuntimeError("pattern not found.")
            else:
                return s + appendIfNotFound

    def replaceFieldWithTextIntoFile(self, path, key, newValue,
            appendIfNotFound=None, allowOnlyOnce=False, encoding=None):
        from .files import readAll, writeAll
        s = readAll(path, encoding=encoding)

        newS = self.replaceFieldWithText(s, key, newValue,
            appendIfNotFound=appendIfNotFound,
            allowOnlyOnce=allowOnlyOnce)

        writeAll(path, newS, 'w', encoding=encoding, skipIfSameContent=True)

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ enum helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

class Bucket:
    "simple named-tuple; o.field looks nicer than o['field']. "
    def __init__(self, **kwargs):
        for key in kwargs:
            object.__setattr__(self, key, kwargs[key])

    def __repr__(self):
        return '\n\n\n'.join(('%s=%s'%(ustr(key), ustr(self.__dict__[key])) for key in sorted(self.__dict__)))

class SimpleEnum:
    "simple enum; also blocks modification after creation."
    _set = None

    def __init__(self, listStart):
        assertTrue(not isinstance(listStart, anystringtype))
        self._set = set(listStart)

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        elif name in self._set:
            return name
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            raise RuntimeError

    def __delattr__(self, name):
        raise RuntimeError

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ data structure helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def appendToListInDictOrStartNewList(d, key, val):
    # easier to read than setdefault
    got = d.get(key, None)
    if got:
        got.append(val)
    else:
        d[key] = [val]

def takeBatchOnArbitraryIterable(iterable, size):
    import itertools
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))

def takeBatch(itr, n):
    """ Yield successive n-sized chunks from l."""
    return list(takeBatchOnArbitraryIterable(itr, n))

class TakeBatch:
    def __init__(self, batchSize, callback):
        self.batch = []
        self.batchSize = batchSize
        self.callback = callback

    def append(self, item):
        self.batch.append(item)
        if len(self.batch) >= self.batchSize:
            self.callback(self.batch)
            self.batch = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # if exiting normally (not by exception), run the callback
        if not exc_type:
            if len(self.batch):
                self.callback(self.batch)

class RecentlyUsedList:
    '''Keep a list of items without storing duplicates'''
    def __init__(self, maxSize=None, startList=None):
        self.list = startList or []
        self.maxSize = maxSize

    def getList(self):
        return self.list

    def indexOf(self, s):
        try:
            return self.list.index(s)
        except ValueError:
            return -1

    def add(self, s):
        # if it's also elsewhere in the list, remove that one
        index = self.indexOf(s)
        if index != -1:
            self.list.pop(index)

        # insert new entry at the top
        self.list.insert(0, s)

        # if we've reached the limit, cut out the extra ones
        if self.maxSize:
            while len(self.list) > self.maxSize:
                self.list.pop()

# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ rng state helper ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

class IndependentRNG:
    "keep a separate random stream that won't get affected by someone else calling seed()"
    def __init__(self, seed=None):
        import random
        if seed is not None:
            random.seed(seed)
            
        self.state = random.getstate()
        self.keep_outside_state = None
        self.entered = False
    
    def __enter__(self):
        if self.entered:
            return
        
        self.entered = True
        self.keep_outside_state = random.getstate()
        random.setstate(self.state)
    
    def __exit__(self, type, value, traceback):
        if not self.entered:
            return
                
        self.entered = False
        random.setstate(self.keep_outside_state)
    
# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ automatically memo-ize ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def BoundedMemoize(fn, limit=20):
    "inspired by http://code.activestate.com/recipes/496879-memoize-decorator-function-with-cache-size-limit/"
    from collections import OrderedDict
    cache = OrderedDict()

    def memoizeWrapper(*args, **kwargs):
        try:
            import cPickle as pickle
        except ImportError:
            import pickle
        key = pickle.dumps((args, kwargs))
        try:
            return cache[key]
        except KeyError:
            result = fn(*args, **kwargs)
            cache[key] = result
            if len(cache) > memoizeWrapper._limit:
                cache.popitem(False)  # the false means remove as FIFO
            return result

    memoizeWrapper._limit = limit
    memoizeWrapper._cache = cache
    if isPy3OrNewer:
        memoizeWrapper.__name__ = fn.__name__
    else:
        memoizeWrapper.func_name = fn.func_name
    
    return memoizeWrapper


# ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ set helpers ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃

def compareTwoListsAsSets(l1, l2, transformFn1=None, transformFn2=None):
    l1Transformed = l1 if not transformFn1 else [transformFn1(item) for item in l1]
    l2Transformed = l2 if not transformFn2 else [transformFn2(item) for item in l2]
    set1 = set(l1Transformed)
    set2 = set(l2Transformed)
    if len(set1) != len(l1Transformed):
        raise ValueError('Duplicate item(s) seen in list 1.' + str(l1Transformed))
    if len(set2) != len(l2Transformed):
        raise ValueError('Duplicate item(s) seen in list 2.' + str(l2Transformed))
    
    extraItems = list(set1 - set2)
    missingItems = list(set2 - set1)
    return Bucket(extraItems=extraItems, missingItems=missingItems)

def expectEqualityTwoListsAsSets(l1, l2, transformFn1=None, transformFn2=None):
    result = compareTwoListsAsSets(l1, l2, transformFn1=None, transformFn2=None)
    if len(result.extraItems):
        trace('Extra items seen in list 1:', result.extraItems)
        return False
    
    if len(result.missingItems):
        trace('Missing items not present in list 1:', result.missingItems)
        return False
    
    return True

def throwIfDuplicates(l1, transformFn1=None, context=''):
    l1Transformed = l1 if not transformFn1 else [transformFn1(item) for item in l1]
    seen = {}
    for item in l1Transformed:
        if item in seen:
            raise ShineRainSoftSevenCommonError('duplicate seen:', item, context)
    
def mergeParamsIntoBucket(bucketConfigs, dictParams):
    for key in params:
        if key in dir(self.configs) and not key.startswith('_'):
            setattr(self.configs, key, params[key])
        else:
            raise Exception('not a supported config:', key)

    
