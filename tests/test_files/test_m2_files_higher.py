# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from tests.test_core.common import fixtureDir, fixtureFileTree
from collections import OrderedDict
import os
import sys
import shutil
from src.shinerainsevenlib.files import *


class TestM3ComputeHash:
    def test_computeHashMd5(self, fixtureDir):
        import hashlib
        hasher = hashlib.md5()
        writeAll(join(fixtureDir, 'a.txt'), 'contents')
        assert '98bf7d8c15784f0a3d63204441e1e2aa' == computeHash(join(fixtureDir, 'a.txt'), hasher)
    
    def test_computeHashSha256(self, fixtureDir):
        writeAll(join(fixtureDir, 'a.txt'), 'contents')
        assert 'd1b2a59fbea7e20077af9f91b27e95e865061b270be03ff539ab3b73587882e8' == computeHash(join(fixtureDir, 'a.txt'), 'sha256')
        
    def test_computeHashCrc(self, fixtureDir):
        writeAll(join(fixtureDir, 'a.txt'), 'contents')
        assert 'b4fa1177' == computeHash(join(fixtureDir, 'a.txt'), 'crc32')
        
    def test_computeHashFromBytes(self, fixtureDir):
        assert 'b4fa1177' == computeHashBytes(b'contents', 'crc32')
        
    def test_computeHashNotExist(self, fixtureDir):
        writeAll(join(fixtureDir, 'a.txt'), 'contents')
        with pytest.raises(ValueError):
            computeHash(join(fixtureDir, 'a.txt'), 'no_such_hash')
       
    def test_computeHashLargeFile(self, fixtureDir):
        fsize = defaultBufSize * 2 + 20
        with open(f'{fixtureDir}/a.dat', 'wb') as fout:
            for i in range(fsize):
                letter = ord('a') + (i%26)
                fout.write(chr(letter).encode('latin-1'))
        assert '4642eec0' == computeHash(f'{fixtureDir}/a.dat', 'crc32')
        assert 'ab73f0d9bfb568486d122f82480e4801' == computeHash(f'{fixtureDir}/a.dat', 'md5')

class TestM3FilesHigher:
    def testFindBinaryOnPath(self, fixtureDir):
        writeAll(f'{fixtureDir}/a.out', ' ')
        writeAll(f'{fixtureDir}/a.exe', ' ')
        writeAll(f'{fixtureDir}/b.bat', ' ')
        writeAll(f'{fixtureDir}/c', ' ')
        os.chdir(fixtureDir)
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
            assert findBinaryOnPath(f'{fixtureDir}/c').lower().endswith('c')

            # test with full paths
            assert not findBinaryOnPath(fixtureDir + ('/doesnotexist'))
            assert not findBinaryOnPath(fixtureDir + ('/doesnotexist.exe'))
            assert findBinaryOnPath(fixtureDir + ('/a.exe')).lower().endswith('a.exe')
            assert findBinaryOnPath(fixtureDir + ('/a')).lower().endswith('a.exe')
            assert findBinaryOnPath(fixtureDir + ('/c')).lower().endswith('c')
        else:
            assert findBinaryOnPath('sh').endswith('sh')
            assert not findBinaryOnPath('doesnotexist')
            assert not findBinaryOnPath('doesnotexist.exe')
            assert findBinaryOnPath('a.exe').endswith('a.exe')
            assert not findBinaryOnPath('a')
            assert findBinaryOnPath('b.bat').endswith('b.bat')
            assert not findBinaryOnPath('b')

            # if given a path, use it
            assert findBinaryOnPath('c').endswith('c')

            # test with full paths
            assert not findBinaryOnPath(fixtureDir + ('/doesnotexist'))
            assert not findBinaryOnPath(fixtureDir + ('/doesnotexist.exe'))
            assert findBinaryOnPath(fixtureDir + ('/a.exe')).endswith('a.exe')
            assert not findBinaryOnPath(fixtureDir + ('/a'))
            assert findBinaryOnPath(fixtureDir + ('/c')).endswith('c')

