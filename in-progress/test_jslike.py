# BenPythonCommon,
# 2020 Ben Fisher, released under the LGPLv3 license.

import pytest
from .. import common_jslike as jslike
from .. import Bucket


class TestJslikeDictMethods:
    def test_compareDict(self):
        assert dict() == dict()
        assert dict(a=1, b=2) == dict(a=1, b=2)
        assert dict(b=2, a=1) == dict(a=1, b=2)
        assert dict(a=1, b=2) != dict(a=1, b=3)
        assert dict(a=1, b=2) != dict(a=1, aa=2)
        assert dict(a=1, b=2) != dict(a=1, b=2, c=3)
        assert dict(a=1, b=2) != dict(a=1)

    def test_mergedBasic(self):
        assert jslike.merged(dict(), dict()) == dict()
        assert jslike.merged(dict(a=1), dict()) == dict(a=1)
        assert jslike.merged(dict(), dict(a=1)) == dict(a=1)
        assert jslike.merged(dict(a=1), dict(a=2)) == dict(a=2)
        assert jslike.merged(dict(a=2), dict(a=1)) == dict(a=1)
        assert jslike.merged(dict(a=1), dict(a=2, b=3)) == dict(a=2, b=3)
        assert jslike.merged(dict(a=2), dict(a=1, b=3)) == dict(a=1, b=3)
        assert jslike.merged(dict(a=1, b=3), dict(a=1, b=3)) == dict(a=1, b=3)
        assert jslike.merged(dict(a=1, b=3), dict(a=4, b=5)) == dict(a=4, b=5)
        assert jslike.merged(dict(a=1, b=3), dict(a=1)) == dict(a=1, b=3)
        assert jslike.merged(dict(a=1, b=3), dict(a=2)) == dict(a=2, b=3)
        assert jslike.merged(dict(a=1, b=3), dict()) == dict(a=1, b=3)
        assert jslike.merged(dict(a=1), dict(b=3)) == dict(a=1, b=3)

    def test_mergedShouldNotModify(self):
        a = dict(a=1, b=2, c=1)
        b = dict(a=3, b=2)
        out = jslike.merged(a, b)
        assert a == dict(a=1, b=2, c=1)
        assert b == dict(a=3, b=2)
        assert out == dict(a=3, b=2, c=1)

class TestJslikeSimpleMethods:
    def test_simple(self):
        assert jslike.floatOrNone('1.2') == float('1.2')
        assert jslike.floatOrNone('-1.2') == float('-1.2')
        assert jslike.floatOrNone('ab') is None

        assert jslike.intOrNone('12') == 12
        assert jslike.intOrNone('-12') == -12
        assert jslike.intOrNone('ab') is None

    def test_span(self):
        assert 'ab12ef' == jslike.spliceSpan('abcdef', [2, 4], '12')


