# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from tests.test_core.common import fixtureTree, fileInfoListToList
from collections import OrderedDict
import os
import sys
import shutil
from src.shinerainsevenlib.files import *


class TestListing:
    def testBasic(self, fixtureTree):
        iter = recurseFiles(fixtureTree)
        assert sorted(list(iter)) == 'xxx'
        
        iter = recurseDirs(fixtureTree)
        assert sorted(list(iter)) == 'xxx'

    def testNoRecurse(self, fixtureTree):
        iter = listDirs(filenamesOnly=False, recurse=False)
        got = fileInfoListToList(fixtureTree, iter)
        assert got == 'xxx'
        
        iter = listDirs(filenamesOnly=True, recurse=False)
        got = sorted(list(iter))
        assert got == 'xxx'

        iter = listFiles(filenamesOnly=False, recurse=False)
        got = fileInfoListToList(fixtureTree, iter)
        assert got == 'xxx'
        
        iter = listFiles(filenamesOnly=True, recurse=False)
        got = sorted(list(iter))
        assert got == 'xxx'
    
    def testRecurse(self, fixtureTree):
        iter = listDirs(filenamesOnly=False, recurse=True)
        got = fileInfoListToList(fixtureTree, iter)
        assert got == 'xxx'
        
        iter = listDirs(filenamesOnly=True, recurse=True)
        got = sorted(list(iter))
        assert got == 'xxx'

        iter = listFiles(filenamesOnly=False, recurse=True)
        got = fileInfoListToList(fixtureTree, iter)
        assert got == 'xxx'
        
        iter = listFiles(filenamesOnly=True, recurse=True)
        got = sorted(list(iter))
        assert got == 'xxx'
    
    def testAllowedExts(self, fixtureTree):
    def testFnFilter(self, fixtureTree):


class TestRecurseinfo:
    def testRecurseInfo(self, fixtureTree):
        pass

class TestDirectorySize:
    def testBasic(self):
        pass

