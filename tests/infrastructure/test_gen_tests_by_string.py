
from shinerainsoftsevencommon.infrastructure import gen_tests_by_string

import pytest
import tempfile
import os

class TestParseDeleteDirectory:
    def test_addition(self):
        n = 1 + 1
        assert n == 2

    def test_test2(self):
        with pytest.raises(ValueError):
            int('abc')
            
    @pytest.mark.skipif('not isPy3OrNewer')
    def test_test3(self):
        with pytest.raises(ValueError):
            int('abc')

a  = gen_tests_by_string.getEmptyTempDirectory('abc')
print(a)
