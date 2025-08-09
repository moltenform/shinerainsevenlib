
# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
import os
import random
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from common import fixtureDir
from src.shinerainsevenlib.core import m4_core_ui

class TestGetRawInput:
    def test(self, mocker):
        import builtins
        mocker.patch('builtins.input')
        m4_core_ui.getRawInput('Please enter text:')
        builtins.input.assert_called_once_with('')

class TestAlert:
    def test(self):
        calls = []
        try:
            gRedirectAlertCalls['fnHook'] = lambda s: calls.append(s)
            alert('a', 'b', 'c')
            assert calls == ['a b c']
        finally:
            gRedirectAlertCalls['fnHook'] = None

class TestCoreUIHelpers:
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
        assert 0 == srss.findUnusedLetter(d, 'abc')
        assert 1 == srss.findUnusedLetter(d, 'abc')
        assert 2 == srss.findUnusedLetter(d, 'abc')
        assert None is srss.findUnusedLetter(d, 'abc')
        assert None is srss.findUnusedLetter(d, 'ABC')
        assert None is srss.findUnusedLetter(d, 'a b c!@#')