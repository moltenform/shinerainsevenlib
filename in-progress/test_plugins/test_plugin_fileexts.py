
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import pytest
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import assertException
from test.test_core.common import fxDirPlain

class TestTemporary:
    def testTemporary(self):
        dir=dir #intentionally cause lint err 
        a = 2+4
        assert a == 6

