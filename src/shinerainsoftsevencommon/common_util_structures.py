
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

# inspired by http://code.activestate.com/recipes/496879-memoize-decorator-function-with-cache-size-limit/
def BoundedMemoize(fn, limit=20):
    from collections import OrderedDict
    cache = OrderedDict()

    def memoize_wrapper(*args, **kwargs):
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
            if len(cache) > memoize_wrapper._limit:
                cache.popitem(False)  # the false means remove as FIFO
            return result

    memoize_wrapper._limit = limit
    memoize_wrapper._cache = cache
    if isPy3OrNewer:
        memoize_wrapper.__name__ = fn.__name__
    else:
        memoize_wrapper.func_name = fn.func_name
    
    return memoize_wrapper

