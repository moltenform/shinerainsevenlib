# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pytest
import tempfile
import os
import sys
from os.path import join
from ..common_util import isPy3OrNewer
from ..common_higher import getNowAsMillisTime

        

class TestFiletimes:
    @pytest.mark.skipif('not isPy3OrNewer')
    def test_modtimeIsUpdated(self, fixtureDir):
        tests = [
            [getFileLastModifiedTime, setFileLastModifiedTime],
            [getModTimeNs, setModTimeNs],
        ]

        for fnGet, fnSet in tests:
            # getting the time from the file twice
            writeAll(join(fixtureDir, 'a.txt'), 'contents')
            curtime1 = fnGet(join(fixtureDir, 'a.txt'))
            curtime2 = fnGet(join(fixtureDir, 'a.txt'))
            assert curtime1 == curtime2

            # update the time by changing the file
            import time
            time.sleep(2)
            with open(join(fixtureDir, 'a.txt'), 'a') as f:
                f.write('changed')
            curtime3 = fnGet(join(fixtureDir, 'a.txt'))
            curtime4 = fnGet(join(fixtureDir, 'a.txt'))
            assert curtime3 == curtime4
            assert curtime3 > curtime2

            # update the time manually
            fnSet(join(fixtureDir, 'a.txt'), curtime3 // 100)
            curtime5 = fnGet(join(fixtureDir, 'a.txt'))
            assert curtime5 < curtime4



class TestDirectoryList:
    def test_listDirs(self, fixture_fulldir):
        expected = ['s1', 's2']
        expectedTuples = [(join(fixture_fulldir, s), s) for s in expected]
        assert expectedTuples == sorted(list(listDirs(fixture_fulldir)))

    def test_listChildren(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png', 's1', 's2']
        expectedTuples = [(join(fixture_fulldir, s), s) for s in expected]
        assert expectedTuples == sorted(list(listChildren(fixture_fulldir)))

    def test_listChildrenFilenamesOnly(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png', 's1', 's2']
        assert expected == sorted(list(listChildren(fixture_fulldir, filenamesOnly=True)))

    def test_listChildrenCertainExtensions(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt']
        assert expected == sorted(list(listChildren(fixture_fulldir, filenamesOnly=True, allowedExts=['png', 'txt'])))

    def test_listFiles(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png']
        expectedTuples = [(join(fixture_fulldir, s), s) for s in expected]
        assert expectedTuples == sorted(list(listFiles(fixture_fulldir)))

    def test_listFilesFilenamesOnly(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png']
        assert expected == sorted(list(listFiles(fixture_fulldir, filenamesOnly=True)))

    def test_listFilesCertainExtensions(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt']
        assert expected == sorted(list(listFiles(fixture_fulldir, filenamesOnly=True, allowedExts=['png', 'txt'])))

    def test_recurseFiles(self, fixture_fulldir):
        expected = ['/P1.PNG', '/a1.txt', '/a2png', '/s1/ss1/file.txt', '/s2/other.txt']
        expectedTuples = [(fixture_fulldir + s.replace('/', sep), getName(s)) for s in expected]
        assert expectedTuples == sorted(list(recurseFiles(fixture_fulldir)))

    def test_recurseFilesFilenamesOnly(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png', 'file.txt', 'other.txt']
        assert expected == sorted(list(recurseFiles(fixture_fulldir, filenamesOnly=True)))

    def test_recurseFilesCertainExtensions(self, fixture_fulldir):
        expected = ['a1.txt', 'file.txt', 'other.txt']
        assert expected == sorted(list(recurseFiles(fixture_fulldir, filenamesOnly=True, allowedExts=['txt'])))

    def test_recurseFilesAcceptAllSubDirs(self, fixture_fulldir):
        expected = ['a1.txt', 'file.txt', 'other.txt']
        assert expected == sorted(list(
            recurseFiles(fixture_fulldir, filenamesOnly=True, allowedExts=['txt'], fnFilterDirs=lambda d: True)))

    def test_recurseFilesAcceptNoSubDirs(self, fixture_fulldir):
        expected = ['a1.txt']
        assert expected == sorted(list(
            recurseFiles(fixture_fulldir, filenamesOnly=True, allowedExts=['txt'], fnFilterDirs=lambda d: False)))

    def test_recurseFilesExcludeOneSubdir(self, fixture_fulldir):
        expected = ['a1.txt', 'other.txt']

        def filter(d):
            return getName(d) != 's1'
        assert expected == sorted(list(recurseFiles(fixture_fulldir, filenamesOnly=True, allowedExts=['txt'], 
                                                    fnFilterDirs=filter)))

    def test_recurseDirs(self, fixture_fulldir):
        expected = ['/full', '/full/s1', '/full/s1/ss1', '/full/s1/ss2', '/full/s2']
        expectedTuples = [(getParent(fixture_fulldir) + s.replace('/', sep), getName(s)) for s in expected]
        assert expectedTuples == sorted(list(recurseDirs(fixture_fulldir)))

    def test_recurseDirsNamesOnly(self, fixture_fulldir):
        expected = ['full', 's1', 's2', 'ss1', 'ss2']
        assert expected == sorted(list(recurseDirs(fixture_fulldir, filenamesOnly=True)))

    def test_recurseDirsExcludeOneSubdir(self, fixture_fulldir):
        expected = ['full', 's2']

        def filter(d):
            return getName(d) != 's1'
        assert expected == sorted(list(recurseDirs(fixture_fulldir, filenamesOnly=True, 
                                                   fnFilterDirs=filter)))

    def tupleFromObj(self, o):
        # x-platform differences in what is the size of a directory
        size = 0 if isDir(o.path) else o.size()
        return (getName(getParent(o.path)), o.short(), size)

    @pytest.mark.skipif('not isPy3OrNewer')
    def test_listFileInfo(self, fixture_fulldir):
        expected = [('full', 'P1.PNG', 15), ('full', 'a1.txt', 15), ('full', 'a2png', 14)]
        got = [self.tupleFromObj(o) for o in listFileInfo(fixture_fulldir)]
        assert expected == sorted(got)

    @pytest.mark.skipif('not isPy3OrNewer')
    def test_listFileInfoIncludeDirs(self, fixture_fulldir):
        expected = [('full', 'P1.PNG', 15), ('full', 'a1.txt', 15), ('full', 'a2png', 14),
            ('full', 's1', 0), ('full', 's2', 0)]
        got = [self.tupleFromObj(o)
            for o in listFileInfo(fixture_fulldir, filesOnly=False)]
        assert expected == sorted(got)

    @pytest.mark.skipif('not isPy3OrNewer')
    def test_recurseFileInfo(self, fixture_fulldir):
        expected = [('full', 'P1.PNG', 15), ('full', 'a1.txt', 15), ('full', 'a2png', 14),
            ('s2', 'other.txt', 18), ('ss1', 'file.txt', 17)]
        got = [self.tupleFromObj(o)
            for o in recurseFileInfo(fixture_fulldir)]
        assert expected == sorted(got)

    @pytest.mark.skipif('not isPy3OrNewer')
    def test_recurseFileInfoIncludeDirs(self, fixture_fulldir):
        expected = [('full', 'P1.PNG', 15), ('full', 'a1.txt', 15), ('full', 'a2png', 14),
            ('full', 's1', 0), ('full', 's2', 0), ('s1', 'ss1', 0), ('s1', 'ss2', 0),
            ('s2', 'other.txt', 18), ('ss1', 'file.txt', 17)]
        got = [self.tupleFromObj(o)
            for o in recurseFileInfo(fixture_fulldir, filesOnly=False)]
        assert expected == sorted(got)

    @pytest.mark.skipif('not isPy3OrNewer')
    def test_recurseFilesMany(self, fixtureFileTree):
        # no filter
        expected = 'fb/a/bz/aa.txt|fb/a/bz/bb.txt|fb/a/bz/fb/cc.txt|' + \
            'fb/a/bz/zz.txt|fb/a/fb/a.txt|fb/a/fb/b.txt|fb/a/fb' + \
            '/c/c0.txt|fb/a/fb/c/c1.txt|fb/a/r1.txt|fb/fb/cc.txt|fb/r2.txt|r3.txt'
        assert expected == listDirectoryToStringFileInfo(fixtureFileTree, True, {})
        assert expected == listDirectoryToStringFileInfo(fixtureFileTree, False, {})

        # filter out nearly everything
        def filter(p):
            return getName(p) != 'fb'
        assert 'r3.txt' == listDirectoryToStringFileInfo(fixtureFileTree, True, {'fnFilterDirs': filter})
        assert 'r3.txt' == listDirectoryToStringFileInfo(fixtureFileTree, False, {'fnFilterDirs': filter})

        # intentionally can't filter out root dir
        expected = 'a/bz/aa.txt|a/bz/bb.txt|a/bz/zz.txt|a/r1.txt|r2.txt'
        assert expected == listDirectoryToStringFileInfo(fixtureFileTree + '/fb', True, {'fnFilterDirs': filter})
        assert expected == listDirectoryToStringFileInfo(fixtureFileTree + '/fb', False, {'fnFilterDirs': filter})

    def test_checkNamedParameters(self, fixtureDir):
        with pytest.raises(ValueError) as exc:
            list(listChildren(fixtureDir, True))
        exc.match('please name parameters')

class TestOtherUtilsActingOnFiles:
    def test_getSizeRecurse(self, fixture_fulldir):
        assert getSizeRecurse(fixture_fulldir) == 79


class TestFilesUtils:
    def test_extensionPossiblyExecutableNoExt(self, fixtureDir):
        assert extensionPossiblyExecutable('noext') is False
        assert extensionPossiblyExecutable('/path/noext') is False

    def test_extensionPossiblyExecutableExt(self, fixtureDir):
        assert extensionPossiblyExecutable('ext.jpg') is False
        assert extensionPossiblyExecutable('/path/ext.jpg') is False

    def test_extensionPossiblyExecutableDirsep(self, fixtureDir):
        assert extensionPossiblyExecutable('dirsep/') is False
        assert extensionPossiblyExecutable('/path/dirsep/') is False

    def test_extensionPossiblyExecutablePeriod(self, fixtureDir):
        assert 'exe' == extensionPossiblyExecutable('test.jpg.exe')
        assert 'exe' == extensionPossiblyExecutable('/path/test.jpg.exe')

    def test_extensionPossiblyExecutablePeriodOk(self, fixtureDir):
        assert extensionPossiblyExecutable('test.exe.jpg') is False
        assert extensionPossiblyExecutable('/path/test.exe.jpg') is False

    def test_extensionPossiblyExecutableOk(self, fixtureDir):
        assert extensionPossiblyExecutable('ext.c') is False
        assert extensionPossiblyExecutable('/path/ext.c') is False
        assert extensionPossiblyExecutable('ext.longer') is False
        assert extensionPossiblyExecutable('/path/ext.longer') is False

    def test_extensionPossiblyExecutableExe(self, fixtureDir):
        assert 'exe' == extensionPossiblyExecutable('ext.exe')
        assert 'exe' == extensionPossiblyExecutable('/path/ext.exe')
        assert 'exe' == extensionPossiblyExecutable('ext.com')
        assert 'exe' == extensionPossiblyExecutable('/path/ext.com')
        assert 'exe' == extensionPossiblyExecutable('ext.vbScript')
        assert 'exe' == extensionPossiblyExecutable('/path/ext.vbScript')

    def test_extensionPossiblyExecutableWarn(self, fixtureDir):
        assert 'warn' == extensionPossiblyExecutable('ext.Url')
        assert 'warn' == extensionPossiblyExecutable('/path/ext.Url')
        assert 'warn' == extensionPossiblyExecutable('ext.doCM')
        assert 'warn' == extensionPossiblyExecutable('/path/ext.doCM')
        assert 'warn' == extensionPossiblyExecutable('ext.EXOPC')
        assert 'warn' == extensionPossiblyExecutable('/path/ext.EXOPC')

    
    def test_computeHashDefaultHash(self, fixtureDir):
        writeAll(join(fixtureDir, 'a.txt'), 'contents')
        assert '4a756ca07e9487f482465a99e8286abc86ba4dc7' == computeHash(join(fixtureDir, 'a.txt'))

    def test_computeHashMd5Specified(self, fixtureDir):
        writeAll(join(fixtureDir, 'a.txt'), 'contents')
        assert '4a756ca07e9487f482465a99e8286abc86ba4dc7' == computeHash(join(fixtureDir, 'a.txt'), 'sha1')

    

    def test_windowsUrlFileGet(self, fixtureDir):
        # typical file
        example = '''[InternetShortcut]
URL=https://example.net/
        '''
        writeAll(join(fixtureDir, 'a.url'), example)
        assert 'https://example.net/' == windowsUrlFileGet(join(fixtureDir, 'a.url'))

        # has different keys
        example = '''[InternetShortcut]
Icon=12345
URL=https://exampletwo.net/'''
        writeAll(join(fixtureDir, 'a.url'), example)
        assert 'https://exampletwo.net/' == windowsUrlFileGet(join(fixtureDir, 'a.url'))

        # has no url
        example = '''[InternetShortcut]
Icon=12345'''
        writeAll(join(fixtureDir, 'a.url'), example)
        with pytest.raises(RuntimeError):
            windowsUrlFileGet(join(fixtureDir, 'a.url'))

    def test_windowsUrlFileWrite(self, fixtureDir):
        expected = '''[InternetShortcut]
URL=https://example.net/
'''
        deleteSure(join(fixtureDir, 'a.url'))
        windowsUrlFileWrite(join(fixtureDir, 'a.url'), 'https://example.net/')
        assert expected.replace('\r\n', '\n') == readAll(join(fixtureDir, 'a.url'))
        assert 'https://example.net/' == windowsUrlFileGet(join(fixtureDir, 'a.url'))

class TestRunRSync:
    def test_normal(self, fixture_fulldir, fixtureDir):
        # typical usage
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == listDirectoryToString(fixture_fulldir)
        dest = join(fixtureDir, 'dest')
        makeDirs(dest)
        runRsync(fixture_fulldir, dest, deleteExisting=True)
        assert expect == listDirectoryToString(dest)

        # copy it again, nothing to change
        runRsync(fixture_fulldir, dest, deleteExisting=True)
        assert expect == listDirectoryToString(dest)

    def test_empty(self, fixtureDir):
        # copying an empty folder should succeed
        src = join(fixtureDir, 'src')
        makeDirs(src)
        dest = join(fixtureDir, 'dest')
        makeDirs(dest)
        runRsync(src, dest, deleteExisting=True)
        assert '' == listDirectoryToString(dest)

    def test_shouldOverwrite(self, fixtureDir):
        # create a modified dir
        src = join(fixtureDir, 'src')
        restoreDirectoryContents(src)
        dest = join(fixtureDir, 'dest')
        restoreDirectoryContents(dest)
        modifyDirectoryContents(src)
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == listDirectoryToString(dest)
        expect = 'P1.PNG,15|a2.txt,15|newfile,11|s1,0|s1/ss1,0|s1/ss1/file.txt,35|s1/ss2,0|s2,0|s2/other.txt,34'
        assert expect == listDirectoryToString(src)

        # run rsync and delete existing
        runRsync(src, dest, deleteExisting=True)
        assert expect == listDirectoryToString(dest)

    def test_shouldNotOverwrite(self, fixtureDir):
        # create a modified dir
        src = join(fixtureDir, 'src')
        restoreDirectoryContents(src)
        dest = join(fixtureDir, 'dest')
        restoreDirectoryContents(dest)
        modifyDirectoryContents(src)
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == listDirectoryToString(dest)
        expect = 'P1.PNG,15|a2.txt,15|newfile,11|s1,0|s1/ss1,0|s1/ss1/file.txt,35|s1/ss2,0|s2,0|s2/other.txt,34'
        assert expect == listDirectoryToString(src)

        # run rsync and don't delete existing
        runRsync(src, dest, deleteExisting=False)
        expect = 'P1.PNG,15|a1.txt,15|a2.txt,15|a2png,14|newfile,11|s1,0|s1/ss1,0|s1/ss1/file.txt,35|s1/ss2,0|s2,0|s2/other.txt,34'
        assert expect == listDirectoryToString(dest)

    def test_winExcludes(self, fixtureDir):
        # create a modified dir
        src = join(fixtureDir, 'src')
        restoreDirectoryContents(src)
        dest = join(fixtureDir, 'dest')
        restoreDirectoryContents(dest)
        modifyDirectoryContents(src)
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == listDirectoryToString(dest)
        expect = 'P1.PNG,15|a2.txt,15|newfile,11|s1,0|s1/ss1,0|s1/ss1/file.txt,35|s1/ss2,0|s2,0|s2/other.txt,34'
        assert expect == listDirectoryToString(src)

        # run rsync with exclusions
        if sys.platform.startswith('win'):
            runRsync(src, dest, deleteExisting=True, winExcludeFiles=['a1.txt', 'newfile', 'other.txt'], winExcludeDirs=['ss1'])
            expect = 'P1.PNG,15|a1.txt,15|a2.txt,15|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
            assert expect == listDirectoryToString(dest)

    def test_dirExcludes(self, fixtureDir):
        src = join(fixtureDir, 'src')
        restoreDirectoryContents(src)
        dest = join(fixtureDir, 'dest')
        restoreDirectoryContents(dest)

        # modify a file
        writeAll(join(src, 'a2png'), 'mm')

        # add ignored files
        makeDirs(join(src, 'ignorethis'))
        writeAll(join(src, 'ignorethis', 'a.txt'), 't1')
        writeAll(join(src, 'ignorethis', 'b.txt'), 't2')
        writeAll(join(src, 'ign.txt'), 't')
        expect = 'P1.PNG,15|a1.txt,15|a2png,14|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == listDirectoryToString(dest)
        expect = 'P1.PNG,15|a1.txt,15|a2png,2|ign.txt,1|ignorethis,0|ignorethis/a.txt,2|ignorethis/b.txt,2|' + \
            's1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == listDirectoryToString(src)

        # run rsync with exclusions
        if sys.platform.startswith('win'):
            runRsync(src, dest, deleteExisting=True, winExcludeFiles=['ign.txt'], winExcludeDirs=['ignorethis'])
        else:
            runRsync(src, dest, deleteExisting=True, linExcludeRelative=['ign.txt', 'ignorethis'])
        expect = 'P1.PNG,15|a1.txt,15|a2png,2|s1,0|s1/ss1,0|s1/ss1/file.txt,17|s1/ss2,0|s2,0|s2/other.txt,18'
        assert expect == listDirectoryToString(dest)

    def test_expectFailure(self, fixtureDir):
        # try to copy non-existing directory
        src = join(fixtureDir, 'srcnotexist')
        dest = join(fixtureDir, 'destnotexist')
        with pytest.raises(Exception):
            runRsync(src, dest, deleteExisting=True, checkExist=False)

    def test_nonWindowsError(self, ):
        assert (True, '') == runRsyncErrMap(0, 'linux')
        assert (False, 'Syntax or usage error') == runRsyncErrMap(1, 'linux')
        assert (False, 'Timeout waiting for daemon connection') == runRsyncErrMap(35, 'linux')
        assert (False, 'Unknown') == runRsyncErrMap(-1, 'linux')
        assert (False, 'Unknown') == runRsyncErrMap(100, 'linux')

    def test_windowsError(self, ):
        res = runRsyncErrMap(0x0, 'windows')
        assert res[0] is True and res[1] == ''
        res = runRsyncErrMap(0x1, 'windows')
        assert res[0] is True and 'One or more files' in res[1]
        res = runRsyncErrMap(0x1 | 0x4, 'windows')
        assert res[0] is True and 'One or more files' in res[1] and 'Mismatched files' in res[1]
        res = runRsyncErrMap(0x1 | 0x10, 'windows')
        assert res[0] is False and 'One or more files' in res[1] and 'Serious error' in res[1]
        res = runRsyncErrMap(0x1 | 0x40, 'windows')
        assert res[0] is False and 'One or more files' in res[1]
        res = runRsyncErrMap(0x20, 'windows')
        assert res[0] is False and res[1] == ''

@pytest.mark.skipif('sys.platform.startswith("win")')
class TestRunProcess:
    def test_runShellScript(self, fixtureDir):
        writeAll(join(fixtureDir, 'src.txt'), 'contents')
        writeAll(join(fixtureDir, 's.sh'), 'cp src.txt dest.txt')
        retcode, stdout, stderr = run(['/bin/bash', join(fixtureDir, 's.sh')])
        assert retcode == 0 and isFile(join(fixtureDir, 'dest.txt'))

    def test_runShellScriptWithoutCapture(self, fixtureDir):
        writeAll(join(fixtureDir, 'src.txt'), 'contents')
        writeAll(join(fixtureDir, 's.sh'), 'cp src.txt dest.txt')
        retcode, stdout, stderr = run(['/bin/bash', join(fixtureDir, 's.sh')], captureOutput=False)
        assert retcode == 0 and isFile(join(fixtureDir, 'dest.txt'))

    def test_runShellScriptWithUnicodeChars(self, fixtureDir):
        import time
        writeAll(join(fixtureDir, 'src.txt'), 'contents')
        writeAll(join(fixtureDir, u's\u1101.sh'), 'cp src.txt dest.txt')
        runWithoutWaitUnicode(['/bin/bash', join(fixtureDir, u's\u1101.sh')])
        time.sleep(0.5)
        assert isFile(join(fixtureDir, 'dest.txt'))

    def test_runGetExitCode(self, fixtureDir):
        writeAll(join(fixtureDir, 's.sh'), '\nexit 123')
        retcode, stdout, stderr = run(['/bin/bash', join(fixtureDir, 's.sh')], throwOnFailure=False)
        assert 123 == retcode

    def test_runGetExitCodeWithoutCapture(self, fixtureDir):
        writeAll(join(fixtureDir, 's.sh'), '\nexit 123')
        retcode, stdout, stderr = run(['/bin/bash', join(fixtureDir, 's.sh')], throwOnFailure=False, captureOutput=False)
        assert 123 == retcode

    def test_runNonZeroExitShouldThrow(self, fixtureDir):
        writeAll(join(fixtureDir, 's.sh'), '\nexit 123')
        with pytest.raises(RuntimeError):
            run(['/bin/bash', join(fixtureDir, 's.sh')])

    def test_runNonZeroExitShouldThrowWithoutCapture(self, fixtureDir):
        writeAll(join(fixtureDir, 's.sh'), '\nexit 123')
        with pytest.raises(RuntimeError):
            run(['/bin/bash', join(fixtureDir, 's.sh')], captureOutput=False)

    def test_runSendArgument(self, fixtureDir):
        writeAll(join(fixtureDir, 's.sh'), '\n@echo off\necho $1')
        retcode, stdout, stderr = run(['/bin/bash', join(fixtureDir, 's.sh'), 'testarg'])
        assert retcode == 0 and stdout == b'testarg'

    def test_runSendArgumentContainingSpaces(self, fixtureDir):
        writeAll(join(fixtureDir, 's.sh'), '\n@echo off\necho $1')
        retcode, stdout, stderr = run(['/bin/bash', join(fixtureDir, 's.sh'), 'test arg'])
        assert retcode == 0 and stdout == b'test arg'

    def test_runGetOutput(self, fixtureDir):
        # the subprocess module uses threads to capture both stderr and stdout without deadlock
        writeAll(join(fixtureDir, 's.sh'), 'echo testecho\necho testechoerr 1>&2')
        retcode, stdout, stderr = run(['/bin/bash', join(fixtureDir, 's.sh')])
        assert retcode == 0
        assert stdout == b'testecho'
        assert stderr == b'testechoerr'

@pytest.mark.skipif('not sys.platform.startswith("win")')
class TestRunProcessWin:
    def test_runShellScript(self, fixtureDir):
        writeAll(join(fixtureDir, 'src.txt'), 'contents')
        writeAll(join(fixtureDir, 's.bat'), 'copy src.txt dest.txt')
        retcode, stdout, stderr = run([join(fixtureDir, 's.bat')])
        assert retcode == 0 and isFile(join(fixtureDir, 'dest.txt'))

    def test_runShellScriptWithoutCapture(self, fixtureDir):
        writeAll(join(fixtureDir, 'src.txt'), 'contents')
        writeAll(join(fixtureDir, 's.bat'), 'copy src.txt dest.txt')
        retcode, stdout, stderr = run([join(fixtureDir, 's.bat')], captureOutput=False)
        assert retcode == 0 and isFile(join(fixtureDir, 'dest.txt'))

    def test_runShellScriptWithUnicodeChars(self, fixtureDir):
        import time
        writeAll(join(fixtureDir, 'src.txt'), 'contents')
        writeAll(join(fixtureDir, u's\u1101.bat'), 'copy src.txt dest.txt')
        runWithoutWaitUnicode([join(fixtureDir, u's\u1101.bat')])
        time.sleep(0.5)
        assert isFile(join(fixtureDir, 'dest.txt'))

    def test_runGetExitCode(self, fixtureDir):
        writeAll(join(fixtureDir, 's.bat'), '\nexit /b 123')
        retcode, stdout, stderr = run([join(fixtureDir, 's.bat')], throwOnFailure=False)
        assert 123 == retcode

    def test_runGetExitCodeWithoutCapture(self, fixtureDir):
        writeAll(join(fixtureDir, 's.bat'), '\nexit /b 123')
        retcode, stdout, stderr = run([join(fixtureDir, 's.bat')], throwOnFailure=False, captureOutput=False)
        assert 123 == retcode

    def test_runNonZeroExitShouldThrow(self, fixtureDir):
        writeAll(join(fixtureDir, 's.bat'), '\nexit /b 123')
        with pytest.raises(RuntimeError):
            run([join(fixtureDir, 's.bat')])

    def test_runNonZeroExitShouldThrowWithoutCapture(self, fixtureDir):
        writeAll(join(fixtureDir, 's.bat'), '\nexit /b 123')
        with pytest.raises(RuntimeError):
            run([join(fixtureDir, 's.bat')], captureOutput=False)

    def test_runSendArgument(self, fixtureDir):
        writeAll(join(fixtureDir, 's.bat'), '\n@echo off\necho %1')
        retcode, stdout, stderr = run([join(fixtureDir, 's.bat'), 'testarg'])
        assert retcode == 0 and stdout == b'testarg'

    def test_runSendArgumentContainingSpaces(self, fixtureDir):
        writeAll(join(fixtureDir, 's.bat'), '\n@echo off\necho %1')
        retcode, stdout, stderr = run([join(fixtureDir, 's.bat'), 'test arg'])
        assert retcode == 0 and stdout == b'"test arg"'

    def test_runGetOutput(self, fixtureDir):
        # the subprocess module uses threads to capture both stderr and stdout without deadlock
        writeAll(join(fixtureDir, 's.bat'), '@echo off\necho testecho\necho testechoerr 1>&2')
        retcode, stdout, stderr = run([join(fixtureDir, 's.bat')])
        assert retcode == 0
        assert stdout == b'testecho'
        assert stderr == b'testechoerr'

def restoreDirectoryContents(basedir):
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

def modifyDirectoryContents(basedir):
    # deleted file
    os.unlink(join(basedir, 'a2png'))

    # new file
    writeAll(join(basedir, 'newfile'), 'newcontents')

    # modified (newer)
    writeAll(join(basedir, 's1/ss1/file.txt'), 'changedcontents' + '-' * 20)

    # modified (older)
    writeAll(join(basedir, 's2/other.txt'), 'changedcontent' + '-' * 20)
    oneday = 60 * 60 * 24
    setFileLastModifiedTime(join(basedir, 's2/other.txt'),
        getNowAsMillisTime() / 1000.0 - oneday)

    # renamed file
    move(join(basedir, 'a1.txt'), join(basedir, 'a2.txt'), True)

def listDirectoryToString(basedir):
    out = []
    for f, short in recurseFiles(basedir, includeDirs=True):
        s = f.replace(basedir, '').replace(os.sep, '/').lstrip('/')
        if s:
            # don't include the root
            size = 0 if isDir(f) else getSize(f)
            out.append(s + ',' + str(size))
    return '|'.join(sorted(out))

def listDirectoryToStringFileInfo(basedir, useFileInfo, kwargs):
    iter = recurseFileInfo(basedir, **kwargs) if useFileInfo else recurseFiles(basedir, **kwargs)
    out = []
    for item in iter:
        if useFileInfo:
            out.append(item.path.replace(basedir, '').replace(os.sep, '/').lstrip('/'))
        else:
            out.append(item[0].replace(basedir, '').replace(os.sep, '/').lstrip('/'))
    return '|'.join(sorted(out))



@pytest.fixture()
def fixtureDir():
    basedir = join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'empty')
    ensureEmptyDirectory(basedir)
    chDir(basedir)
    yield basedir
    ensureEmptyDirectory(basedir)

@pytest.fixture(scope='module')
def fixture_fulldir():
    basedir = join(tempfile.gettempdir(), 'shinerainsevenlib_test', 'full')
    restoreDirectoryContents(basedir)
    yield basedir
    ensureEmptyDirectory(basedir)

