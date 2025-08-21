# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
import sys
sys.path.append('../test_core')
sys.path.append('./tests/test_core')
from common import fxTree, fileInfoListToList, fxTreePlain, fxFilesPlain, fxFullDirPlain
from collections import OrderedDict
import os
import shutil
import time
from src.shinerainsevenlib.files import *


class TestListing:
    def testFullResultsFiles(self, fxTreePlain):
        iter = recurseFiles(fxTreePlain)
        got = sorted(iter)
        assert got == sorted(listFiles(fxTreePlain, recurse=True))
        assert all(os.path.isabs(item[0]) and exists(item[0]) for item in got)
        assert all(not os.path.isabs(item[1]) for item in got)
        assert sorted([item[1] for item in got]) == sorted(listFiles(fxTreePlain, recurse=True, filenamesOnly=True))
        assert [item[1] for item in got] == ['aa.txt', 'bb.txt', 'cc.txt', 'zz.txt', 'a.txt', 'b.txt', 'c0.txt', 'c1.txt', 'r1.txt', 'cc.txt', 'r2.txt', 'r3.txt']
        assert [item[0].replace(fxTreePlain, '').replace('\\', '/') for item in got] == ['/fb/a/bz/aa.txt', '/fb/a/bz/bb.txt', '/fb/a/bz/fb/cc.txt', '/fb/a/bz/zz.txt', '/fb/a/fb/a.txt', '/fb/a/fb/b.txt', '/fb/a/fb/c/c0.txt', '/fb/a/fb/c/c1.txt', '/fb/a/r1.txt', '/fb/fb/cc.txt', '/fb/r2.txt', '/r3.txt']
        
    def testFullResultsDirs(self, fxTreePlain):
        iter = recurseDirs(fxTreePlain)
        got = sorted(iter)
        assert got == sorted(listDirs(fxTreePlain, recurse=True, ))
        assert all(os.path.isabs(item[0]) and exists(item[0]) for item in got)
        assert all(not os.path.isabs(item[1]) for item in got)
        assert sorted([item[1] for item in got]) == sorted(listDirs(fxTreePlain, recurse=True, filenamesOnly=True, ))
        assert [item[1] for item in got] ==  ['tree', 'fb', 'a', 'bz', 'fb', 'fb', 'c', 'fb']
        assert [item[0].replace(fxTreePlain, '').replace('\\', '/') for item in got] ==  ['', '/fb', '/fb/a', '/fb/a/bz', '/fb/a/bz/fb', '/fb/a/fb', '/fb/a/fb/c', '/fb/fb']

    def testFullResultsNoRecurseFiles(self, fxTree):
        got = sorted(listFiles(fxTree.pathDir))
        assert [item[1] for item in got] == ['a.txt', 'b.txt']
        assert [item[0].replace(fxTree.pathDir, '').replace('\\', '/') for item in got] == ['/a.txt', '/b.txt']

    def testFullResultsNoRecurseDirs(self, fxTree):
        got = sorted(listDirs(fxTree.basedir + '/fb/a'))
        assert [item[1] for item in got] == ['bz', 'fb']
        assert [item[0].replace(fxTree.basedir + '/fb/a', '').replace('\\', '/') for item in got] == ['/bz', '/fb']

    def testFilenamesOnly(self, fxTree):
        got = sorted(listFiles(fxTree.pathDir, filenamesOnly=True))
        assert got == ['a.txt', 'b.txt']
        got = sorted(listDirs(fxTree.basedir + '/fb/a', filenamesOnly=True))
        assert got == ['bz', 'fb']
    
    def testFilenamesWithUnicode(self, fxFilesPlain):
        got = sorted(listFiles(fxFilesPlain, filenamesOnly=True))
        assert got == ['1ᄁ.txt', '2ᄁ.txt', 'a1.txt', 'bb2.txt', 'ccc3.txt', 'd4.txt', 'ee5.txt']
    
    def testRecurseFilesExtensions(self, fxTreePlain):
        writeAll(fxTreePlain + '/fb/a/fb/ttt.mp3', 'contents')
        writeAll(fxTreePlain + '/fb/a/ttt.mp3', 'contents')
        writeAll(fxTreePlain + '/fb/a/ttt.png', 'contents')
        writeAll(fxTreePlain + '/fb/ttt.MP3', 'contents')
        writeAll(fxTreePlain + '/fb/notamp3', 'contents')
        writeAll(fxTreePlain + '/fb/not.mp3.other', 'contents')
        
        # this "dotfile" should not count
        writeAll(fxTreePlain + '/fb/.mp3', 'contents')

        # incorrect usage
        with pytest.raises(AssertionError):
            got = sorted(recurseFiles(fxTreePlain, allowedExts='mp3'))

        # incorrect usage
        with pytest.raises(AssertionError):
            got = sorted(recurseFiles(fxTreePlain, allowedExts=['.mp3']))

        # finds no matches
        got = sorted(recurseFiles(fxTreePlain, filenamesOnly=True, allowedExts=['gif']))
        assert got == []

        # with list
        got = sorted(recurseFiles(fxTreePlain, filenamesOnly=True, allowedExts=['png', 'mp3']))
        assert got == ['ttt.MP3', 'ttt.mp3', 'ttt.mp3', 'ttt.png'] 

        # with set
        got = sorted(recurseFiles(fxTreePlain, filenamesOnly=True, allowedExts=set(['png'])))
        assert got == ['ttt.png'] 
    
    def testIncludes(self, fxTreePlain):
        got = sorted(recurseFiles(fxTreePlain, filenamesOnly=True, includeFiles=False, includeDirs=False))
        assert got == []

        got = sorted(recurseFiles(fxTreePlain, filenamesOnly=True, includeFiles=True, includeDirs=False))
        assert got == ['a.txt', 'aa.txt', 'b.txt', 'bb.txt', 'c0.txt', 'c1.txt', 'cc.txt', 'cc.txt', 'r1.txt', 'r2.txt', 'r3.txt', 'zz.txt']

        got = sorted(recurseFiles(fxTreePlain, filenamesOnly=True, includeFiles=False, includeDirs=True))
        assert got == ['a', 'bz', 'c', 'fb', 'fb', 'fb', 'fb', 'tree']

        got = sorted(recurseFiles(fxTreePlain, filenamesOnly=True, includeFiles=True, includeDirs=True))
        assert got == ['a', 'a.txt', 'aa.txt', 'b.txt', 'bb.txt', 'bz', 'c', 'c0.txt', 'c1.txt', 'cc.txt', 'cc.txt', 'fb', 'fb', 'fb', 'fb', 'r1.txt', 'r2.txt', 'r3.txt', 'tree', 'zz.txt']
        
class TestFiltering:
    def test_recurseFilesAcceptAllSubDirs(self, fxFullDirPlain):
        expected = ['a1.txt', 'file.txt', 'other.txt']
        assert expected == sorted(
            recurseFiles(fxFullDirPlain, filenamesOnly=True, allowedExts=['txt'], fnFilterDirs=lambda d: True))

    def test_recurseFilesAcceptNoSubDirs(self, fxFullDirPlain):
        expected = ['a1.txt']
        assert expected == sorted(
            recurseFiles(fxFullDirPlain, filenamesOnly=True, allowedExts=['txt'], fnFilterDirs=lambda d: False))

    def test_recurseFilesExcludeOneSubdir(self, fxFullDirPlain):
        expected = ['a1.txt', 'other.txt']

        def filter(d):
            return getName(d) != 's1'
        assert expected == sorted(recurseFiles(fxFullDirPlain, filenamesOnly=True, allowedExts=['txt'], 
                                                    fnFilterDirs=filter))

    def test_recurseDirs(self, fxFullDirPlain):
        expected = ['/full', '/full/s1', '/full/s1/ss1', '/full/s1/ss2', '/full/s2']
        expectedTuples = [(getParent(fxFullDirPlain) + s.replace('/', sep), getName(s)) for s in expected]
        assert expectedTuples == sorted(recurseDirs(fxFullDirPlain))

    def test_recurseDirsExcludeOneSubdir(self, fxFullDirPlain):
        expected = ['full', 's2']

        def filter(d):
            return getName(d) != 's1'
        assert expected == sorted(recurseDirs(fxFullDirPlain, filenamesOnly=True, 
                                                   fnFilterDirs=filter))

def recurseFileInfoWithResultsLikeRecurseFiles(root, filenamesOnly=False, **kwargs):
    results = list(recurseFileInfo(root, **kwargs))
    if filenamesOnly:
        return [item.short() for item in results]
    else:
        return [(item.path, item.short()) for item in results]
    
def listFileInfoWithResultsLikeListFiles(root, filenamesOnly=False, **kwargs):
    results = list(listFileInfo(root, **kwargs))
    if filenamesOnly:
        return [item.short() for item in results]
    else:
        return [(item.path, item.short()) for item in results]

@pytest.mark.skipif('not isPy3OrNewer')
class TestListingWithInfo:
    # same as TestListing, but no root
    def testFullResultsFiles(self, fxTreePlain):
        iter = recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain)
        got = sorted(iter)
        assert got == sorted(listFileInfoWithResultsLikeListFiles(fxTreePlain, recurse=True))
        assert all(os.path.isabs(item[0]) and exists(item[0]) for item in got)
        assert all(not os.path.isabs(item[1]) for item in got)
        assert sorted([item[1] for item in got]) == sorted(listFileInfoWithResultsLikeListFiles(fxTreePlain, recurse=True, filenamesOnly=True))
        assert [item[1] for item in got] == ['aa.txt', 'bb.txt', 'cc.txt', 'zz.txt', 'a.txt', 'b.txt', 'c0.txt', 'c1.txt', 'r1.txt', 'cc.txt', 'r2.txt', 'r3.txt']
        assert [item[0].replace(fxTreePlain, '').replace('\\', '/') for item in got] == ['/fb/a/bz/aa.txt', '/fb/a/bz/bb.txt', '/fb/a/bz/fb/cc.txt', '/fb/a/bz/zz.txt', '/fb/a/fb/a.txt', '/fb/a/fb/b.txt', '/fb/a/fb/c/c0.txt', '/fb/a/fb/c/c1.txt', '/fb/a/r1.txt', '/fb/fb/cc.txt', '/fb/r2.txt', '/r3.txt']

    def testFullResultsNoRecurseFiles(self, fxTree):
        got = sorted(listFileInfoWithResultsLikeListFiles(fxTree.pathDir))
        assert [item[1] for item in got] == ['a.txt', 'b.txt']
        assert [item[0].replace(fxTree.pathDir, '').replace('\\', '/') for item in got] == ['/a.txt', '/b.txt']

    def testFilenamesOnly(self, fxTree):
        got = sorted(listFileInfoWithResultsLikeListFiles(fxTree.pathDir, filenamesOnly=True))
        assert got == ['a.txt', 'b.txt']
        got = sorted(listFileInfoWithResultsLikeListFiles(fxTree.basedir + '/fb/a', filenamesOnly=True, includeDirs=True, includeFiles=False))
        assert got == ['bz', 'fb']
    
    def testFilenamesWithUnicode(self, fxFilesPlain):
        got = sorted(listFileInfoWithResultsLikeListFiles(fxFilesPlain, filenamesOnly=True))
        assert got == ['1ᄁ.txt', '2ᄁ.txt', 'a1.txt', 'bb2.txt', 'ccc3.txt', 'd4.txt', 'ee5.txt']
    
    def testRecurseFilesExtensions(self, fxTreePlain):
        writeAll(fxTreePlain + '/fb/a/fb/ttt.mp3', 'contents')
        writeAll(fxTreePlain + '/fb/a/ttt.mp3', 'contents')
        writeAll(fxTreePlain + '/fb/a/ttt.png', 'contents')
        writeAll(fxTreePlain + '/fb/ttt.MP3', 'contents')
        writeAll(fxTreePlain + '/fb/notamp3', 'contents')
        writeAll(fxTreePlain + '/fb/not.mp3.other', 'contents')
        
        # this "dotfile" should not count
        writeAll(fxTreePlain + '/fb/.mp3', 'contents')

        # incorrect usage
        with pytest.raises(AssertionError):
            got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, allowedExts='mp3'))

        # incorrect usage
        with pytest.raises(AssertionError):
            got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, allowedExts=['.mp3']))

        # finds no matches
        got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, filenamesOnly=True, allowedExts=['gif']))
        assert got == []

        # with list
        got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, filenamesOnly=True, allowedExts=['png', 'mp3']))
        assert got == ['ttt.MP3', 'ttt.mp3', 'ttt.mp3', 'ttt.png'] 

        # with set
        got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, filenamesOnly=True, allowedExts=set(['png'])))
        assert got == ['ttt.png'] 
    
    def testIncludes(self, fxTreePlain):
        got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, filenamesOnly=True, includeFiles=False, includeDirs=False))
        assert got == []

        got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, filenamesOnly=True, includeFiles=True, includeDirs=False))
        assert got == ['a.txt', 'aa.txt', 'b.txt', 'bb.txt', 'c0.txt', 'c1.txt', 'cc.txt', 'cc.txt', 'r1.txt', 'r2.txt', 'r3.txt', 'zz.txt']

        got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, filenamesOnly=True, includeFiles=False, includeDirs=True))
        # this one is different, doesn't have 'tree'
        assert got == ['a', 'bz', 'c', 'fb', 'fb', 'fb', 'fb', ]

        got = sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxTreePlain, filenamesOnly=True, includeFiles=True, includeDirs=True))
        # this one is different, doesn't have 'tree'
        assert got == ['a', 'a.txt', 'aa.txt', 'b.txt', 'bb.txt', 'bz', 'c', 'c0.txt', 'c1.txt', 'cc.txt', 'cc.txt', 'fb', 'fb', 'fb', 'fb', 'r1.txt', 'r2.txt', 'r3.txt', 'zz.txt']
        
@pytest.mark.skipif('not isPy3OrNewer')
class TestFilteringWithInfo:
    # same as TestFiltering, but no root
    def test_recurseFilesAcceptAllSubDirs(self, fxFullDirPlain):
        expected = ['a1.txt', 'file.txt', 'other.txt']
        assert expected == sorted(
            recurseFileInfoWithResultsLikeRecurseFiles(fxFullDirPlain, filenamesOnly=True, allowedExts=['txt'], fnFilterDirs=lambda d: True))

    def test_recurseFilesAcceptNoSubDirs(self, fxFullDirPlain):
        expected = ['a1.txt']
        assert expected == sorted(
            recurseFileInfoWithResultsLikeRecurseFiles(fxFullDirPlain, filenamesOnly=True, allowedExts=['txt'], fnFilterDirs=lambda d: False))

    def test_recurseFilesExcludeOneSubdir(self, fxFullDirPlain):
        expected = ['a1.txt', 'other.txt']

        def filter(d):
            return getName(d) != 's1'
        assert expected == sorted(recurseFileInfoWithResultsLikeRecurseFiles(fxFullDirPlain, filenamesOnly=True, allowedExts=['txt'], 
                                                    fnFilterDirs=filter))

    def test_recurseDirs(self, fxFullDirPlain):
        # doesn't include the root
        expected = ['/full/s1', '/full/s1/ss1', '/full/s1/ss2', '/full/s2']
        expectedTuples = [(getParent(fxFullDirPlain) + s.replace('/', sep), getName(s)) for s in expected]
        assert expectedTuples == sorted(recurseFileInfoWithResultsLikeRecurseFiles(
            fxFullDirPlain, includeFiles=False, includeDirs=True))

    def test_recurseDirsExcludeOneSubdir(self, fxFullDirPlain):
        # doesn't include the root
        expected = ['s2']

        def filter(d):
            return getName(d) != 's1'
        assert expected == sorted(recurseFileInfoWithResultsLikeRecurseFiles(
            fxFullDirPlain, filenamesOnly=True, 
            includeFiles=False, includeDirs=True,
            fnFilterDirs=filter))

@pytest.mark.skipif('not isPy3OrNewer')
class TestRecurseInfoStructFields:
    def testRecurseInfo(self, fxFilesPlain):
        got = sorted(recurseFileInfo(fxFilesPlain), key=lambda item: item.path)
        s = ''
        for item in got[0:3]:
            s += replaceMustExist(item.path, fxFilesPlain, '').replace('\\', '/') + ','
            s += str(item.isDir()) + ','
            s += str(item.isFile()) + ','
            s += str(item.short()) + ','
            s += str(item.size()) + ';'
        
        assert s == '/1ᄁ.txt,False,True,1ᄁ.txt,4;/2ᄁ.txt,False,True,2ᄁ.txt,4;/a1.txt,False,True,a1.txt,2;'
    
    def testRecurseInfoGetModtime(self, fxFilesPlain):
        now = time.time()
        got = sorted(recurseFileInfo(fxFilesPlain), key=lambda item: item.path)
        assert got[0].getLastModTime() > now - 1000
        assert got[0].getLastModTime(TimeUnits.Seconds) > now - 1000
        assert got[0].getLastModTime(TimeUnits.Milliseconds) > (now - 1000)*1000
        assert got[0].getLastModTime(TimeUnits.Nanoseconds) > (now - 1000)*1.0e6

class TestDirectorySize:
    def testBasic(self, fxFullDirPlain):
        got = getDirectorySizeRecurse(fxFullDirPlain)
        assert got == 79

