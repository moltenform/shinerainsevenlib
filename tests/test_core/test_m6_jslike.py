
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsevenlib import *

class TestJslike:
    def testConcat(self):
        a = [1, 2]
        b = [3, 4]
        c = jslike.concat(a, b)
        assert c == [1, 2, 3, 4]
