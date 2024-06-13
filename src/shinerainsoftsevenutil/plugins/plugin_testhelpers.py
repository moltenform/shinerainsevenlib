

import fnmatch as _fnmatch
import inspect as _inspect

def doTestSrssByLines(fn, sInput, exitAfterOneFailure=True):
    from .. import core as _srss
    lines = _srss.strToList(sInput)
    failureSeen = False
    for line in lines:
        if not doTestSrss(fn, line, exitAfterOneFailure=exitAfterOneFailure):
            failureSeen = True
    
    if failureSeen:
        raise AssertionError("One or more subtest failed.")

def doTestSrss(fn, sInput, exitAfterOneFailure=True):
    sInput, sExpected = sInput.split('=>')
    sInput = sInput.strip() 
    sExpected = sExpected.strip()
    try:
        got = fn(sInput)
    except Exception as e:
        result = handleExceptionHit(sInput, sExpected, e,)
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
    from .. import core as _srss
    chain = _inspect.getmro(obj.__class__)
    return _srss.jslike.map(chain, lambda item: repr(item).replace("<class '", '').replace("'>", ''))

def handleExceptionHit(sInput, sExpected, e):
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
    from shinerainsoftsevenutil.standard import srss
    lines = srss.strToList(s)
    for line in lines:
        print(f'assert fn("{line}") == "xxxxxx"')

if __name__ == '__main__':
    pass
    makeAsserts(r'''
test(tbz).tar.bz2
test(tgz).tar.gz
test(txz).tar.xz
test_7z.7z
test_rar_nosolid_nostore.rar
test_rar_nosolid_store.rar
test_rar_solid_nostore.rar
test_zip_made_with_7z.zip
test_zip_made_with_7z_store.zip
test_zip_made_with_py_default.zip
test_zip_made_with_py_lzma.zip
test_zip_made_with_winrar.zip
unicode.7z
unicode.rar
unicode.zip
                ''')

