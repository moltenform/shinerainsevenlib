
# shinerainsoftsevencommon
# Released under the LGPLv3 License
from .common_util_datetime import *

class Bucket:
    "simple named-tuple; o.field looks nicer than o['field']. "
    def __init__(self, **kwargs):
        for key in kwargs:
            object.__setattr__(self, key, kwargs[key])

    def __repr__(self):
        return '\n\n\n'.join(('%s=%s'%(ustr(key), ustr(self.__dict__[key])) for key in sorted(self.__dict__)))

class SimpleEnum:
    "simple enum; prevents modification after creation."
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

TimeUnits = SimpleEnum(('Milliseconds', 'Seconds', 'Nanoseconds'))

def addOrAppendToArrayInDict(d, key, val):
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

# keep a separate random stream that won't get affected by someone else calling seed()
class IndependentRNG:
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
    
    def __exit__(self ,type, value, traceback):
        if not self.entered:
            return
                
        self.entered = False
        random.setstate(self.keep_outside_state)
        

# inspired by http://code.activestate.com/recipes/496879-memoize-decorator-function-with-cache-size-limit/
def BoundedMemoize(fn, limit=20):
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
    
    
