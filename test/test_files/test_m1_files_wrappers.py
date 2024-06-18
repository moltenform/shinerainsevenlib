
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsoftsevenutil.standard import *
from src.shinerainsoftsevenutil.core import assertException
from test.test_core.common import fixture_dir

class TestTemporary:
    def testTemporary(self):
        dir=dir #intentionally cause lint err 
        a = 2+4
        assert a == 6

