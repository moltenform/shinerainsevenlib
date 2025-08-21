# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
import sys
sys.path.append('../test_core')
sys.path.append('./tests/test_core')
from common import fxTree, fileInfoListToList, fxTreePlain
from collections import OrderedDict
import os
import shutil
from src.shinerainsevenlib.files import *


class TestListing:
    def testFullResults(self, fxTreePlain):
        iter = recurseFiles(fxTreePlain)
        got = sorted(list(iter))
        assert got ==  sorted(list(listFiles(fxTreePlain, recurse=True)))
        assert all(os.path.isabs(item[0]) and exists(item[0]) for item in got)
        assert all(not os.path.isabs(item[1]) for item in got)
        assert sorted([item[1] for item in got]) == sorted(list(listFiles(fxTreePlain, recurse=True, filenamesOnly=True)))
        assert [item[1] for item in got] == ['aa.txt', 'bb.txt', 'cc.txt', 'zz.txt', 'a.txt', 'b.txt', 'c0.txt', 'c1.txt', 'r1.txt', 'cc.txt', 'r2.txt', 'r3.txt']
        assert [item[0].replace(fxTreePlain, '').replace('\\', '/') for item in got] == ['/fb/a/bz/aa.txt', '/fb/a/bz/bb.txt', '/fb/a/bz/fb/cc.txt', '/fb/a/bz/zz.txt', '/fb/a/fb/a.txt', '/fb/a/fb/b.txt', '/fb/a/fb/c/c0.txt', '/fb/a/fb/c/c1.txt', '/fb/a/r1.txt', '/fb/fb/cc.txt', '/fb/r2.txt', '/r3.txt']
        
        iter = recurseDirs(fxTreePlain)
        got = sorted(list(iter))
        assert got ==  sorted(list(listDirs(fxTreePlain, recurse=True, )))
        assert all(os.path.isabs(item[0]) and exists(item[0]) for item in got)
        assert all(not os.path.isabs(item[1]) for item in got)
        assert sorted([item[1] for item in got]) == sorted(list(listDirs(fxTreePlain, recurse=True, filenamesOnly=True, )))
        assert [item[1] for item in got] ==  ['tree', 'fb', 'a', 'bz', 'fb', 'fb', 'c', 'fb']
        assert [item[0].replace(fxTreePlain, '').replace('\\', '/') for item in got] ==  ['', '/fb', '/fb/a', '/fb/a/bz', '/fb/a/bz/fb', '/fb/a/fb', '/fb/a/fb/c', '/fb/fb']

    def testNoRecurse(self, fxTreePlain):
        print(fxTreePlain)
        print(sorted(list(recurseDirs(fxTreePlain,  ))))
        print(sorted(list(listDirs(fxTreePlain, recurse=True, ))))
        print(sorted(list(listDirs(fxTreePlain, recurse=False, ))))
        iter = listDirs(fxTreePlain, filenamesOnly=False, recurse=False)
        got = fileInfoListToList(fxTreePlain, iter)
        assert got == ['/fb']
        
        #~ iter = listDirs(fxTreePlain, filenamesOnly=True, recurse=False)
        #~ got = sorted(list(iter))
        #~ assert got == 'xxx'

        #~ iter = listFiles(filenamesOnly=False, recurse=False)
        #~ got = fileInfoListToList(fxTreePlain, iter)
        #~ assert got == 'xxx'
        
        #~ iter = listFiles(filenamesOnly=True, recurse=False)
        #~ got = sorted(list(iter))
        #~ assert got == 'xxx'
    
    def testRecurse(self, fxTreePlain):
        iter = listDirs(fxTreePlain, filenamesOnly=False, recurse=True)
        #~ got = fileInfoListToList(fxTreePlain, iter)
        #~ assert got == 'xxx'
        
        #~ iter = listDirs(filenamesOnly=True, recurse=True)
        #~ got = sorted(list(iter))
        #~ assert got == 'xxx'

        #~ iter = listFiles(filenamesOnly=False, recurse=True)
        #~ got = fileInfoListToList(fxTreePlain, iter)
        #~ assert got == 'xxx'
        
        #~ iter = listFiles(filenamesOnly=True, recurse=True)
        #~ got = sorted(list(iter))
        #~ assert got == 'xxx'
    
    #~ def testAllowedExts(self, fxTreePlain):
    #~ def testFnFilter(self, fxTreePlain):


class TestRecurseinfo:
    def testRecurseInfo(self, fxTreePlain):
        pass

class TestDirectorySize:
    def testBasic(self):
        pass

