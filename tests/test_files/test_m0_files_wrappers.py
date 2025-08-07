

# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv2.1 License.

import pytest
import os
import enum
from os.path import join
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
from tests.test_core.common import fixture_dir
from collections import OrderedDict

class TestGetModTime:
    @pytest.mark.skipif('not isPy3OrNewer')
    def test_modtimeRendered(self, fixture_dir):
        files.writeAll(join(fixture_dir, 'a.txt'), 'contents')
        curtimeWritten = files.getLastModTime(join(fixture_dir, 'a.txt'), files.TimeUnits.Milliseconds)
        curtimeNow = getNowAsMillisTime()

        # we expect it to be at least within 1 day
        dayMilliseconds = 24 * 60 * 60 * 1000
        assert abs(curtimeWritten - curtimeNow) < dayMilliseconds

        # so we expect at least the date to match
        nCharsInDate = 10
        scurtimeWritten = renderMillisTime(curtimeWritten)
        scurtimeNow = renderMillisTime(curtimeNow)
        assert scurtimeWritten[0:nCharsInDate] == scurtimeNow[0:nCharsInDate]

    
