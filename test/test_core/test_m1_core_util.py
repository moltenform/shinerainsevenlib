
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from shinerainsoftsevenutil.standard import *
from shinerainsoftsevenutil.plugins.plugin_testhelpers import *


class TestTemporary:
    def testTemporary(self):
        a = 2+4
        a = 7*8
        makeFail()
        assert a == 6

