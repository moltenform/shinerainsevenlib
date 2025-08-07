

import os
import pytest
from ..files import join
from ..common_ui import *
from .test_files import fixture_dir as fixture_dir_
fixture_dir = fixture_dir_

class TestCommonHigher:
    # getRandomString
    def test_getRandomString(self):
        s1 = getRandomString()
        assert all((c in '0123456789' for c in s1))
        s2 = getRandomString()
        assert all((c in '0123456789' for c in s2))
        assert s1 != s2

    # genUuid
    def test_genUuid(self):
        s1 = genUuid()
        assert 36 == len(s1)
        s2 = genUuid()
        assert 36 == len(s2)
        assert s1 != s2

    # genUuid, as base 64
    def test_genUuidBase64(self):
        s1 = genUuid(asBase64=True)
        assert 24 == len(s1)
        s2 = genUuid(asBase64=True)
        assert 24 == len(s2)
        assert s1 != s2

    # getClipboardText
    def test_getClipboardTextWithNoUnicode(self):
        # let's check that pyperclip is installed
        import pyperclip  # NOQA
        prev = getClipboardText()
        try:
            setClipboardText('normal ascii')
            assert 'normal ascii' == getClipboardText()
        finally:
            setClipboardText(prev)

    def test_getClipboardTextWithUnicode(self):
        # let's check that pyperclip is installed
        import pyperclip  # NOQA
        prev = getClipboardText()
        try:
            setClipboardText(u'\u1E31\u1E77\u1E53\u006E')
            assert u'\u1E31\u1E77\u1E53\u006E' == getClipboardText()
        finally:
            setClipboardText(prev)

    def test_downloadUrl(self):
        contents = downloadUrl('https://example.com', asText=True)
        contents = contents.replace(' ', '').replace('\r', '').replace('\n', '')
        hash = files.computeHashBytes(contents.encode('utf-8'), 'sha1')
        assert hash == 'e24287384b2d7cfddf8bc5d83443ee90b4f61c24'



class TestCommonUI:
    def test_checkIsDigit(self):
        # make sure isdigit behaves as expected
        assert not ''.isdigit()
        assert '0'.isdigit()
        assert '123'.isdigit()
        assert not '123 '.isdigit()
        assert not '123a'.isdigit()
        assert not 'a123'.isdigit()

    def test_findUnusedLetterMaintainsUsedLetterState(self):
        d = dict()
        assert 0 == findUnusedLetter(d, 'abc')
        assert 1 == findUnusedLetter(d, 'abc')
        assert 2 == findUnusedLetter(d, 'abc')
        assert None is findUnusedLetter(d, 'abc')
        assert None is findUnusedLetter(d, 'ABC')
        assert None is findUnusedLetter(d, 'a b c!@#')

    def test_softDeleteFileShouldMakeFileNotExist(self, fixture_dir):
        path = join(fixture_dir, 'testdelfile1.txt')
        files.writeAll(path, 'contents')
        assert os.path.exists(path)
        newlocation = softDeleteFile(path)
        assert not os.path.exists(path)
        assert os.path.exists(newlocation)

    def test_softDeleteFileShouldRenameFirstCharOfFile(self, fixture_dir):
        path = join(fixture_dir, 'zzzz', 'testdelfile2.txt')
        files.makeDirs(files.getParent(path))
        files.writeAll(path, 'contents')
        newlocation = softDeleteFile(path)
        assert os.path.exists(newlocation)
        assert files.getName(newlocation).startswith('z')
