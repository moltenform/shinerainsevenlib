
import os as _os
import sys as _sys
import re as _re
import pprint as _pprint
import unicodedata as _unicodedata
import types as _types


# region string helpers

def strToList(s, replaceComments=True):
    "When quickly writing code, get a list of strings, useful for short scripts"
    lines = standardNewlines(s).split('\n')
    if replaceComments:
        lines = [line for line in lines if not line.strip().startswith('#')]

    return [line.strip() for line in lines if line.strip()]

def strToSet(s, replaceComments=True):
    "When quickly writing code, get a set from a list of strings, useful for short scripts"
    lst = strToList(s, replaceComments=replaceComments)
    return set(lst)

def standardNewlines(s):
    "Normalize newlines to \\n"
    return s.replace('\r\n', '\n').replace('\r', '\n')

def longStr(s):
    "When quickly writing code, get a string that spans multiple lines."
    s = _re.sub(r'\r|\n', ' ', s)
    s = _re.sub(r'\t', ' ', s)
    s = _re.sub(r' +', ' ', s)
    s = s.strip()
    return s

def easyToEnterFilepath(s, checkIfExists=True):
    '''Lets people easily copy/paste a filepath in, without worrying about quotes or extra whitespace.
    See unit tests for examples.'''
    lines = [line.replace('"', '').replace("'", '').strip() for line in strToList(s)]
    candidateLines = [line for line in lines if line]
    if len(candidateLines) == 0:
        raise ValueError("No input given")
    elif len(candidateLines) > 1:
        raise ValueError("More than one input given. You can comment-out extra lines with #")
    s = candidateLines[0]
    for c in s:
        if ord(c) < ord(' '):
            raise ValueError(f'Non-ascii character found {ord(c)}, do you have a backslash without a r""?')
    if checkIfExists and not _os.path.exists(s):
        raise ValueError(f"easyToEnterFilepath, path {s} not found")
    return s

def parseIntOrFallback(s, fallBack=None):
    "Parse as an int, or return None"
    try:
        return int(s)
    except:
        return fallBack

def parseFloatOrFallback(s, fallBack=None):
    "Parse as a float, or return None"
    try:
        return float(s)
    except:
        return fallBack

def clampNumber(value, minValue, maxValue):
    "If the input is bigger than maxValue, return maxValue, if smaller than minValue, return minValue"
    if not minValue <= maxValue:
        raise ValueError('minValue must be less than or equal to maxValue')

    return max(minValue, min(value, maxValue))

# endregion

# region set helpers

def compareTwoListsAsSets(l1, l2, transformFn1=None, transformFn2=None):
    "Compare two lists of strings"
    from .m2_core_data_structures import Bucket
    
    l1Transformed = l1 if not transformFn1 else [transformFn1(item) for item in l1]
    l2Transformed = l2 if not transformFn2 else [transformFn2(item) for item in l2]
    set1 = set(l1Transformed)
    set2 = set(l2Transformed)
    if len(set1) != len(l1Transformed):
        raise ValueError('Duplicate item(s) seen in list 1.' + str(l1Transformed))
    if len(set2) != len(l2Transformed):
        raise ValueError('Duplicate item(s) seen in list 2.' + str(l2Transformed))

    addedItems = list(set2 - set1)
    lostItems = list(set1 - set2)

    # sort, or else the order is nondeterministic
    addedItems.sort()
    lostItems.sort()
    return Bucket(addedItems=addedItems, lostItems=lostItems)

def expectEqualityTwoListsAsSets(l1, l2, transformFn1=None, transformFn2=None):
    "Display differences between two lists of strings"
    result = compareTwoListsAsSets(l1, l2, transformFn1=transformFn1, transformFn2=transformFn2)
    if len(result.addedItems):
        trace('New items only in list 1:', result.addedItems)
        return False

    if len(result.lostItems):
        trace('Missing items not present in list 2:', result.lostItems)
        return False

    return True

def throwIfDuplicates(l1, transformFn1=None, context=''):
    "Detect duplicate items in a list"
    l1Transformed = l1 if not transformFn1 else [transformFn1(item) for item in l1]
    seen = {}
    for item in l1Transformed:
        if item in seen:
            raise ShineRainSevenLibError('duplicate seen:', item, context)
        
        seen[item] = True

def mergeDict(dict1, dict2):
    "Merge two dictionaries"
    return dict1 | dict2

def mergeDictIntoBucket(bucketConfigs, dictParams, allowNewKeys=False):
    "Merge a dictionary into a bucket (see the Bucket class for more)"
    validKeys = set(dir(bucketConfigs))
    for key in dictParams:
        if not allowNewKeys and not (key in validKeys and not key.startswith('_')):
            raise RuntimeError('not a supported config:', key)
        else:
            setattr(bucketConfigs, key, dictParams[key])

# endregion

# region trace helpers

def getPrintable(s, okToIgnore=False):
    "From a-with-accent to plain a, get closest visual ascii equivalent"
    if isinstance(s, bytes):
        return s.decode('ascii')
    if not isinstance(s, str):
        return str(s)

    s = _unicodedata.normalize('NFKD', s)
    if okToIgnore:
        return s.encode('ascii', 'ignore').decode('ascii')
    else:
        return s.encode('ascii', 'replace').decode('ascii')


gRedirectTraceCalls = {}
gRedirectTraceCalls['fnHook'] = None

def trace(*args, always=False):
    """Similar to print, but
    1) distinguish debugging prints vs intentional production prints
    2) can be redirected to fnHook, e.g. for testing
    3) certain terminals throw exceptions if given unicode characters"""
    val = ' '.join(map(getPrintable, args))
    if gRedirectTraceCalls['fnHook'] and not always:
        gRedirectTraceCalls['fnHook'](val)
    else:
        print(val)

def tracep(*args, always=False):
    "Similar to print, but uses pprint to pretty-print"
    val = ' '.join(map(_pprint.pformat, args))
    val = getPrintable(val)
    if gRedirectTraceCalls['fnHook'] and not always:
        gRedirectTraceCalls['fnHook'](val)
    else:
        print(val)

# endregion

class ShineRainSevenLibError(RuntimeError):
    def __init__(self, *args):
        """For exceptions in the ShineRainSevenLib layer and not lower layers.
        You can pass in more than one string"""
        combined = ' '.join(str(arg) for arg in args)
        super().__init__(combined)

