# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2 License

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

from . import m2_core_data_structures as _m2_core_data_structures


def concat(ar1, ar2):
    "Like extend, but operates on a copy"
    ar = list(ar1)
    ar.extend(ar2)
    return ar


def every(lst, fn):
    "Return true if the condition holds for all items, will exit early"
    return builtins.all(builtins.map(fn, lst))


def some(lst, fn):
    "Return true if fn called on any element returns true, exits early"
    return builtins.any(builtins.map(fn, lst))


# pylint: disable-next=redefined-builtin
def filter(lst, fn):
    "Return a list with items where the condition holds"
    return [item for item in lst if fn(item)]


def find(lst, fn):
    "Returns the value in a list where fn returns true, or None"
    ind = findIndex(lst, fn)
    return lst[ind] if ind != -1 else None


def findIndex(lst, fn):
    "Returns the position in a list where fn returns true, or None"
    for i, val in enumerate(lst):
        if fn(val):
            return i
    return -1


def indexOf(lst, valToFind):
    "Search for a value and return first position where seen, or -1"
    for i, val in enumerate(lst):
        if val == valToFind:
            return i
    return -1


def lastIndexOf(lst, valToFind):
    "Search for a value and return last position where seen, or -1"
    i = len(lst) - 1
    while i >= 0:
        if lst[i] == valToFind:
            return i
        i -= 1
    return -1


# pylint: disable-next=redefined-builtin
def map(lst, fn):
    "Return a list with fn called on each item"
    return list(builtins.map(fn, lst))


def times(n, fn):
    "Return a list with n items, values from calling fn"
    return [fn() for _ in range(n)]


def reduce(lst, fn, initialVal=_m2_core_data_structures.DefaultVal):
    "Like JS reduce. Callback should have 2 parameters"
    import functools

    if initialVal is _m2_core_data_structures.DefaultVal:
        return functools.reduce(fn, lst)
    else:
        return functools.reduce(fn, lst, initialVal)


def splice(s, insertionPoint, lenToDelete=0, newText=''):
    "Like javascript's splice"
    return s[0:insertionPoint] + newText + s[insertionPoint + lenToDelete :]

def spliceSpan(s, span, newText):
    "Provide a span [startIndex, stopIndex] to be replaced with newText"
    _m5_batch_util.assertEq(2, len(span), 'expected [startIndex, stopIndex]')
    _m5_batch_util.assertTrue(span[1] >= span[0])
    return splice(s, span[0], span[1] - span[0], newText)
