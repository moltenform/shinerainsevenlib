
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from shinerainsoftsevenutil.standard import *

class TestTemporary:
    def testTemporary(self):
        dir=dir #intentionally cause lint err 
        a = 2+4
        assert a == 6

