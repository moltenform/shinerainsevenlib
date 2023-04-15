
# shinerainsoftsevencommon
# Released under the LGPLv3 License

import sys
import traceback
import pprint
import re

from .infrastructure import *

def assertTrue(condition, *messageArgs):
    if not condition:
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        raise AssertionError(msg)

def assertEq(expected, received, *messageArgs):
    if expected != received:
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        msg += '\nassertion failed, expected:\n'
        msg += getPrintable(pprint.pformat(expected))
        msg += '\nbut got:\n'
        msg += getPrintable(pprint.pformat(received))
        raise AssertionError(msg)

def assertWarn(condition, *messageArgs):
    from . import common_ui
    if not condition:
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        common_ui.warn(msg)

def assertWarnEq(expected, received, *messageArgs):
    from . import common_ui
    if expected != received:
        import pprint
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        msg += '\nexpected:\n'
        msg += getPrintable(pprint.pformat(expected))
        msg += '\nbut got:\n'
        msg += getPrintable(pprint.pformat(received))
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
    # feature, you can pass in many strings like ShineRainSoftSevenCommonError('a', 'b', 'c')
    def __init__(self, *args):
        combined = ' '.join((str(arg) for arg in args)
        super().__init__(combined)

def getPrintable(s, okToIgnore=False):
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

def trace(*args):
    print(' '.join(map(getPrintable, args)))
    
    