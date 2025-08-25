
# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
import os
import random
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from common import fxDirPlain
from src.shinerainsevenlib.core import m4_core_ui

class TestRngHelpers:
    def testGetRandomStringBasic(self):
        s = getRandomString()
        assert isinstance(s, str)
        s2 = getRandomString()
        assert s != s2

        s = getRandomString(asHex=True)
        assert isinstance(s, str)
        assert len(s) == 8
        s2 = getRandomString(asHex=True)
        assert len(s2) == 8
        assert s != s2

    def testGetRandomStringAdvanced(self):
        with pytest.raises(AssertionError):
            getRandomString(asHex=True, rng=IndependentRNG())
        
        # should use system rng
        random.seed(12345)
        firstNumberWithSeed12345 = random.randrange(0, 1000)
        getRandomString()
        assert random.randrange(0, 1000) != self.getKnownRandomValue()

        # should use an independent rng
        myRng = IndependentRNG(12345)
        random.seed(12345)
        firstNumberWithSeed12345 = random.randrange(0, 1000)
        getRandomString(rng=myRng.rng)
        assert random.randrange(0, 1000) == self.getKnownRandomValue()
    
    def getKnownRandomValue(self):
        # get a known sequence, will let us detect
        # if the default Random rng has been touched
        # because if so, a different sequence will be there.
        seed = 12345
        rng = random.Random(seed)
        firstNumberWithSeed12345 = rng.randrange(0, 1000)
        secondNumberWithSeed12345 = rng.randrange(0, 1000)
        return secondNumberWithSeed12345

    def testGenUuid(self):
        uuid = genUuid()
        assert isinstance(uuid, str)
        assert len(uuid) == 36
        uuid = genUuid(asBase64=True)
        assert isinstance(uuid, str)
        assert len(uuid) == 24

class TestAssertWarn:
    def test_assertWarnHits(self, mocker):
        mocker.patch('src.shinerainsevenlib.core.m4_core_ui.warn')
        assertWarn(False, 'message')
        m4_core_ui.warn.assert_called_once_with('message')

    def test_assertWarnNoHits(self, mocker):
        mocker.patch('src.shinerainsevenlib.core.m4_core_ui.warn')
        assertWarn(True, 'message')
        m4_core_ui.warn.assert_not_called()
    
    def test_assertWarnEqHits(self, mocker):
        mocker.patch('src.shinerainsevenlib.core.m4_core_ui.warn')
        assertWarnEq(1, 2, 'message')
        m4_core_ui.warn.assert_called_once()

    def test_assertWarnEqNoHits(self, mocker):
        mocker.patch('src.shinerainsevenlib.core.m4_core_ui.warn')
        assertWarnEq(2, 2, 'message')
        m4_core_ui.warn.assert_not_called()
        
def requestsAvailable():
    "Checks if the requests module is available."
    try:
        import requests
        return True
    except ImportError:
        return False

@pytest.mark.skipif('not requestsAvailable()')
class TestDownloadUrl:
    def testBinary(self, mocker, fxDirPlain):
        import requests
        mocker.patch('requests.get', return_value=Bucket(text='abc', content=b'abc'))
        outPath = join(fxDirPlain, 'out.txt')
        got = downloadUrl('http://test.com', toFile=outPath)
        assert files.readAll(outPath) == 'abc'
        requests.get.assert_called_once_with('http://test.com', timeout=30)
        assert got == b'abc'
        assert isinstance(got, bytes)
    
    def testText(self, mocker, fxDirPlain):
        import requests
        mocker.patch('requests.get', return_value=Bucket(text='abc', content=b'abc'))
        got = downloadUrl('http://test.com', toFile=None, asText=True)
        requests.get.assert_called_once_with('http://test.com', timeout=30)
        assert got == 'abc'
        assert isinstance(got, str)


class TestStartThread:
    def test(self, mocker):
        import threading
        mocker.patch('threading.Thread.start')
        startThread(lambda: None)
        threading.Thread.start.assert_called_once()
    
    def testWithArgs(self, mocker):
        import threading
        mocker.patch('threading.Thread.start')
        startThread(lambda: None, (1, 2, 3))
        threading.Thread.start.assert_called_once()

@pytest.mark.skipif('not os.getenv("GITHUB_ACTION")')
class TestClipboard:
    def test_getClipboardTextWithNoUnicode(self):
        import pyperclip
        prev = getClipboardText()
        try:
            setClipboardText('normal ascii')
            assert 'normal ascii' == getClipboardText()
        finally:
            setClipboardText(prev)

    def test_getClipboardTextWithUnicode(self):
        import pyperclip
        prev = getClipboardText()
        try:
            setClipboardText(u'\u1E31\u1E77\u1E53\u006E')
            assert u'\u1E31\u1E77\u1E53\u006E' == getClipboardText()
        finally:
            setClipboardText(prev)
    
    # could not get pyperclip to work in gh actions
    # even after adding
    # sudo apt-get update && sudo apt-get install -y xclip(and xsel)
    

#~ class TestSoftDeleteFile:
    #~ def testSendToTrash(self, mocker):
        #~ import send2trash
        #~ mocker.patch('send2trash.send2trash')
        #~ softDeleteFile('my_file')
        #~ send2trash.send2trash.assert_called_once_with('my_file')



