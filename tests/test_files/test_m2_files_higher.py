# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from tests.test_core.common import fxDirPlain, fxTreePlain
from collections import OrderedDict
import os
import sys
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
    
    def test_computeHashSha256(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        assert 'd1b2a59fbea7e20077af9f91b27e95e865061b270be03ff539ab3b73587882e8' == computeHash(join(fxDirPlain, 'a.txt'), 'sha256')
        
    def test_computeHashCrc(self, fxDirPlain):
        writeAll(join(fxDirPlain, 'a.txt'), 'contents')
        assert 'b4fa1177' == computeHash(join(fxDirPlain, 'a.txt'), 'crc32')
        
    def test_computeHashFromBytes(self, fxDirPlain):
        assert 'b4fa1177' == computeHashBytes(b'contents', 'crc32')
        
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
        assert 'ab73f0d9bfb568486d122f82480e4801' == computeHash(f'{fxDirPlain}/a.dat', 'md5')

