
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsoftsevenutil.standard import *
from src.shinerainsoftsevenutil.core import assertException
from test.test_core.common import fixture_dir

class TestTemporary:
    def testTemporary(self):
        dir=dir #intentionally cause lint err 
        a = 2+4
        assert a == 6

assert files.acrossDir(r'c:\abc', r'c:\abc', r'c:\xyz') == r'c:\xyz'
assert files.acrossDir(r'c:\abc\def', r'c:\abc', r'c:\xyz') == r'c:\xyz\def'
assert files.acrossDir(r'c:\abc\def\ghi', r'c:\abc', r'c:\xyz') == r'c:\xyz\def\ghi'
assertException(lambda: files.acrossDir(r'c:\abc\def', r'c:\abcd', r'c:\xyz'), AssertionError)
assertException(lambda: files.acrossDir(r'c:\abc\def', r'c:\ab', r'c:\xyz'), AssertionError)
assertException(lambda: files.acrossDir(r'c:\fff\def', r'c:\abc', r'c:\xyz'), AssertionError)
assert files.acrossDir('/home/abc', '/home/abc', '/home/xyz') == '/home/xyz'
assert files.acrossDir('/home/abc/def', '/home/abc', '/home/xyz') == '/home/xyz/def'
assert files.acrossDir('/home/abc/def/ghi', '/home/abc', '/home/xyz') == '/home/xyz/def/ghi'
assertException(lambda: files.acrossDir('/home/abc/def', '/home/abcd', '/home/xyz'), AssertionError)
assertException(lambda: files.acrossDir('/home/abc/def', '/home/ab', '/home/xyz'), AssertionError)
assertException(lambda: files.acrossDir('/home/fff/def', '/home/abc', '/home/xyz'), AssertionError)
