

import fnmatch as _fnmatch
import inspect as _inspect
from shinerainsevenlib import srss

def doTestSrssByLines(fn, sInput, exitAfterOneFailure=True):
    "Help people write automated tests quickly by putting the tests in a string"
    from .. import core as _srss
    lines = _srss.strToList(sInput)
    failureSeen = False
    for line in lines:
        if not doTestSrss(fn, line, exitAfterOneFailure=exitAfterOneFailure):
            failureSeen = True
    
    if failureSeen:
        raise AssertionError("One or more subtest failed.")

def doTestSrss(fn, sInput, exitAfterOneFailure=True):
    "Help people write automated tests quickly by putting the tests in a string. Runs one test."
    sInput, sExpected = sInput.split('=>')
    sInput = sInput.strip() 
    sExpected = sExpected.strip()
    try:
        got = fn(sInput)
    except Exception as e:
        result = _handleExceptionHit(sInput, sExpected, e,)
    else:
        if str(got) != sInput:
            print(f"Test did not pass: input {sInput}\n expected {sExpected}\n got {got}")
            result = False
        else:
            result = True

    if exitAfterOneFailure:
        raise AssertionError("One or more subtest failed.") 
    return result

def getClassChainAsStrings(obj):
    "Show class names as strings"
    from .. import core as _srss
    chain = _inspect.getmro(obj.__class__)
    return _srss.jslike.map(chain, lambda item: repr(item).replace("<class '", '').replace("'>", ''))

def _handleExceptionHit(sInput, sExpected, e):
    if ' ' in sExpected:
        exceptionClass, expectPatternMatch = sExpected.split(' ', 1)
    else:
        exceptionClass = sExpected
        expectPatternMatch = '*' # match everything by default

    chain = getClassChainAsStrings(e)
    if exceptionClass not in chain:
        print(f"caught exception, but wrong type. Expected {exceptionClass} but got {repr(e)} (and its parents {chain})")
        print(f"context: input {sInput} expected {sExpected}")
        return False

    justMessage = str(e)
    if not _fnmatch.fnmatch(justMessage, expectPatternMatch):
        print(f"caught exception, but message does not match. Expected {justMessage} but got {expectPatternMatch}")
        print(f"context: input {sInput} expected {sExpected}")
        return False

    return True

def makeAsserts(s):
    "Generate test placeholders"
    lines = srss.strToList(s)
    for line in lines:
        print(f'assert fn("{line}") == "xxxxxx"')
