

# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from tests.test_core.common import fixture_dir, fixture_dir_with_many
from collections import OrderedDict
import os
import sys
import shutil
from src.shinerainsevenlib.files import *

class TestSimpleWrappers:
    def test(self):
        assert files.rename is os.rename
        assert files.exists is os.path.exists
        assert files.join is os.path.join
        assert files.split is os.path.split
        assert files.isDir is os.path.isdir
        assert files.isFile is os.path.isfile
        assert files.getSize is os.path.getsize
        assert files.rmDir is os.rmdir
        assert files.chDir is os.chdir
        assert files.sep is os.path.sep
        assert files.lineSep is os.linesep
        assert files.absPath is os.path.abspath
        assert files.rmTree is shutil.rmtree


class TestGetName:
    def test_getParent(self):
        assert '/path/to' == getParent('/path/to/file')

    def test_getName(self):
        assert 'file' == getName('/path/to/file')

class TestExtensionsRelated:
    def test_getExt(self):
        # corner cases
        assert '' == getExt('/path/to/')
        assert '' == getExt('/path/to/..')
        assert '' == getExt('/path/to/file')
        assert '' == getExt('/path/to/file.')
        assert 'txt' == getExt('/path/to/file.txt')
        assert 'txt' == getExt('/path/to/file.other.txt')
        assert '' == getExt('/path/to/.txt')

        # remove dot on different extension lengths
        assert 'a' == getExt('/path/to/file.a')
        assert 'ab' == getExt('/path/to/file.ab')
        assert 'abcde' == getExt('/path/to/file.abcde')

        # make lowercase
        assert 'txt' == getExt('/path/to/file.TXT')
        assert 'txt' == getExt('/path/to/file.TxT')
        assert 'txt' == getExt('/path/to/file.tXt')

        # include dot
        assert '.a' == getExt('/path/to/file.a', removeDot=False)
        assert '.txt' == getExt('/path/to/file.txt', removeDot=False)

        # ones-to-preserve
        assert 'jpg' == getExt('/path/a.jpg', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert 'jxl' == getExt('/path/a.jxl', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert 'jxl' == getExt('/path/a.b.jxl', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert 'l.jxl' == getExt('/path/a.l.jxl', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert 'j.jxl' == getExt('/path/a.j.jxl', onesToPreserve=['.l.jxl', '.j.jxl'])

    def test_splitExt(self):
        # basic
        assert splitExt('/path/a.txt') == ('/path/a', '.txt')
        assert splitExt('/path/.txt') == ('/path/.txt', '')

        # relative paths
        assert splitExt('./a.txt') == ('./a', '.txt')
        assert splitExt('./.txt') == ('./.txt', '')
        assert splitExt('a.txt') == ('a', '.txt')
        assert splitExt('.txt') == ('.txt', '')

        # with no dot
        assert splitExt('./abc') == ('./abc', '')
        if sys.platform.startswith('win'):
            assert splitExt('.\\abc') == ('.\\abc', '')

        # ones-to-preserve
        assert splitExt('/path/a.jpg', onesToPreserve=['.l.jxl', '.j.jxl']) == ('/path/a', '.jpg')
        assert splitExt('/path/a.jxl', onesToPreserve=['.l.jxl', '.j.jxl']) == ('/path/a', '.jxl')
        assert splitExt('/path/a.b.jxl', onesToPreserve=['.l.jxl', '.j.jxl']) == ('/path/a.b', '.jxl')
        assert splitExt('/path/a.l.jxl', onesToPreserve=['.l.jxl', '.j.jxl']) == ('/path/a', '.l.jxl')
        assert splitExt('/path/a.j.jxl', onesToPreserve=['.l.jxl', '.j.jxl']) == ('/path/a', '.j.jxl')


class TestGetAltered:
    def test_getWithDifferentExt(self):
        assert '/path/to/file.new' == getWithDifferentExt('/path/to/file.tXt', '.new')
        assert './path/to/file.new' == getWithDifferentExt('./path/to/file.tXt', '.new')
        assert 'file.new' == getWithDifferentExt('file.tXt', '.new')

    def test_getWithDifferentExtRequiresExtension(self):
        with pytest.raises(AssertionError):
            getWithDifferentExt('/path/to/file_no_ext', '.new')

        with pytest.raises(AssertionError):
            getWithDifferentExt('./file_no_ext', '.new')

        with pytest.raises(AssertionError):
            getWithDifferentExt('file_no_ext', '.new')
    
    def test_withOnesToPreserve(self):
        assert '/path/a.other' == getWithDifferentExt('/path/a.jpg', '.other', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert '/path/a.other' == getWithDifferentExt('/path/a.jpg', '.other', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert '/path/a.other' == getWithDifferentExt('/path/a.jxl', '.other', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert '/path/a.b.other' == getWithDifferentExt('/path/a.b.jxl', '.other', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert '/path/a.other' == getWithDifferentExt('/path/a.j.jxl', '.other', onesToPreserve=['.l.jxl', '.j.jxl'])
        assert '/path/a.other' == getWithDifferentExt('/path/a.l.jxl', '.other', onesToPreserve=['.l.jxl', '.j.jxl'])

    def test_getAcross(self):
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


class TestDelete:
    def test(self, fixture_dir_with_many):
        # file
        assert os.path.isfile(fixture_dir_with_many + '/foobar/a/foobar/c/c0.txt')
        delete(fixture_dir_with_many + '/foobar/a/foobar/c/c0.txt')
        assert not os.path.isfile(fixture_dir_with_many + '/foobar/a/foobar/c/c0.txt')

        # non existing file
        assert not os.path.isfile(fixture_dir_with_many + '/notexist.txt')
        delete(fixture_dir_with_many + '/notexist.txt')
        assert not os.path.isfile(fixture_dir_with_many + '/notexist.txt')

        # cannot delete directories
        assert os.path.isdir(fixture_dir_with_many + '/foobar/a/foobar')
        with pytest.raises(PermissionError):
            delete(fixture_dir_with_many + '/foobar/a/foobar')

        # trace
        assert not os.path.isfile(fixture_dir_with_many + '/notexist.txt')
        delete(fixture_dir_with_many + '/notexist.txt', doTrace=True)
        assert not os.path.isfile(fixture_dir_with_many + '/notexist.txt')

        # file while lock is held
        if sys.platform.startswith("win"):
            with open(fixture_dir_with_many + '/foobar/a/foobar/c/c0.txt', 'w') as f:
                assert os.path.isfile(fixture_dir_with_many + '/foobar/a/foobar/c/c0.txt')
                with pytest.raises(PermissionError):
                    delete(fixture_dir_with_many + '/foobar/a/foobar/c/c0.txt')
            

class TestGetModTime:
    @pytest.mark.skipif('not isPy3OrNewer')
    def test_modtimeRendered(self, fixture_dir):
        files.writeAll(join(fixture_dir, 'a.txt'), 'contents')
        curtimeWritten = files.getLastModTime(join(fixture_dir, 'a.txt'), files.TimeUnits.Milliseconds)
        curtimeNow = getNowAsMillisTime()

        # we expect it to be at least within 1 day
        dayMilliseconds = 24 * 60 * 60 * 1000
        assert abs(curtimeWritten - curtimeNow) < dayMilliseconds

        # so we expect at least the date to match
        nCharsInDate = 10
        scurtimeWritten = renderMillisTime(curtimeWritten)
        scurtimeNow = renderMillisTime(curtimeNow)
        assert scurtimeWritten[0:nCharsInDate] == scurtimeNow[0:nCharsInDate]

    
