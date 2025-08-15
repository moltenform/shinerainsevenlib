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
        assert all(os.path.isabs(item[0]) and files.exists(item[0]) for item in got)
        assert all(not os.path.isabs(item[1]) for item in got)
        assert [item[1] for item in got] == ['aa.txt', 'bb.txt', 'cc.txt', 'zz.txt', 'a.txt', 'b.txt', 'c0.txt', 'c1.txt', 'r1.txt', 'cc.txt', 'r2.txt', 'r3.txt']
        assert [item[0].replace(fxTreePlain, '').replace('\\', '/') for item in got] == ['/foobar/a/baz/aa.txt', '/foobar/a/baz/bb.txt', '/foobar/a/baz/foobar/cc.txt', '/foobar/a/baz/zz.txt', '/foobar/a/foobar/a.txt', '/foobar/a/foobar/b.txt', '/foobar/a/foobar/c/c0.txt', '/foobar/a/foobar/c/c1.txt', '/foobar/a/r1.txt', '/foobar/foobar/cc.txt', '/foobar/r2.txt', '/r3.txt']
        
        iter = recurseDirs(fxTreePlain)
        got = sorted(list(iter))
        assert all(os.path.isabs(item[0]) and files.exists(item[0]) for item in got)
        assert all(not os.path.isabs(item[1]) for item in got)
        assert [item[1] for item in got] ==  ['tree', 'foobar', 'a', 'baz', 'foobar', 'foobar', 'c', 'foobar']
        assert [item[0].replace(fxTreePlain, '').replace('\\', '/') for item in got] ==  ['', '/foobar', '/foobar/a', '/foobar/a/baz', '/foobar/a/baz/foobar', '/foobar/a/foobar', '/foobar/a/foobar/c', '/foobar/foobar']

    def testNoRecurse(self, fxTreePlain):
        iter = listDirs(fxTreePlain, filenamesOnly=False, recurse=False)
        #~ got = fileInfoListToList(fxTreePlain, iter)
        #~ assert got == 'xxx'
        
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

