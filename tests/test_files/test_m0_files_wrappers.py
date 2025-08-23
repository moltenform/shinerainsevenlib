

# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from tests.test_core.common import fxDirPlain, fxTreePlain, fxFilesPlain, fxTree, fxFiles
from collections import OrderedDict
import os
import sys
import shutil
import time
from src.shinerainsevenlib.files import *
from src.shinerainsevenlib.files import m2_files_higher
from unittest.mock import patch


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

class TestSimpleWrappers:
    def test(self):
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

class TestMakeDirs:
    def test(self, fxDirPlain):
        # one-deep
        assert not isDir(join(fxDirPlain, 'd'))
        makeDirs(join(fxDirPlain, 'd'))
        assert isDir(join(fxDirPlain, 'd'))

        # two-deep
        assert not isDir(join(fxDirPlain, 'd1', 'd2'))
        makeDirs(join(fxDirPlain, 'd1', 'd2'))
        assert isDir(join(fxDirPlain, 'd1', 'd2'))

        # ok if already exists
        makeDirs(join(fxDirPlain, 'd1', 'd2'))
        assert isDir(join(fxDirPlain, 'd1', 'd2'))

        # invalid path
        with pytest.raises(OSError):
            makeDirs('?' if sys.platform.startswith("win") else '')
        
        # exists as file
        files.writeAll(join(fxDirPlain, 'a.txt'), 'abc')
        with pytest.raises(OSError):
            makeDirs(join(fxDirPlain, 'a.txt'))

class TestDelete:
    def testDelete(self, fxTree):
        self.runDeleteTests(files.delete, fxTree)
    
    def testDeleteSure(self, fxTree):
        self.runDeleteTests(files.deleteSure, fxTree)
    
    def runDeleteTests(self, fnDelete, fxTree):
        # file
        assert os.path.isfile(fxTree.pathFileExists)
        fnDelete(fxTree.pathFileExists)
        assert not os.path.isfile(fxTree.pathFileExists)

        # non existing file
        assert not os.path.isfile(fxTree.pathNotExist)
        fnDelete(fxTree.pathNotExist)
        assert not os.path.isfile(fxTree.pathNotExist)

        # cannot fnDelete directories
        assert os.path.isdir(fxTree.pathDir)
        with pytest.raises(Exception):
            fnDelete(fxTree.pathDir)

        # trace
        assert not os.path.isfile(fxTree.pathNotExist)
        fnDelete(fxTree.pathNotExist, doTrace=True)
        assert not os.path.isfile(fxTree.pathNotExist)

        # file while lock is held
        if sys.platform.startswith("win"):
            with open(fxTree.pathFileToLock, 'w') as f:
                assert os.path.isfile(fxTree.pathFileToLock)
                with pytest.raises(PermissionError):
                    fnDelete(fxTree.pathFileToLock)



class TestEnsureEmptyDir:
    def test(self, fxTree):
        # doesn't need recursion
        assert self.hasSubfiles(fxTree.pathFewChildren)
        assert not self.hasSubdirs(fxTree.pathFewChildren)
        ensureEmptyDirectory(fxTree.pathFewChildren)
        assert isEmptyDir(fxTree.pathFewChildren)
        assert not self.hasSubdirs(fxTree.pathFewChildren) and not self.hasSubfiles(fxTree.pathFewChildren)

        # already empty
        pathAlreadyEmpty = fxTree.pathFewChildren
        assert isEmptyDir(pathAlreadyEmpty)
        ensureEmptyDirectory(pathAlreadyEmpty)
        assert isEmptyDir(pathAlreadyEmpty)

        # with both subdirs and subdir files
        assert not isEmptyDir(fxTree.pathManyChildren)
        assert self.hasSubdirs(fxTree.pathManyChildren) and self.hasSubfiles(fxTree.pathManyChildren)
        ensureEmptyDirectory(fxTree.pathManyChildren)
        assert isEmptyDir(fxTree.pathManyChildren)
        assert not self.hasSubdirs(fxTree.pathManyChildren) and not self.hasSubfiles(fxTree.pathManyChildren)
    
        # can't delete a file
        assert isFile(fxTree.pathSmallFile)
        with pytest.raises(Exception):
            ensureEmptyDirectory(fxTree.pathSmallFile)

        # does not exist (will be created)
        assert not isDir(fxTree.pathDirNotExist)
        ensureEmptyDirectory(fxTree.pathDirNotExist)
        assert isDir(fxTree.pathDirNotExist)
        assert isEmptyDir(fxTree.pathDirNotExist)

    def hasSubdirs(self, d):
        return len(list(listChildren(d, includeFiles=False, includeDirs=True)))
    
    def hasSubfiles(self, d):
        return len(list(listChildren(d, includeFiles=True, includeDirs=False)))

class TestCopy:
    def test_overWriteMode_srcNotExist(self, fxFiles):
        with pytest.raises(IOError):
            copy(fxFiles.f1 + '.notexist', fxFiles.f2, True)
        
    def test_overWriteMode_noOverwrite(self, fxFiles):
        assert not exists(fxFiles.f3notExistYet)
        copy(fxFiles.f1, fxFiles.f3notExistYet, True)
        assert exists(fxFiles.f3notExistYet)
        assert '1\u1101' == readAll(fxFiles.f3notExistYet)

    def test_overWriteMode_overwrite(self, fxFiles):
        # check contents before
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)
        
        # replace a file
        assert exists(fxFiles.f2)
        copy(fxFiles.f1, fxFiles.f2, True)
        assert exists(fxFiles.f2)

        # check contents after
        # (in py2, check correctness for nonascii paths+contents)
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '1\u1101' == readAll(fxFiles.f2)

    def test_overWriteModeOff_srcNotExist(self, fxFiles):
        with pytest.raises(IOError):
            copy(fxFiles.f1 + '.notexist', fxFiles.f2, False)
        
    def test_overWriteModeOff_noOverwrite(self, fxFiles):
        assert not exists(fxFiles.f3notExistYet)
        copy(fxFiles.f1, fxFiles.f3notExistYet, False)
        assert exists(fxFiles.f3notExistYet)
        assert '1\u1101' == readAll(fxFiles.f3notExistYet)

    def test_overWriteModeOff_overwrite(self, fxFiles):
        # check contents before
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)
        
        # replace a file (fails)
        assert exists(fxFiles.f2)
        with pytest.raises(IOError):
            copy(fxFiles.f1, fxFiles.f2, False)

        # check contents after
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)
    
    def test_trace(self, fxFiles):
        assert not exists(fxFiles.f3notExistYet)
        copy(fxFiles.f1, fxFiles.f3notExistYet, False, doTrace=True, traceOnly=True)
        assert not exists(fxFiles.f3notExistYet)
        
        assert not exists(fxFiles.f3notExistYet)
        copy(fxFiles.f1, fxFiles.f3notExistYet, False, doTrace=True)
        assert exists(fxFiles.f3notExistYet)
        assert '1\u1101' == readAll(fxFiles.f3notExistYet)

    def test_allowDirs(self, fxFiles):
        with pytest.raises(OSFileRelatedError):
            copy(fxFiles.basedir, fxFiles.basedir + '2', False)
    
    def test_skipSame(self, fxFiles):
        contents = readAll(fxFiles.f1)
        copy(fxFiles.f1, fxFiles.f1, True)
        assert contents == readAll(fxFiles.f1)
    
    def test_autoCreateParent(self, fxTree):
        with pytest.raises(OSFileRelatedError):
            copy(fxTree.pathFileExists, fxTree.basedir + '/newdir/a.txt', False)
        
        assert not exists(fxTree.basedir + '/newdir/a.txt')
        
        copy(fxTree.pathFileExists, fxTree.basedir + '/newdir/a.txt', False, createParent=True)
        assert readAll(fxTree.pathFileExists) == readAll(fxTree.basedir + '/newdir/a.txt')
    
    def test_keepSameModifiedTime(self, fxFiles):
        # check contents before
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)

        files.setLastModTime(fxFiles.f2, 1754712000)
        
        # replace a file
        assert exists(fxFiles.f2)
        copy(fxFiles.f1, fxFiles.f2, True, keepSameModifiedTime=True)
        assert exists(fxFiles.f2)

        assert files.getLastModTime(fxFiles.f2) == pytest.approx(1754712000, abs=10)

class TestMove:
    def test_overWriteMode_srcNotExist(self, fxFiles):
        with pytest.raises(IOError):
            move(fxFiles.f1 + '.notexist', fxFiles.f2, True)
        
    def test_overWriteMode_noOverwrite(self, fxFiles):
        assert exists(fxFiles.f1)
        assert not exists(fxFiles.f3notExistYet)
        move(fxFiles.f1, fxFiles.f3notExistYet, True)
        assert exists(fxFiles.f3notExistYet)
        assert not exists(fxFiles.f1)
        assert '1\u1101' == readAll(fxFiles.f3notExistYet)

    def test_overWriteMode_overwrite(self, fxFiles):
        # check contents before
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)
        
        # replace a file
        assert exists(fxFiles.f1)
        assert exists(fxFiles.f2)
        move(fxFiles.f1, fxFiles.f2, True)
        assert not exists(fxFiles.f1)
        assert exists(fxFiles.f2)

        # check contents after
        # (in py2, check correctness for nonascii paths+contents)
        assert '1\u1101' == readAll(fxFiles.f2)

    def test_overWriteModeOff_srcNotExist(self, fxFiles):
        with pytest.raises(IOError):
            move(fxFiles.f1 + '.notexist', fxFiles.f2, False)
        
    def test_overWriteModeOff_noOverwrite(self, fxFiles):
        assert exists(fxFiles.f1)
        assert not exists(fxFiles.f3notExistYet)
        move(fxFiles.f1, fxFiles.f3notExistYet, False)
        assert not exists(fxFiles.f1)
        assert exists(fxFiles.f3notExistYet)
        assert '1\u1101' == readAll(fxFiles.f3notExistYet)

    def test_overWriteModeOff_overwrite(self, fxFiles):
        # check contents before
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)
        
        # replace a file (fails)
        assert exists(fxFiles.f2)
        with pytest.raises(IOError):
            move(fxFiles.f1, fxFiles.f2, False)

        # check contents after
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)
    
    def test_trace(self, fxFiles):
        assert exists(fxFiles.f1)
        assert not exists(fxFiles.f3notExistYet)
        move(fxFiles.f1, fxFiles.f3notExistYet, False, doTrace=True, traceOnly=True)
        assert exists(fxFiles.f1)
        assert not exists(fxFiles.f3notExistYet)
        
        assert not exists(fxFiles.f3notExistYet)
        move(fxFiles.f1, fxFiles.f3notExistYet, False, doTrace=True)
        assert exists(fxFiles.f3notExistYet)
        assert not exists(fxFiles.f1)
        assert '1\u1101' == readAll(fxFiles.f3notExistYet)

    def test_allowDirs(self, fxFiles):
        with pytest.raises(OSFileRelatedError):
            move(fxFiles.basedir, fxFiles.basedir + '2', False)
    
    def test_skipSame(self, fxFiles):
        contents = readAll(fxFiles.f1)
        move(fxFiles.f1, fxFiles.f1, True)
        assert contents == readAll(fxFiles.f1)
    
    def test_autoCreateParent(self, fxTree):
        with pytest.raises(OSFileRelatedError):
            move(fxTree.pathFileExists, fxTree.basedir + '/newdir/a.txt', False)
        
        assert exists(fxTree.pathFileExists)
        assert not exists(fxTree.basedir + '/newdir/a.txt')
        
        contents = readAll(fxTree.pathFileExists)
        move(fxTree.pathFileExists, fxTree.basedir + '/newdir/a.txt', False, createParent=True)
        assert contents == readAll(fxTree.basedir + '/newdir/a.txt')
        assert not exists(fxTree.pathFileExists)
    
class TestPosixSpecificCopy:
    @patch('sys.platform', 'linux')
    def test_overWriteFile(self, fxFiles):
        # replace a file
        copy(fxFiles.f1, fxFiles.f2, True)

        # check contents after
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '1\u1101' == readAll(fxFiles.f2)

    @patch('sys.platform', 'linux')
    def test_overWriteFileBlocked(self, fxFiles):
        with pytest.raises(OSError):
            copy(fxFiles.f1, fxFiles.f2, False)
    
    @patch('sys.platform', 'linux')
    def test_overWriteCapableButNotNeeded(self, fxFiles):
        copy(fxFiles.f1, fxFiles.f2 + '.new', False)
        assert '1\u1101' == readAll(fxFiles.f2 + '.new')

    @patch('sys.platform', 'linux')
    def test_overWriteCapableButNotNeededBigFile(self, fxFiles):
        # test with a large file to make the loop happen
        oneMbOfAs = 'a' * 1024 * 1024
        files.writeAll(fxFiles.f1, oneMbOfAs)
        copy(fxFiles.f1, fxFiles.f2 + '.new', False)
        assert oneMbOfAs == readAll(fxFiles.f2 + '.new')

class TestPosixSpecificMove:
    @patch('sys.platform', 'linux')
    def test_couldOverWriteFile(self, fxFiles):
        # replace a file
        move(fxFiles.f1, fxFiles.f2 + '.new', True)

        # check contents after
        assert not exists(fxFiles.f1)
        assert '1\u1101' == readAll(fxFiles.f2 + '.new')

    @patch('sys.platform', 'linux')
    def test_overWriteFile(self, fxFiles):
        # replace a file
        move(fxFiles.f1, fxFiles.f2, True)

        # check contents after
        assert not exists(fxFiles.f1)
        assert '1\u1101' == readAll(fxFiles.f2)
    
    @patch('sys.platform', 'linux')
    def test_mvWithNoNoClobber(self, fxFiles, mocker):
        def simulateMvWithNoOption(args, **kwargs):
            assert args[0] == 'mv'
            if '--no-clobber' in args:
                raise OSError('no option')
            else:
                raise AssertionError('Not reached')

        files.m0_files_wrappers.confirmedMvOpts = None
        mocker.patch('src.shinerainsevenlib.files.m2_files_higher.run', side_effect=simulateMvWithNoOption)
        with pytest.raises(Exception, match='failed to run no-clobber test'):
            move(fxFiles.f1, fxFiles.f2, False)

        assert 'failed to run no-clobber test' in files.m0_files_wrappers.confirmedMvOpts
        
        # nothing should have changed, bc exception
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)
    
    @patch('sys.platform', 'linux')
    def test_mvHasNoClobberOptionButDoesTheWrongThing(self, fxFiles, mocker):
        def simulateMvThatAlwaysClobbers(args, **kwargs):
            assert args[0] == 'mv'
            assert args[1] == '--no-clobber'
            assert exists(args[2])
            assert exists(args[3])
            files.delete(args[3])
            shutil.copy(args[2], args[3])
            files.delete(args[2])

        files.m0_files_wrappers.confirmedMvOpts = None
        mocker.patch('src.shinerainsevenlib.files.m2_files_higher.run', side_effect=simulateMvThatAlwaysClobbers)
        with pytest.raises(Exception, match='mv still overwrote'):
            move(fxFiles.f1, fxFiles.f2, False)

        assert 'mv still overwrote' in files.m0_files_wrappers.confirmedMvOpts

        # nothing should have changed, bc exception
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)

    @patch('sys.platform', 'linux')
    def test_mvThatWorksAsExpected(self, fxFiles, mocker):
        def simulateMvAsExpected(args, **kwargs):
            assert args[0] == 'mv'
            assert args[1] == '--no-clobber'
            assert exists(args[2])
            if exists(args[3]):
                return 0
            else:
                shutil.move(args[2], args[3])

        files.m0_files_wrappers.confirmedMvOpts = None
        mocker.patch('src.shinerainsevenlib.files.m2_files_higher.run', side_effect=simulateMvAsExpected)
        move(fxFiles.f1, fxFiles.f2, False)

        assert files.m0_files_wrappers.confirmedMvOpts is True

        # nothing should have changed, because overwrite=False
        assert '1\u1101' == readAll(fxFiles.f1)
        assert '2\u1101' == readAll(fxFiles.f2)



class TestGetModTime:
    @pytest.mark.skipif('not isPy3OrNewer')
    def test_modtimeRendered(self, fxDirPlain):
        files.writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        curtimeWritten = files.getLastModTime(join(fxDirPlain, 'a.txt'), files.TimeUnits.Milliseconds)
        curtimeNow = getNowAsMillisTime()

        # we expect it to be at least within 1 day
        dayMilliseconds = 24 * 60 * 60 * 1000
        assert curtimeWritten == pytest.approx(curtimeNow, abs=dayMilliseconds)

        # so we expect at least the date to match
        nCharsInDate = 10
        scurtimeWritten = renderMillisTime(curtimeWritten)
        scurtimeNow = renderMillisTime(curtimeNow)
        assert scurtimeWritten[0:nCharsInDate] == scurtimeNow[0:nCharsInDate]
    
    def test_modtimeWithInvalidUnits(self, fxDirPlain):
        files.writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        tm = files.getLastModTime(join(fxDirPlain, 'a.txt'), files.TimeUnits.Seconds)
        with pytest.raises(ValueError):
            files.getLastModTime(join(fxDirPlain, 'a.txt'), 'Days')
        
        files.setLastModTime(join(fxDirPlain, 'a.txt'), tm, files.TimeUnits.Seconds)
        with pytest.raises(ValueError):
            files.setLastModTime(join(fxDirPlain, 'a.txt'), tm, 'Days')
    
    def test_getModtimeWithDifferentUnits(self, fxTree):
        files.writeAll(fxTree.pathSmallFile, 'contents')
        tmS = files.getLastModTime(fxTree.pathSmallFile, files.TimeUnits.Seconds)
        tmMs = files.getLastModTime(fxTree.pathSmallFile, files.TimeUnits.Milliseconds)
        tmNs = files.getLastModTime(fxTree.pathSmallFile, files.TimeUnits.Nanoseconds)
        assert tmMs == pytest.approx(tmS * 1000, rel=0.1)
        assert tmNs == pytest.approx(tmS * 1.0e9, rel=0.1)
    
    def test_setModtimeWithDifferentUnits(self, fxTree):
        files.writeAll(fxTree.pathSmallFile, 'contents')
        tmBase = files.getLastModTime(fxTree.pathSmallFile, files.TimeUnits.Seconds)
        tmBase -= 555

        files.setLastModTime(fxTree.pathSmallFile, tmBase, files.TimeUnits.Seconds)
        assert files.getLastModTime(fxTree.pathSmallFile) == pytest.approx(tmBase, rel=0.1)
        files.setLastModTime(fxTree.pathSmallFile, tmBase*1000, files.TimeUnits.Milliseconds)
        assert files.getLastModTime(fxTree.pathSmallFile) == pytest.approx(tmBase, rel=0.1)
        files.setLastModTime(fxTree.pathSmallFile, tmBase*1.0e9, files.TimeUnits.Nanoseconds)
        assert files.getLastModTime(fxTree.pathSmallFile) == pytest.approx(tmBase, rel=0.1)

    def test_modtimeChanges(self, fxFiles):
        tmBase = files.getLastModTime(fxFiles.f1, files.TimeUnits.Milliseconds)
        time.sleep(2)
        files.writeAll(fxFiles.f1, 'change')
        tmNew = files.getLastModTime(fxFiles.f1, files.TimeUnits.Milliseconds)
        assert tmNew > tmBase


class TestFilesEqual:
    def testSameContentAndSameTimes(self, fxTree):
        files.writeAll(fxTree.pathSmallFile, 'contents')
        files.writeAll(fxTree.pathExample, 'contents')
        tm = files.getLastModTime(fxTree.pathExample)
        files.setLastModTime(fxTree.pathSmallFile, tm)
        files.setLastModTime(fxTree.pathExample, tm)
        assert files.fileContentsEqual(fxTree.pathSmallFile, fxTree.pathExample)

    def testSameContentAndDifferentTimes(self, fxTree):
        files.writeAll(fxTree.pathSmallFile, 'contents')
        files.writeAll(fxTree.pathExample, 'contents')
        tm = files.getLastModTime(fxTree.pathExample)
        files.setLastModTime(fxTree.pathSmallFile, tm)
        files.setLastModTime(fxTree.pathExample, tm - 10)
        assert files.fileContentsEqual(fxTree.pathSmallFile, fxTree.pathExample)

    def testDiffContentAndSameTimes(self, fxTree):
        files.writeAll(fxTree.pathSmallFile, 'contents')
        files.writeAll(fxTree.pathExample, 'contentS')
        tm = files.getLastModTime(fxTree.pathExample)
        files.setLastModTime(fxTree.pathSmallFile, tm)
        files.setLastModTime(fxTree.pathExample, tm)
        assert not files.fileContentsEqual(fxTree.pathSmallFile, fxTree.pathExample)

    def testDiffContentAndDiffTimes(self, fxTree):
        files.writeAll(fxTree.pathSmallFile, 'contents')
        files.writeAll(fxTree.pathExample, 'contentS')
        tm = files.getLastModTime(fxTree.pathExample)
        files.setLastModTime(fxTree.pathSmallFile, tm)
        files.setLastModTime(fxTree.pathExample, tm - 10)
        assert not files.fileContentsEqual(fxTree.pathSmallFile, fxTree.pathExample)

class TestWriteFiles:
    def test_readAndWriteSimple(self, fxDirPlain):
        ret = writeAll(join(fxDirPlain, 'a.txt'), 'abc', mode='w')
        assert ret is True
        assert u'abc' == readAll(join(fxDirPlain, 'a.txt'), 'r')
        ret = writeAll(join(fxDirPlain, 'a.txt'), 'def', mode='w')
        assert ret is True
        assert u'def' == readAll(join(fxDirPlain, 'a.txt'), 'r')

    def test_readAndWriteUtf8(self, fxDirPlain):
        path = join(fxDirPlain, u'a\u1E31.txt')
        kwargs = dict(encoding='utf-8') if isPy3OrNewer else dict(unicodetype='utf-8')
        ret = writeAll(path, u'\u1E31\u1E77\u1E53\u006E', **kwargs)
        assert ret is True
        assert u'\u1E31\u1E77\u1E53\u006E' == readAll(path, **kwargs)

    def test_readAndWriteUtf16(self, fxDirPlain):
        path = join(fxDirPlain, u'a\u1E31.txt')
        kwargs = dict(encoding='utf-16le') if isPy3OrNewer else dict(unicodetype='utf-16le')
        ret = writeAll(path, u'\u1E31\u1E77\u1E53\u006E', **kwargs)
        assert ret is True
        assert u'\u1E31\u1E77\u1E53\u006E' == readAll(path, **kwargs)

    def test_writeAllUnlessThereNewFile(self, fxDirPlain):
        path = join(fxDirPlain, 'a.dat')
        ret = writeAll(path, b'abc', mode='wb', skipIfSameContent=True)
        assert ret is True
        assert b'abc' == readAll(path, 'rb')

    def test_writeAllUnlessThereChangedFile(self, fxDirPlain):
        path = join(fxDirPlain, 'a.dat')
        writeAll(path, b'abcd', 'wb')
        ret = writeAll(path, b'abc', mode='wb', skipIfSameContent=True)
        assert ret is True
        assert b'abc' == readAll(path, 'rb')

    def test_writeAllUnlessThereSameFile(self, fxDirPlain):
        path = join(fxDirPlain, 'a.dat')
        writeAll(path, b'abc', 'wb')
        ret = writeAll(path, b'abc', mode='wb', skipIfSameContent=True)
        assert ret is False
        assert b'abc' == readAll(path, 'rb')

    def test_writeAllUnlessThereNewTxtFile(self, fxDirPlain):
        path = join(fxDirPlain, 'a.txt')
        ret = writeAll(path, 'abc', mode='w', skipIfSameContent=True)
        assert ret is True
        assert 'abc' == readAll(path)

    def test_writeAllUnlessThereChangedTxtFile(self, fxDirPlain):
        path = join(fxDirPlain, 'a.txt')
        writeAll(path, 'abcd')
        ret = writeAll(path, 'abc', mode='w', skipIfSameContent=True)
        assert ret is True
        assert 'abc' == readAll(path)

    def test_writeAllUnlessThereSameTxtFile(self, fxDirPlain):
        path = join(fxDirPlain, 'a.txt')
        writeAll(path, 'abc')
        ret = writeAll(path, 'abc', mode='w', skipIfSameContent=True)
        assert ret is False
        assert 'abc' == readAll(path)

    def test_updateTimeIfSameContent(self, fxDirPlain):
        path = join(fxDirPlain, 'a.txt')
        writeAll(path, 'abc')
        setLastModTime(path, 1754712000, units=TimeUnits.Seconds)
        ret = writeAll(path, 'abc', mode='w', skipIfSameContent=True, updateTimeIfSameContent=True)
        assert ret is False
        assert 'abc' == readAll(path)
        assert getLastModTime(path, units=TimeUnits.Seconds ) != pytest.approx(1754712000, abs=5)

