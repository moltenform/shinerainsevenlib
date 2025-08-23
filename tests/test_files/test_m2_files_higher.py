# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from tests.test_core.common import fxDirPlain, fxTreePlain, fxFilesPlain
from collections import OrderedDict
import os
import sys
import time
from src.shinerainsevenlib.files import *
import webbrowser

class TestOpenUrl:
    def test_basic(self, mocker):
        mocker.patch('webbrowser.open')
        openUrl('https://example.com')
        webbrowser.open.assert_called_once_with('https://example.com', new=2)
    
    def test_basicHttp(self, mocker):
        mocker.patch('webbrowser.open')
        openUrl('http://example.com')
        webbrowser.open.assert_called_once_with('http://example.com', new=2)
    
    def test_blocked(self):
        with pytest.raises(AssertionError):
            openUrl('file:///example.com')
        with pytest.raises(AssertionError):
            openUrl('example.com')
        with pytest.raises(AssertionError):
            openUrl('www.example.com')

    def test_escape(self, mocker):
        mocker.patch('webbrowser.open')
        openUrl('https://example.com a&b')
        webbrowser.open.assert_called_once_with('https://example.com%20a%26b', new=2)
    
    def test_escapeAndQuotes(self, mocker):
        mocker.patch('webbrowser.open')
        openUrl('''http://example.com " ' \\ ''')
        webbrowser.open.assert_called_once_with('http://example.com%20%22%20%27%20%5C%20', new=2)

class TestM3FilesHigher:
    def testFindBinaryOnPath(self, fxDirPlain):
        writeAll(f'{fxDirPlain}/a.out', ' ')
        writeAll(f'{fxDirPlain}/a.exe', ' ')
        writeAll(f'{fxDirPlain}/b.bat', ' ')
        writeAll(f'{fxDirPlain}/c', ' ')
        os.chdir(fxDirPlain)
        if sys.platform.startswith('win'):
            assert findBinaryOnPath('notepad').lower().endswith('notepad.exe')
            assert findBinaryOnPath('notepad.exe').lower().endswith('notepad.exe')
            assert not findBinaryOnPath('doesnotexist')
            assert not findBinaryOnPath('doesnotexist.exe')
            assert findBinaryOnPath('a.exe').lower().endswith('a.exe')
            assert findBinaryOnPath('a').lower().endswith('a.exe')
            assert findBinaryOnPath('b.bat').lower().endswith('b.bat')
            assert findBinaryOnPath('b').lower().endswith('b.bat')

            # no exe extension so skipped 
            assert not findBinaryOnPath('c')

            # but if given a full path, use it
            assert findBinaryOnPath(f'{fxDirPlain}/c').lower().endswith('c')

            # test with full paths
            assert not findBinaryOnPath(fxDirPlain + ('/doesnotexist'))
            assert not findBinaryOnPath(fxDirPlain + ('/doesnotexist.exe'))
            assert findBinaryOnPath(fxDirPlain + ('/a.exe')).lower().endswith('a.exe')
            assert findBinaryOnPath(fxDirPlain + ('/a')).lower().endswith('a.exe')
            assert findBinaryOnPath(fxDirPlain + ('/c')).lower().endswith('c')
        else:
            assert findBinaryOnPath('sh').endswith('sh')
            assert not findBinaryOnPath('doesnotexist')
            assert not findBinaryOnPath('doesnotexist.exe')
            assert not findBinaryOnPath('a.exe')
            assert not findBinaryOnPath('a')
            assert not findBinaryOnPath('b.bat')
            assert not findBinaryOnPath('b')

            # if given a path, use it
            assert findBinaryOnPath('c').endswith('c')

            # test with full paths
            assert not findBinaryOnPath(fxDirPlain + ('/doesnotexist'))
            assert not findBinaryOnPath(fxDirPlain + ('/doesnotexist.exe'))
            assert findBinaryOnPath(fxDirPlain + ('/a.exe')).endswith('a.exe')
            assert not findBinaryOnPath(fxDirPlain + ('/a'))
            assert findBinaryOnPath(fxDirPlain + ('/c')).endswith('c')


class TestM3ComputeHash:
    def test_computeHashMd5(self, fxDirPlain):
        import hashlib
        hasher = hashlib.md5()
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        assert '98bf7d8c15784f0a3d63204441e1e2aa' == computeHash(join(fxDirPlain, 'a.txt'), hasher)
        hasher = hashlib.md5()
        assert '98bf7d8c15784f0a3d63204441e1e2aa' == computeHash(join(fxDirPlain, 'a.txt'), hasher, buffersize=3)
    
    def test_computeHashSha256(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        assert 'd1b2a59fbea7e20077af9f91b27e95e865061b270be03ff539ab3b73587882e8' == computeHash(join(fxDirPlain, 'a.txt'), 'sha256')
        assert 'd1b2a59fbea7e20077af9f91b27e95e865061b270be03ff539ab3b73587882e8' == computeHash(join(fxDirPlain, 'a.txt'), 'sha256', buffersize=3)
        
    def test_computeHashCrc32(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        assert 'b4fa1177' == computeHash(join(fxDirPlain, 'a.txt'), 'crc32')
        assert 'b4fa1177' == computeHash(join(fxDirPlain, 'a.txt'), 'crc32', buffersize=3)

    def test_computeHashCrc64(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        assert '5eb93453d1752eb5' == computeHash(join(fxDirPlain, 'a.txt'), 'crc64')
        assert '5eb93453d1752eb5' == computeHash(join(fxDirPlain, 'a.txt'), 'crc64', buffersize=3)

    def test_computeHashXx32(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        assert '9061db37' == computeHash(join(fxDirPlain, 'a.txt'), 'xxhash_32')
        assert '9061db37' == computeHash(join(fxDirPlain, 'a.txt'), 'xxhash_32', buffersize=3)

    def test_computeHashXx64(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        assert '89d565b6bc1ad5a9' == computeHash(join(fxDirPlain, 'a.txt'), 'xxhash_64')
        assert '89d565b6bc1ad5a9' == computeHash(join(fxDirPlain, 'a.txt'), 'xxhash_64', buffersize=3)
        
    def test_computeHashFromBytes(self, fxDirPlain):
        assert 'b4fa1177' == computeHashBytes(b'contents', 'crc32')
        assert 'b4fa1177' == computeHashBytes(b'contents', 'crc32', buffersize=3)
        
    def test_computeHashNotExist(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        with pytest.raises(ValueError):
            computeHash(join(fxDirPlain, 'a.txt'), 'no_such_hash')
       
    def test_computeHashLargeFile(self, fxDirPlain):
        fsize = defaultBufSize * 2 + 20
        with open(f'{fxDirPlain}/a.dat', 'wb') as fout:
            for i in range(fsize):
                letter = ord('a') + (i%26)
                fout.write(chr(letter).encode('latin-1'))
        assert '4642eec0' == computeHash(f'{fxDirPlain}/a.dat', 'crc32')
        assert '4642eec0' == computeHash(f'{fxDirPlain}/a.dat', 'crc32', buffersize=40)
        assert 'ab73f0d9bfb568486d122f82480e4801' == computeHash(f'{fxDirPlain}/a.dat', 'md5')
        assert 'ab73f0d9bfb568486d122f82480e4801' == computeHash(f'{fxDirPlain}/a.dat', 'md5', buffersize=30)

class TestWindowsUrlFileGet:
    def test(self, fxDirPlain):
        # typical file
        example = '''[InternetShortcut]
URL=https://example.net/
        '''
        writeAll(join(fxDirPlain, 'a.url'), example)
        assert 'https://example.net/' == windowsUrlFileGet(join(fxDirPlain, 'a.url'))

        # has different keys
        example = '''[InternetShortcut]
Icon=12345
URL=https://exampletwo.net/'''
        writeAll(join(fxDirPlain, 'a.url'), example)
        assert 'https://exampletwo.net/' == windowsUrlFileGet(join(fxDirPlain, 'a.url'))

        # has no url
        example = '''[InternetShortcut]
Icon=12345'''
        writeAll(join(fxDirPlain, 'a.url'), example)
        with pytest.raises(RuntimeError):
            windowsUrlFileGet(join(fxDirPlain, 'a.url'))

    def test_windowsUrlFileWrite(self, fxDirPlain):
        expected = '''[InternetShortcut]
URL=https://example.net/
'''
        deleteSure(join(fxDirPlain, 'a.url'))
        windowsUrlFileWrite(join(fxDirPlain, 'a.url'), 'https://example.net/')
        assert expected.replace('\r\n', '\n') == readAll(join(fxDirPlain, 'a.url'))
        assert 'https://example.net/' == windowsUrlFileGet(join(fxDirPlain, 'a.url'))

@pytest.mark.skipif('sys.platform.startswith("win")')
class TestRunProcess:
    def test_runShellScript(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'src.txt'), 'contents')
        writeAll(join(fxDirPlain, 's.sh'), 'cp src.txt dest.txt')
        retcode, stdout, stderr = run(['/bin/bash', join(fxDirPlain, 's.sh')])
        assert retcode == 0 and isFile(join(fxDirPlain, 'dest.txt'))

    def test_runShellScriptWithoutCapture(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'src.txt'), 'contents')
        writeAll(join(fxDirPlain, 's.sh'), 'cp src.txt dest.txt')
        retcode, stdout, stderr = run(['/bin/bash', join(fxDirPlain, 's.sh')], captureOutput=False)
        assert retcode == 0 and isFile(join(fxDirPlain, 'dest.txt'))

    def test_runShellScriptWithUnicodeChars(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'src.txt'), 'contents')
        writeAll(join(fxDirPlain, u's\u1101.sh'), 'cp src.txt dest.txt')
        runWithoutWait(['/bin/bash', join(fxDirPlain, u's\u1101.sh')])
        time.sleep(0.5)
        assert isFile(join(fxDirPlain, 'dest.txt'))
    
    def test_runShellScriptWithoutWait(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'src.txt'), 'contents')
        writeAll(join(fxDirPlain, u's\u1101.sh'), 'cp src.txt dest.txt')
        run(['/bin/bash', join(fxDirPlain, u's\u1101.sh')], wait=False, captureOutput=False, throwOnFailure=False)
        time.sleep(0.5)
        assert isFile(join(fxDirPlain, 'dest.txt'))

    def test_runGetExitCode(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.sh'), '\nexit 123')
        retcode, stdout, stderr = run(['/bin/bash', join(fxDirPlain, 's.sh')], throwOnFailure=False)
        assert 123 == retcode

    def test_runGetExitCodeWithoutCapture(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.sh'), '\nexit 123')
        retcode, stdout, stderr = run(['/bin/bash', join(fxDirPlain, 's.sh')], throwOnFailure=False, captureOutput=False)
        assert 123 == retcode

    def test_runNonZeroExitShouldThrow(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.sh'), '\nexit 123')
        with pytest.raises(RuntimeError):
            run(['/bin/bash', join(fxDirPlain, 's.sh')])

    def test_runNonZeroExitShouldThrowWithoutCapture(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.sh'), '\nexit 123')
        with pytest.raises(RuntimeError):
            run(['/bin/bash', join(fxDirPlain, 's.sh')], captureOutput=False)

    def test_runSendArgument(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.sh'), '\n@echo off\necho $1')
        retcode, stdout, stderr = run(['/bin/bash', join(fxDirPlain, 's.sh'), 'testarg'])
        assert retcode == 0 and stdout == b'testarg'

    def test_runSendArgumentContainingSpaces(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.sh'), '\n@echo off\necho $1')
        retcode, stdout, stderr = run(['/bin/bash', join(fxDirPlain, 's.sh'), 'test arg'])
        assert retcode == 0 and stdout == b'test arg'

    def test_runGetOutput(self, fxDirPlain):
        # the subprocess module uses threads to capture both stderr and stdout without deadlock
        writeAll(join(fxDirPlain, 's.sh'), 'echo testecho\necho testechoerr 1>&2')
        retcode, stdout, stderr = run(['/bin/bash', join(fxDirPlain, 's.sh')])
        assert retcode == 0
        assert stdout == b'testecho'
        assert stderr == b'testechoerr'

    def test_runWithTimeout(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.sh'), 'echo testecho\necho testechoerr 1>&2')
        retcode, stdout, stderr = runWithTimeout(['/bin/bash', join(fxDirPlain, 's.sh')],
            timeoutSeconds=1)
        assert retcode == 0
        assert stdout == b'testecho'
        assert stderr == b'testechoerr'

    def test_runWithTimeoutTimesOut(self, fxDirPlain):
        tm = SimpleTimer()
        writeAll(join(fxDirPlain, 's.sh'), 'sleep 100')
        with pytest.raises(Exception, match='timed out'):
            runWithTimeout(['/bin/bash', join(fxDirPlain, 's.sh')], 
                timeoutSeconds=1, captureOutput=False)
            
        assert tm.check() < 2
    
    def test_runQuiet(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.sh'), 'echo testecho\necho testechoerr 1>&2\nexit 123')
        retcode, stdout, stderr = run(['/bin/bash', join(fxDirPlain, 's.sh')], 
            captureOutput=False, silenceOutput=True, throwOnFailure=False)
        
        assert 123 == retcode
        

@pytest.mark.skipif('not sys.platform.startswith("win")')
class TestRunProcessWin:
    def test_runShellScript(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'src.txt'), 'contents')
        writeAll(join(fxDirPlain, 's.bat'), 'copy src.txt dest.txt')
        retcode, stdout, stderr = run([join(fxDirPlain, 's.bat')])
        assert retcode == 0 and isFile(join(fxDirPlain, 'dest.txt'))

    def test_runShellScriptWithoutCapture(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'src.txt'), 'contents')
        writeAll(join(fxDirPlain, 's.bat'), 'copy src.txt dest.txt')
        retcode, stdout, stderr = run([join(fxDirPlain, 's.bat')], captureOutput=False)
        assert retcode == 0 and isFile(join(fxDirPlain, 'dest.txt'))

    def test_runShellScriptWithUnicodeChars(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'src.txt'), 'contents')
        writeAll(join(fxDirPlain, u's\u1101.bat'), 'copy src.txt dest.txt')
        runWithoutWait([join(fxDirPlain, u's\u1101.bat')])
        time.sleep(0.5)
        assert isFile(join(fxDirPlain, 'dest.txt'))
    
    def test_runShellScriptWithoutWait(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'src.txt'), 'contents')
        writeAll(join(fxDirPlain, u's\u1101.bat'), 'copy src.txt dest.txt')
        run([join(fxDirPlain, u's\u1101.bat')], wait=False, captureOutput=False, throwOnFailure=False)
        time.sleep(0.5)
        assert isFile(join(fxDirPlain, 'dest.txt'))

    def test_runGetExitCode(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.bat'), '\nexit /b 123')
        retcode, stdout, stderr = run([join(fxDirPlain, 's.bat')], throwOnFailure=False)
        assert 123 == retcode

    def test_runGetExitCodeWithoutCapture(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.bat'), '\nexit /b 123')
        retcode, stdout, stderr = run([join(fxDirPlain, 's.bat')], throwOnFailure=False, captureOutput=False)
        assert 123 == retcode

    def test_runNonZeroExitShouldThrow(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.bat'), '\nexit /b 123')
        with pytest.raises(RuntimeError):
            run([join(fxDirPlain, 's.bat')])

    def test_runNonZeroExitShouldThrowWithoutCapture(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.bat'), '\nexit /b 123')
        with pytest.raises(RuntimeError):
            run([join(fxDirPlain, 's.bat')], captureOutput=False)

    def test_runSendArgument(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.bat'), '\n@echo off\necho %1')
        retcode, stdout, stderr = run([join(fxDirPlain, 's.bat'), 'testarg'])
        assert retcode == 0 and stdout == b'testarg'

    def test_runSendArgumentContainingSpaces(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.bat'), '\n@echo off\necho %1')
        retcode, stdout, stderr = run([join(fxDirPlain, 's.bat'), 'test arg'])
        assert retcode == 0 and stdout == b'"test arg"'

    def test_runGetOutput(self, fxDirPlain):
        # the subprocess module uses threads to capture both stderr and stdout without deadlock
        writeAll(join(fxDirPlain, 's.bat'), '@echo off\necho testecho\necho testechoerr 1>&2')
        retcode, stdout, stderr = run([join(fxDirPlain, 's.bat')])
        assert retcode == 0
        assert stdout == b'testecho'
        assert stderr == b'testechoerr'
    
    def test_runWithTimeout(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.bat'), '@echo off\necho testecho\necho testechoerr 1>&2')
        retcode, stdout, stderr = runWithTimeout([join(fxDirPlain, 's.bat')], 
            timeoutSeconds=1)
        assert retcode == 0
        assert stdout == b'testecho'
        assert stderr == b'testechoerr'

    def test_runWithTimeoutTimesOut(self, fxDirPlain):
        tm = SimpleTimer()
        writeAll(join(fxDirPlain, 's.bat'), 'timeout /t 100')
        with pytest.raises(Exception, match='timed out'):
            runWithTimeout([join(fxDirPlain, 's.bat')], timeoutSeconds=1, captureOutput=False)
        
        assert tm.check() < 2
    
    def test_runQuiet(self, fxDirPlain):
        writeAll(join(fxDirPlain, 's.bat'), 'echo testecho\necho testechoerr 1>&2\nexit /b 123')
        retcode, stdout, stderr = run([join(fxDirPlain, 's.bat')], 
            captureOutput=False, silenceOutput=True, throwOnFailure=False)
        
        assert 123 == retcode

class TestRunRSync:
    def test_basic(self, fxFilesPlain, fxDirPlain):
        self._restoreDirectoryContents(fxFilesPlain)

        # typical usage
        expect = ''
        assert expect == self._listDirectoryToString(fxDirPlain)
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == self._listDirectoryToString(fxFilesPlain)
        dest = join(fxDirPlain, 'dest')
        makeDirs(dest)
        self._runBasedOnPlatform(fxFilesPlain, dest, deleteExisting=True)
        assert expect == self._listDirectoryToString(dest)

        # copy it again, nothing to change
        self._runBasedOnPlatform(fxFilesPlain, dest, deleteExisting=True)
        assert expect == self._listDirectoryToString(dest)

    def test_empty(self, fxDirPlain):
        # copying an empty folder should succeed
        src = join(fxDirPlain, 'src')
        makeDirs(src)
        dest = join(fxDirPlain, 'dest')
        makeDirs(dest)
        self._runBasedOnPlatform(src, dest, deleteExisting=True)
        assert '' == self._listDirectoryToString(dest)

    def test_shouldOverwrite(self, fxDirPlain):
        # create a modified dir
        src = join(fxDirPlain, 'src')
        self._restoreDirectoryContents(src)
        dest = join(fxDirPlain, 'dest')
        self._restoreDirectoryContents(dest)
        self._modifyDirectoryContents(src)
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == self._listDirectoryToString(dest)
        expect = 'P1.PNG,15|a2.txt,15|newfile,11|s1,0|s1/ss1,0|s1/ss1/file.txt,35|s1/ss2,0|s2,0|s2/other.txt,34'
        assert expect == self._listDirectoryToString(src)

        # run rsync and delete existing
        self._runBasedOnPlatform(src, dest, deleteExisting=True)
        assert expect == self._listDirectoryToString(dest)

    def test_shouldNotOverwrite(self, fxDirPlain):
        # create a modified dir
        src = join(fxDirPlain, 'src')
        self._restoreDirectoryContents(src)
        dest = join(fxDirPlain, 'dest')
        self._restoreDirectoryContents(dest)
        self._modifyDirectoryContents(src)
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == self._listDirectoryToString(dest)
        expect = 'P1.PNG,15|a2.txt,15|newfile,11|s1,0|s1/ss1,0|s1/ss1/file.txt,35|s1/ss2,0|s2,0|s2/other.txt,34'
        assert expect == self._listDirectoryToString(src)

        # run rsync and don't delete existing
        self._runBasedOnPlatform(src, dest, deleteExisting=False)
        expect = 'P1.PNG,15|a1.txt,15|a2.txt,15|a2png,14|newfile,11|s1,0|s1/ss1,0|s1/ss1/file.txt,35|s1/ss2,0|s2,0|s2/other.txt,34'
        assert expect == self._listDirectoryToString(dest)

    def test_winExcludes(self, fxDirPlain):
        # create a modified dir
        src = join(fxDirPlain, 'src')
        self._restoreDirectoryContents(src)
        dest = join(fxDirPlain, 'dest')
        self._restoreDirectoryContents(dest)
        self._modifyDirectoryContents(src)
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == self._listDirectoryToString(dest)
        expect = 'P1.PNG,15|a2.txt,15|newfile,11|s1,0|s1/ss1,0|s1/ss1/file.txt,35|s1/ss2,0|s2,0|s2/other.txt,34'
        assert expect == self._listDirectoryToString(src)

        # run rsync with exclusions
        if sys.platform.startswith('win'):
            self._runBasedOnPlatform(src, dest, deleteExisting=True, robocopyExcludeFiles=['a1.txt', 'newfile', 'other.txt'], robocopyExcludeDirs=['ss1'])
            expect = 'P1.PNG,15|a1.txt,15|a2.txt,15|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
            assert expect == self._listDirectoryToString(dest)

    def test_dirExcludes(self, fxDirPlain):
        src = join(fxDirPlain, 'src')
        self._restoreDirectoryContents(src)
        dest = join(fxDirPlain, 'dest')
        self._restoreDirectoryContents(dest)

        # modify a file
        writeAll(join(src, 'a2png'), 'mm')

        # add ignored files
        makeDirs(join(src, 'ignorethis'))
        writeAll(join(src, 'ignorethis', 'a.txt'), 't1')
        writeAll(join(src, 'ignorethis', 'b.txt'), 't2')
        writeAll(join(src, 'ign.txt'), 't')
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == self._listDirectoryToString(dest)
        expect = 'P1.PNG,15|a1.txt,15|a2png,2|ign.txt,1|ignorethis,0|ignorethis/a.txt,2|ignorethis/b.txt,2|' + \
            's1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == self._listDirectoryToString(src)

        # run rsync with exclusions
        if sys.platform.startswith('win'):
            self._runBasedOnPlatform(src, dest, deleteExisting=True, robocopyExcludeFiles=['ign.txt'], robocopyExcludeDirs=['ignorethis'])
        else:
            self._runBasedOnPlatform(src, dest, deleteExisting=True, excludeRelative=['ign.txt', 'ignorethis'])

        expect = 'P1.PNG,15|a1.txt,15|a2png,2|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == self._listDirectoryToString(dest)

    def test_expectFailure(self, fxDirPlain):
        # try to copy non-existing directory
        src = join(fxDirPlain, 'src')
        dest = join(fxDirPlain, 'dest')
        with pytest.raises(Exception):
            self._runBasedOnPlatform(src, dest, deleteExisting=True, checkExist=False)

    def test_nonWindowsError(self):
        assert (True, '') == interpretRsyncErr(0)
        assert (False, 'Syntax or usage error') == interpretRsyncErr(1)
        assert (False, 'Timeout waiting for daemon connection') == interpretRsyncErr(35)
        assert (False, 'Unknown') == interpretRsyncErr(-1)
        assert (False, 'Unknown') == interpretRsyncErr(100)

    def test_windowsError(self):
        res = interpretRobocopyErr(0x0)
        assert res[0] is True and res[1] == ''
        res = interpretRobocopyErr(0x1)
        assert res[0] is True and 'One or more files' in res[1]
        res = interpretRobocopyErr(0x1 | 0x4)
        assert res[0] is True and 'One or more files' in res[1] and 'Mismatched files' in res[1]
        res = interpretRobocopyErr(0x1 | 0x10)
        assert res[0] is False and 'One or more files' in res[1] and 'Serious error' in res[1]
        res = interpretRobocopyErr(0x1 | 0x40)
        assert res[0] is False and 'One or more files' in res[1]
        res = interpretRobocopyErr(0x20)
        assert res[0] is False and res[1] == ''
    
    def _runBasedOnPlatform(self, *args, **kwargs):
        if sys.platform.startswith('win'):
            runRsync(*args, useRobocopy=True, **kwargs)
        else:
            runRsync(*args, **kwargs)
    
    def _listDirectoryToString(self, basedir):
        out = []
        for f, short in files.recurseFiles(basedir, includeDirs=True):
            s = f.replace(basedir, '').replace(os.sep, '/').lstrip('/')
            if s:
                # don't include the root
                size = 0 if files.isDir(f) else files.getSize(f)
                out.append(s + ',' + str(size))

        return '|'.join(sorted(out))

    def _modifyDirectoryContents(self, basedir):
        # deleted file
        os.unlink(join(basedir, 'a2png'))

        # new file
        writeAll(join(basedir, 'newfile'), 'newcontents')

        # modified (newer)
        writeAll(join(basedir, 's1/ss1/file.txt'), 'changedcontents' + '-' * 20)

        # modified (older)
        writeAll(join(basedir, 's2/other.txt'), 'changedcontent' + '-' * 20)
        oneday = 60 * 60 * 24
        setLastModTime(join(basedir, 's2/other.txt'),
            getNowAsMillisTime() / 1000.0 - oneday, TimeUnits.Milliseconds)

        # renamed file
        move(join(basedir, 'a1.txt'), join(basedir, 'a2.txt'), True)
    
    def _restoreDirectoryContents(self, basedir):
        ensureEmptyDirectory(basedir)

        # create every combination:
        # full						contains files and dirs
        # full/s1					contains dirs but no files
        # full/s1/ss1 			contains files but no dirs
        # full/s1/ss2 			contains no files or dirs
        dirsToCreate = ['s1', 's2', 's1/ss1', 's1/ss2']
        for dir in dirsToCreate:
            os.makedirs(join(basedir, dir).replace('/', sep))

        filesToCreate = ['P1.PNG', 'a1.txt', 'a2png', 's1/ss1/file.txt', 's2/other.txt']
        for file in filesToCreate:
            writeAll(join(basedir, file).replace('/', sep), 'contents_' + getName(file))

