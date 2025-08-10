# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
import sys
sys.path.append('../test_core')
from common import fxTree, fileInfoListToList, fxTreePlain
from collections import OrderedDict
import os
import shutil
from src.shinerainsevenlib.files import *


class TestListing:
    def testBasic(self, fxTreePlain):
        iter = recurseFiles(fxTreePlain)
        #~ assert sorted(list(iter)) == 'xxx'
        
        #~ iter = recurseDirs(fxTreePlain)
        #~ assert sorted(list(iter)) == 'xxx'

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

